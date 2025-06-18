import random
from datetime import timezone as dt_timezone
from dateutil import parser
from django.utils import timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from News_Processing.FetchNews import fetch_latest_headlines_clustered
from .models import ArticleClick
import numpy as np
import logging

logger = logging.getLogger(__name__)

# tuned thresholds
FAM_THRESHOLD = 0.5  # anything ≥0.5 is clearly familiar
NOV_THRESHOLD = 0.4  # anything ≤0.4 is clearly novel


def get_phase2_feed_custom(request, person, days_back=1, page_size=40):
    # 1) Load Phase 1 record & elapsed time
    click = ArticleClick.objects.get(person=person, phase=1)
    elapsed = person.phase1_elapsed or 0

    # 2) Decide fam/nov ratio
    if elapsed < 120:
        fam_ratio, nov_ratio = 0.30, 0.70
    elif elapsed < 240:
        fam_ratio, nov_ratio = 0.30, 0.70
    else:
        fam_ratio, nov_ratio = 0.30, 0.70

    logger.info(
        "Phase1 elapsed=%ds → using fam/nov split %.0f/%.0f%%",
        elapsed, fam_ratio * 100, nov_ratio * 100
    )

    # 3) Build TF-IDF profile on clicked title+body
    profile_texts = [
        (c["title"] or "") + " " + (c.get("body", "") or "")
        for c in click.click_data
    ]
    tfidf = TfidfVectorizer(
        stop_words='english',
        max_features=10000,
        ngram_range=(1, 2)
    )
    X = tfidf.fit_transform(profile_texts)
    centroid = np.asarray(X.mean(axis=0))

    def score(articles):
        # 3a) candidate vectors
        texts = [
            (a.get('title', '') or "") + " " + (a.get('body', '') or "")
            for a in articles
        ]
        Xc = tfidf.transform(texts)
        fam_s = cosine_similarity(Xc, centroid).ravel()

        # 3b) freshness bonus
        now = timezone.now().astimezone(dt_timezone.utc)
        fresh = []
        for a in articles:
            try:
                pub = parser.isoparse(a['published_date'])
                if not pub.tzinfo:
                    pub = pub.replace(tzinfo=dt_timezone.utc)
                else:
                    pub = pub.astimezone(dt_timezone.utc)
                age_h = max((now - pub).total_seconds() / 3600, 0.1)
                fresh.append(1.0 / (1.0 + age_h))
            except:
                fresh.append(0.0)

        # normalize
        mf = max(fresh) if fresh else 1.0
        fresh = [f / mf for f in fresh]

        # 3c) combine with new weights + rescale
        for art, f_s, r_s in zip(articles, fam_s, fresh):
            raw = 0.6 * f_s + 0.4 * r_s
            # stretch so raw=0.7 → 1.0
            art['score'] = min(1.0, raw / 0.7)

        return sorted(articles, key=lambda x: x['score'], reverse=True)

    # 4) fetch pool
    clusters = fetch_latest_headlines_clustered(
        topics=None, days_back=days_back, page=1,
        page_size=page_size, countries=['US', 'GB'], lang='en',
        clustering_enabled=True, clustering_threshold=0.7
    )
    pool = [art for cl in clusters for art in cl.get('articles', [])]

    # 5) score once
    scored = score(pool)

    # 6) compute splits
    total = len(scored)
    n_fam = max(1, int(round(fam_ratio * total)))
    n_nov = total - n_fam

    # 7) bucket by new thresholds
    fam_bucket = [a for a in scored if a['score'] >= FAM_THRESHOLD]
    nov_bucket = [a for a in scored if a['score'] <= NOV_THRESHOLD]
    fam_ids = {a['id'] for a in fam_bucket}
    nov_ids = {a['id'] for a in nov_bucket}
    mid_bucket = [a for a in scored if a['id'] not in fam_ids | nov_ids]

    # 8) select fam
    fam_sel = fam_bucket[:n_fam]
    if len(fam_sel) < n_fam:
        fam_sel += scored[:(n_fam - len(fam_sel))]

    # 9) select nov
    fam_sel_ids = {a['id'] for a in fam_sel}
    nov_cand = [a for a in nov_bucket if a['id'] not in fam_sel_ids]
    nov_sel = nov_cand[:n_nov]
    if len(nov_sel) < n_nov:
        nov_sel += [a for a in mid_bucket if a['id'] not in fam_sel_ids][: (n_nov - len(nov_sel))]

    # 10) tag & shuffle
    feed = []
    for a in fam_sel:
        a['explore'] = False
        feed.append(a)
    for a in nov_sel:
        a['explore'] = True
        feed.append(a)
    random.shuffle(feed)

    logger.debug("Phase 2 → fam_sel=%d, nov_sel=%d", len(fam_sel), len(nov_sel))
    return feed