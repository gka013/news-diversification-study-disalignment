#!/usr/bin/env python
# coding: utf-8

import os
import requests
import logging

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ----------------------------------------------------------
# NEWSCATCHER V3 API CONFIGURATION
# ----------------------------------------------------------
NEWS_API_KEY = os.getenv(
    'NEWSCATCHER_API_KEY',
    "m102RlosKZIC9AbVdg8MeyeTAGcpbQdS"  # placeholder; override via env
)
API_URL_HEADLINES = "https://v3-api.newscatcherapi.com/api/latest_headlines"

# A curated list of reputable, well-rounded English-language news outlets
REPUTABLE_SOURCES = [
    'reuters.com', 'apnews.com', 'bbc.com', 'nytimes.com', 'wsj.com',
    'washingtonpost.com', 'npr.org', 'pbs.org', 'theguardian.com',
    'thetimes.co.uk', 'ft.com', 'independent.co.uk', 'aljazeera.com',
    'theeconomist.com',
]


def fetch_latest_headlines_clustered(
        topics=None,
        sources=None,
        days_back=1,
        page=1,
        page_size=100,
        countries=None,
        lang="en",
        clustering_enabled=True,
        clustering_threshold=0.5,
        exclude_duplicates=True):
    """
    Fetch the most recent headlines, optionally clustered by the API.
    Returns the raw `clusters` list from NewsCatcher.
    """
    hours_back = days_back * 24
    params = {
        "lang": lang,
        "when": f"{hours_back}h",
        "page": page,
        "page_size": page_size,
        "clustering_enabled": "true" if clustering_enabled else "false",
        "clustering_threshold": clustering_threshold,
        "exclude_duplicates": "true" if exclude_duplicates else "false",
    }

    if sources:
        params["sources"] = ",".join(sources)
    elif countries:
        params["countries"] = ",".join(countries)

    if topics:
        try:
            params["theme"] = ",".join(str(t) for t in topics)
        except TypeError:
            pass

    headers = {"x-api-token": NEWS_API_KEY}

    try:
        resp = requests.get(API_URL_HEADLINES, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data.get("clusters", [])
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during API request: {e}")
        return []


def select_representative_articles(clusters):
    """
    From each returned cluster, pick exactly one “best” article
    (we use the longest summary as a simple heuristic).
    """
    rep = []
    for cluster in clusters:
        arts = cluster.get("articles", [])
        if not arts:
            continue
        # Heuristic: choose the article with the longest summary
        best = max(arts, key=lambda a: len(a.get("summary","")))
        best["cluster_size"] = cluster.get("cluster_size", 1)
        rep.append(best)
    return rep


def fetch_unique_headlines(*, topics=None, sources=None, days_back=1, page=1, page_size=30):
    """
    Combines the above two steps: fetch clusters, then pick one article per cluster.
    Returns a flat list of representative articles.
    """
    clusters = fetch_latest_headlines_clustered(
        topics=topics,
        sources=sources,
        days_back=days_back,
        page=page,
        page_size=page_size,
        lang="en",
        clustering_enabled=True,
        clustering_threshold=0.5,
        exclude_duplicates=True,
    )
    if not clusters:
        logging.warning("No clusters fetched, returning empty list.")
        return []
    return select_representative_articles(clusters)


if __name__ == "__main__":
    THEMES = [
        'Crime', 'Politics', 'Economics',
        'Business', 'Science', 'Tech',
        'Sports', 'Entertainment'
    ]

    if not NEWS_API_KEY or "YOUR_API_KEY" in NEWS_API_KEY:
        logging.error("NEWSCATCHER_API_KEY is not set or is a placeholder.")
        exit(1)

    # Fetch & de-duplicate
    final_articles = fetch_unique_headlines(
        topics=THEMES,
        sources=REPUTABLE_SOURCES,
        days_back=1,
        page=1,
        page_size=50
    )

    logging.info(f"Retrieved {len(final_articles)} unique articles.")

    # Pretty-print
    for art in final_articles:
        title = art.get("title","")
        src   = art.get("clean_url","")
        size  = art.get("cluster_size",1)
        cluster_note = f" (from cluster of {size})" if size> 1 else ""
        summary = art.get("summary","No summary.")
        print(f"\n• [{src}] {title}{cluster_note}\n  → {summary}")
