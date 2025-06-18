from django.forms import formset_factory
from django.db.models import Count
import requests
import logging
import pandas as pd
from random import *
from django.contrib import messages
from django.conf import settings
import random
from sys import prefix
from django import forms
from django.forms import formset_factory
from django.db.models import Count
from datetime import datetime as dt, timedelta
from django.utils import timezone as django_timezone
from requests.exceptions import HTTPError
from .recommender import get_phase2_feed_custom
import logging
import pandas as pd
from random import *
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
import random
from sys import prefix
from django import forms
from django.db import reset_queries
from django.forms.models import ModelForm
from django.http import request
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from pandas.core.indexes import category
from django.shortcuts import render
import re
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from django.shortcuts import redirect, render

from django.shortcuts import get_object_or_404
import json
from News_Processing.FetchNews import fetch_latest_headlines_clustered, select_representative_articles

from django.shortcuts import render

from .forms import *
from .models import *
import string
import random
import re

# configure logger at module level
logger = logging.getLogger(__name__)


def get_phase2_feed(person, days_back=1, page_size=30):
    """
    1) Load Phase 1 clicks → cluster_ids
    2) Fetch *all* recent clusters (no theme filter)
    3) 80/20 split by cluster membership
    """
    try:
        click_record = ArticleClick.objects.get(person=person, phase=1)
    except ArticleClick.DoesNotExist:
        return []

    liked_clusters = set(str(c) for c in (click_record.cluster_ids or []))

    clusters = fetch_latest_headlines_clustered(
        topics=None,
        days_back=days_back,
        page=1,
        page_size=page_size,
        countries=['US', 'GB'],
        lang='en',
        clustering_enabled=True,
        clustering_threshold=0.5,
    )

    all_articles = []
    new_map = {}
    for cl in clusters:
        cid = str(cl.get('cluster_id'))
        for art in cl.get('articles', []):
            aid = art.get('id')
            if not aid:
                continue
            art['body'] = art.get('content') or art.get('summary') or art.get('description', '')
            all_articles.append(art)
            new_map[str(aid)] = cid

    familiar = [a for a in all_articles if new_map.get(str(a['id'])) in liked_clusters]
    novel = [a for a in all_articles if new_map.get(str(a['id'])) not in liked_clusters]

    N = len(all_articles)
    n_fam = max(1, int(0.8 * N))
    n_nov = N - n_fam

    fam_sel = random.sample(familiar, min(n_fam, len(familiar)))
    nov_sel = random.sample(novel, min(n_nov, len(novel)))
    feed = fam_sel + nov_sel
    random.shuffle(feed)

    for art in feed:
        art['explore'] = new_map.get(str(art['id'])) not in liked_clusters

    return feed


ADMIN_PROLIFIC_ID = "gloria_test"


def home(request):
    """
    Handles user entry, routing, and delays. Includes an admin bypass for
    time delays and a more complete reset feature for testing.
    """
    # Define constants
    NEW_USER_DELAY_MS = 15_000
    RETURN_THRESHOLD = timedelta(days=2)

    # --- 1. Unify PID retrieval from GET or POST ---
    pid = None
    if request.method == 'GET':
        pid = request.GET.get('PROLIFIC_PID')
    elif request.method == 'POST':
        pid = request.POST.get('prolific_pid', '').strip()
        if not pid:
            return render(request, 'Labels_Nudges/homes.html', {
                'error': "Please enter your Prolific ID.", 'prefill_pid': ''
            })

    # --- NEW: Admin Reset Feature ---
    # To use, visit: /?PROLIFIC_PID=YOUR_TEST_ID&reset=true
    if pid == ADMIN_PROLIFIC_ID and request.GET.get('reset') == 'true':
        try:
            participant = Personal_info.objects.get(prolific_username=pid)
            # Delete all related data for this user
            ArticleClick.objects.filter(person=participant).delete()
            Topic_preference.objects.filter(person=participant).delete()

            # --- THIS IS THE CRITICAL FIX ---
            # Also delete any previous GHS/FK survey responses for the user.
            Ghs_fk2.objects.filter(person=participant).delete()

            # Reset all flags and timestamps on the participant object
            participant.phase_one_complete = False
            participant.phase_two_complete = False
            participant.redemption_code_phase1 = None
            participant.redemption_code_phase2 = None
            participant.last_home = None
            participant.save()

            # Clear the entire session to ensure a fresh start
            request.session.flush()

            logger.info(f"Admin user '{pid}' has been completely reset.")
            # Redirect to the home page to start the flow cleanly
            return redirect(reverse('Labels_Nudges:home'))
        except Personal_info.DoesNotExist:
            # If admin user doesn't exist yet, just proceed normally
            pass
    # --- End of Admin Reset ---

    # --- 2. If no PID is found, show the manual entry form ---
    if not pid:
        return render(request, 'Labels_Nudges/homes.html', {
            'prefill_pid': request.session.get('prolific_username', '')
        })

    # --- 3. A PID was provided, process it ---
    request.session['prolific_username'] = pid
    context = {'prefill_pid': pid}

    try:
        # --- Returning User Logic ---
        participant = Personal_info.objects.get(prolific_username=pid)
        request.session['person_id'] = participant.id
        now = timezone.now()

        # Check if the user has completed Phase 1
        if not participant.phase_one_complete:
            # User is still in Phase 1. Let them proceed immediately.
            context['next_url'] = reverse('Labels_Nudges:topic_preference')
            context['delay_ms'] = 0
        else:
            # User HAS completed Phase 1 and is returning for Phase 2.
            # Route to topic_preference to start the Phase 2 flow.
            context['next_url'] = reverse('Labels_Nudges:topic_preference')

            # --- Admin Bypass Logic for time delay ---
            if pid == ADMIN_PROLIFIC_ID:
                logger.info(f"Admin user '{pid}' detected. Bypassing time delay.")
                context['delay_ms'] = 0
            else:
                # Regular user logic: Enforce the two-day delay.
                if participant.last_home is None:
                    participant.last_home = now
                    participant.save(update_fields=['last_home'])
                    remaining_time = RETURN_THRESHOLD
                else:
                    elapsed = now - participant.last_home
                    if elapsed < RETURN_THRESHOLD:
                        remaining_time = RETURN_THRESHOLD - elapsed
                    else:
                        remaining_time = timedelta(0)

                delay_seconds = int(remaining_time.total_seconds())
                context['delay_ms'] = delay_seconds * 1000

                if delay_seconds > 60:
                    days, rem = divmod(delay_seconds, 86400)
                    hours, rem = divmod(rem, 3600)
                    minutes, _ = divmod(rem, 60)
                    parts = []
                    if days > 0: parts.append(f"{days} day{'s' if days > 1 else ''}")
                    if hours > 0: parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
                    if minutes > 0 and not days: parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
                    context['wait_message'] = f"Please return in about {' and '.join(parts)}."

    except Personal_info.DoesNotExist:
        # --- New User Logic ---
        context['delay_ms'] = NEW_USER_DELAY_MS
        context['next_url'] = reverse('Labels_Nudges:personal_info')

    # --- 4. Final render ---
    return render(request, 'Labels_Nudges/homes.html', context)


def personal_info(request):
    # 1) Grab the Prolific ID from the session
    pid = request.session.get('prolific_username')
    if not pid:
        return redirect('Labels_Nudges:home')

    # 2) Try to load an existing record for that PID, or None
    try:
        participant = Personal_info.objects.get(prolific_username=pid)
    except Personal_info.DoesNotExist:
        participant = None

    if request.method == 'POST':
        form = Personal_infoForm(request.POST, instance=participant)

        # **DEBUG**: print any form errors so you can see why it refuses to validate
        if not form.is_valid():
            print("personal_info form errors:", form.errors)

        if form.is_valid():
            pi = form.save(commit=False)

            # 3) Assign the PID (never asked in the template)
            pi.prolific_username = pid

            # 4) Generate and save a session_id
            now = dt.now().strftime('%H%M%S')
            rnd = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
            pi.session_id = f'dars{now}_{pid}_{rnd}'

            pi.save()

            # 5) Store for downstream views
            request.session['person_id'] = pi.id
            request.session['participant_session_id'] = pi.session_id
            request.session['clicked_articles'] = []

            return redirect('Labels_Nudges:topic_preference')

    else:
        form = Personal_infoForm(instance=participant)

    return render(request,
                  'Labels_Nudges/personal_info.html',
                  {'form': form})


def topic_preference(request):
    pid = request.session.get('person_id')
    if not pid:
        return redirect('Labels_Nudges:home')
    person = get_object_or_404(Personal_info, id=pid)

    # If they've finished Phase 2, they shouldn't be here. Redirect to the end.
    if person.phase_two_complete:
        return redirect('Labels_Nudges:thank_u')  # Or wherever your final page is

    # Load or create the one preference record for this person
    tp, created = Topic_preference.objects.get_or_create(person=person)

    if request.method == 'POST':
        form = Topic_preferenceForm(request.POST, instance=tp)
        if form.is_valid():
            # --- THIS IS THE NEW, ROBUST LOGIC ---

            # 1. Get the latest preferences from the form
            latest_prefs = {
                k: v for k, v in form.cleaned_data.items()
                if k not in ('csrfmiddlewaretoken', 'history', 'session_id')
            }

            # 2. Build the new entry with a timestamp
            new_entry = {
                'timestamp': timezone.now().isoformat(),
                'preferences': latest_prefs
            }

            # 3. Load the history, ensuring it's a dictionary
            history = tp.history or {}
            if not isinstance(history, dict):
                history = {}  # Overwrite if it's an old list format

            # 4. Determine which phase this submission belongs to and save it.
            #    This automatically overwrites any previous submission for the SAME phase.
            if not person.phase_one_complete:
                history['phase_1'] = new_entry
            else:
                history['phase_2'] = new_entry

            # 5. Save the updated fields and the new history structure
            tp = form.save(commit=False)
            tp.history = history

            # Preserve your session token logic
            session_token = request.session.get('participant_session_id')
            if not session_token:
                rnd = ''.join(random.choices(string.ascii_lowercase, k=5))
                ts = timezone.now().strftime('%H%M%S')
                session_token = f'dars{ts}_{pid}_{rnd}'
                request.session['participant_session_id'] = session_token
            tp.session_id = session_token

            tp.save()

            # 6. Redirect to the correct evaluation view
            if not person.phase_one_complete:
                return redirect('Labels_Nudges:choice_evaluation')
            else:
                return redirect('Labels_Nudges:choice_evaluation2')
        else:
            messages.error(request, "Something went wrong—please check your entries.")
    else:
        form = Topic_preferenceForm(instance=tp)

    return render(request, 'Labels_Nudges/topic_preference.html', {
        'form': form
    })

def ghs_fk(request):
    try:
        print("Entering ghs_fk function")

        # Fetch the user's topic preferences
        user_selected = Topic_preference.objects.filter(person_id=request.session.get('person_id')).first()
        print(f"User selected: {user_selected}")

        if not user_selected:
            print("No user selected. Redirecting to topic preference.")
            return redirect('Labels_Nudges:topic_preference')

        # Map user ratings to topics
        user_ratings = {
            'topic_environment': user_selected.topic_environment,
            'topic_weather': user_selected.topic_weather,
            'topic_green_living': user_selected.topic_green_living
        }
        print(f"User ratings: {user_ratings}")

        # Find the highest-rated topic
        max_rating = max(user_ratings.values())
        top_topics = [topic for topic, rating in user_ratings.items() if rating == max_rating]
        print(f"Max rating: {max_rating}")
        print(f"Top topics: {top_topics}")

        # Randomly select one topic in case of a tie
        chosen_topic = random.choice(top_topics)
        print(f"Chosen topic: {chosen_topic}")

        # Hardcoded article ranges
        topic_to_article_range = {
            'topic_environment': range(1, 7),
            'topic_weather': range(7, 13),
            'topic_green_living': range(13, 19)
        }

        Sub_100Articals = []  # Initialize local variable
        if chosen_topic in topic_to_article_range:
            article_range = list(topic_to_article_range[chosen_topic])
            Sub_100Articals = random.sample(article_range, min(len(article_range), 6))
            print(f"Article range: {article_range}")
            print(f"Selected articles: {Sub_100Articals}")

            # Save selected articles to session
            request.session['selected_article_ids'] = Sub_100Articals
            print(f"Session articles updated: {request.session['selected_article_ids']}")
        else:
            print(f"Chosen topic {chosen_topic} not found in hardcoded ranges")

        if request.method == 'POST':
            ghs_fk_form = Ghs_fkForm(request.POST)
            if ghs_fk_form.is_valid():
                answer = ghs_fk_form.save(commit=False)
                rd_str = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
                time_now = dt.now().strftime('%H%M%S')
                gene_session = f'dars{time_now}_{answer.id}_{rd_str}'
                ghs_fk_form.instance.session_id = gene_session
                ghs_fk_form.instance.person_id = request.session['person_id']
                answer.save()

                return redirect('Labels_Nudges:choice_evaluation')
        else:
            ghs_fk_form = Ghs_fkForm()

    except Exception as e:
        print(f"An exception occurred: {e}")
        return redirect('Labels_Nudges:home')

    return render(request, 'Labels_Nudges/healthy_knowledge.html', context={'form': ghs_fk_form})


# This function is for Jeng's testing code
def list_news(request):
    # Get all news records
    news_records = NewsRec.objects.all()

    # Build a list of dictionaries, one dictionary per news item
    newsList = []
    for rec in news_records:
        image_url = rec.image.url if rec.image else ''  # If using ImageField
        # Add a dictionary representing this news item

        newsList.append({
            'id': rec.id,
            'image_url': image_url,
            'title': rec.title,
            'text': rec.text,
        })

    return render(request, 'Labels_Nudges/list_news.html', {'newsList': newsList})


def list_img(request):
    # this used to Random: num_instances = ClimateNews.objects.all().count()
    # context = {'num_instances':num_instances}

    # This used to send the image and title information to template:
    # image = ClimateNews.objects.all()
    # context = {'imageKey':image}

    # return render(request, 'Labels_Nudges/list_news.html',context = context) # notice here we are adding

    # This used to send the image and title information to template:
    newsAttributes = NewsRec.objects.all()
    newsList = [newsAttributes.id, newsAttributes.image_url]
    # context = {'image':image[1],'title':image[1][1]}
    return render(request, 'Labels_Nudges/list_img.html',
                  context={'newsList': newsList})  # notice here we are adding


# size10 = len(ClimateNews.objects.all())
Sub_100Articals = []

Sub_100ArticalsDict = {}
# Sub_100Articals= sample(range(1, 101), 10)
# Sub_100Articals2=Sub_100Articals
print("Globel Sub_100Articals be called:")
print(Sub_100Articals)


def choice_evaluation(request):
    # — ensure session_key for logging —
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    logger.info(">>> choice_evaluation called; method=%s; session_key=%s",
                request.method, session_key)

    # — 1) Must be logged in —
    person_id = request.session.get('person_id')
    if not person_id:
        logger.warning("No person_id in session; redirecting to home")
        return redirect('Labels_Nudges:home')

    person = get_object_or_404(Personal_info, id=person_id)

    # --- POST REQUEST LOGIC ---
    if request.method == 'POST':
        # parse timing
        raw_start = request.POST.get('phase1_start')
        raw_elapsed = request.POST.get('phase1_elapsed')
        try:
            elapsed = int(raw_elapsed)
        except (TypeError, ValueError):
            elapsed = None

        phase1_start = None
        if raw_start:
            try:
                ms = int(raw_start)
                phase1_start = dt.fromtimestamp(ms / 1000.0, tz=django_timezone.utc)
            except:
                phase1_start = None

        # load clicks payload
        saved_json = request.POST.get('saved_articles', '[]')
        try:
            saved_ids = json.loads(saved_json)
        except json.JSONDecodeError:
            messages.error(request, "Invalid list of saved articles.")
            return redirect('Labels_Nudges:choice_evaluation')

        # This is now the clean, de-duplicated list from the session
        articles = request.session.get('selected_articles', [])

        # build one list of click‐objects
        click_data = []
        for sid in saved_ids:
            art = next((a for a in articles if str(a.get('id')) == str(sid)), None)
            if not art:
                continue

            # extract source & topics exactly as before
            source = (art.get('source_name') or art.get('clean_url') or art.get('rights') or "")
            topics = []
            if art.get('topic'): topics.append(art['topic'])
            if art.get('nlp', {}).get('theme'):
                topics.append(art['nlp']['theme'])

            click_data.append({
                "id": str(sid),
                "title": art.get("title", ""),
                # *** CHANGED: Get cluster_id directly from the article object
                "cluster": art.get("cluster_id", ""),
                "source": source,
                "topics": topics,
                "clicked_at": django_timezone.now().isoformat()
            })

        total_clicked = len(click_data)

        # persist into your single JSONField
        if click_data:
            click_obj, created = ArticleClick.objects.update_or_create(
                person=person,
                phase=1,
                defaults={
                    "session_id": session_key,
                    "click_data": click_data,
                    "clicked_at": django_timezone.now(),
                    "phase1_start": phase1_start,
                    "phase1_elapsed": elapsed,
                    "total_clicked": total_clicked,
                }
            )
            verb = "Created" if created else "Updated"
            logger.info(
                "%s Phase 1 ArticleClick(id=%s) for person=%s: %d clicks",
                verb, click_obj.id, person.id, len(click_data)
            )

        # save timing on person
        person.phase_one_complete = True
        person.redemption_code_phase1 = generate_redemption_code()
        person.save()

        return redirect('Labels_Nudges:ghs_fk2')

    # --- GET REQUEST LOGIC ---
    pref = get_object_or_404(Topic_preference, person_id=person_id)
    api_theme_map = {
        'politikk': ['Politics'],
        'okonomi_og_naeringsliv': ['Economics', 'Business', 'Finance'],
        'kriminalitet_og_rettssaker': ['Crime', 'Financial Crime'],
        'utenriks_og_globale_konflikter': ['Politics'],
        'samfunn_og_arbeidsliv': ['General'],
        'klima_og_miljo': ['Science'],
        'helse_og_forskning': ['Health', 'Science'],
        'teknologi_og_vitenskap': ['Tech', 'Science'],
        'sport': ['Sports'],
        'underholdning_og_kjendiser': ['Entertainment'],
        'livsstil_og_helse': ['Lifestyle', 'Health'],
        'mat_og_drikke': ['Lifestyle'],
    }
    liked = [f for f in api_theme_map if getattr(pref, f) == 1]
    if not liked:
        ratings = {f: getattr(pref, f) for f in api_theme_map if getattr(pref, f) is not None}
        liked = [max(ratings, key=ratings.get)] if ratings else ['politikk']
    selected_themes = list(set(t for f in liked for t in api_theme_map[f]))

    try:
        clusters = fetch_latest_headlines_clustered(
            topics=selected_themes,
            days_back=1, page=1, page_size=30,
            countries=['US', 'GB'], lang='en',
            clustering_enabled=True, clustering_threshold=0.5
        )
    except Exception:
        messages.error(request, "Error fetching articles. Please try again later.")
        logger.exception("Error in fetch_latest_headlines_clustered")
        return redirect('Labels_Nudges:topic_preference')

    # *** CHANGED: Replaced the entire "flatten clusters" loop with this one line ***
    articles = select_representative_articles(clusters)

    # Add body attribute for template compatibility
    for art in articles:
        art['body'] = art.get('content') or art.get('summary') or art.get('description', '')

    if not articles:
        messages.error(request, "No articles found – try adjusting your preferences.")
        logger.warning("No articles after clustering for themes %s", selected_themes)
        return redirect('Labels_Nudges:topic_preference')

    # save into session & render
    request.session['selected_articles'] = articles
    # *** CHANGED: The 'article_clusters' map is no longer needed in the session ***
    logger.info("Saved %d de-duplicated articles into session", len(articles))

    return render(request, 'Labels_Nudges/choice_evaluation.html', {
        'articles': articles
    })


def get_phase2_feed_by_score(person, days_back=1, page_size=30):
    click_record = get_object_or_404(ArticleClick, person=person, phase=1)
    clicked_topics = click_record.topics or []

    # 1) Fetch familiar & novel clusters
    fam_clusters = fetch_latest_headlines_clustered(
        topics=clicked_topics, days_back=days_back, page=1,
        page_size=page_size, countries=['US', 'GB'], lang='en',
        clustering_enabled=True, clustering_threshold=0.5,
    )
    nov_clusters = fetch_latest_headlines_clustered(
        topics=None, days_back=days_back, page=1,
        page_size=page_size, countries=['US', 'GB'], lang='en',
        clustering_enabled=True, clustering_threshold=0.5,
    )

    # 2) Flatten
    familiar = [art for cl in fam_clusters for art in cl.get('articles', [])]
    novel = [art for cl in nov_clusters for art in cl.get('articles', [])]

    # 3) Sort by score
    familiar.sort(key=lambda a: a.get('score', 0), reverse=True)
    novel.sort(key=lambda a: a.get('score', 0), reverse=True)

    # 4) Log top‐5 of each pool for debugging
    logger.debug("Top 5 familiar (id,score): %r",
                 [(a['id'], a.get('score')) for a in familiar[:5]])
    logger.debug("Top 5 novel    (id,score): %r",
                 [(a['id'], a.get('score')) for a in novel[:5]])

    # 5) Compute split sizes
    N = len(familiar) + len(novel)
    n_fam = max(1, int(0.8 * N))
    n_nov = N - n_fam

    # 6) Slice top‐scoring
    fam_sel = familiar[:min(n_fam, len(familiar))]
    nov_sel = novel[:min(n_nov, len(novel))]

    # 7) Log what we actually selected
    logger.debug("Selected familiar (id,score): %r",
                 [(a['id'], a.get('score')) for a in fam_sel])
    logger.debug("Selected novel     (id,score): %r",
                 [(a['id'], a.get('score')) for a in nov_sel])

    # 8) Tag & combine
    feed = []
    for art in fam_sel:
        art['explore'] = False
        feed.append(art)
    for art in nov_sel:
        art['explore'] = True
        feed.append(art)

    # 9) Shuffle and final log
    random.shuffle(feed)
    logger.debug("Final feed order (id,score,explore): %r",
                 [(a['id'], a.get('score'), a['explore']) for a in feed])

    return feed


def choice_evaluation2(request):
    # 1) Participant and Route Guards (These run on EVERY request, which is correct)
    pid = request.session.get('person_id')
    if not pid:
        return redirect('Labels_Nudges:home')
    person = get_object_or_404(Personal_info, id=pid)

    if not Topic_preference.objects.filter(person_id=pid).exists():
        return redirect('Labels_Nudges:topic_preference')
    if not person.phase_one_complete:
        return redirect('Labels_Nudges:choice_evaluation')
    if not person.redemption_code_phase1:
        return redirect('Labels_Nudges:redemption', phase=1)
    if person.phase_two_complete:
        return redirect('Labels_Nudges:thank_u')

    # ----------------------------------------------------------------------------------
    # 2) POST Request Logic: Handle the user's form submission
    # This block only runs when the user clicks "Next" and submits the form.
    # ----------------------------------------------------------------------------------
    if request.method == 'POST':
        # A) CRITICAL: Retrieve the feed that was *originally shown* to the user from the session.
        # Do NOT generate a new feed. This is the key to fixing the mismatch.
        phase2_articles = request.session.get('phase2_articles', [])

        # B) Parse timing data from the submitted form
        raw_start = request.POST.get('phase2_start')
        raw_elapsed = request.POST.get('phase2_elapsed')
        elapsed2 = int(raw_elapsed) if raw_elapsed and raw_elapsed.isdigit() else None
        phase2_start = dt.fromtimestamp(int(raw_start) / 1000.0,
                                        tz=django_timezone.utc) if raw_start and raw_start.isdigit() else None

        # C) Parse the bookmarked article IDs from the submitted form
        raw_saved_articles = request.POST.get('saved_articles', '[]')
        try:
            saved_ids = json.loads(raw_saved_articles)
        except json.JSONDecodeError:
            saved_ids = []
        request.session['saved_articles'] = saved_ids  # Store the final choices

        # D) Build click_data by comparing saved IDs against the original session feed
        click_data = []
        for sid in saved_ids:
            # This lookup will now succeed because phase2_articles is the correct list
            art = next((a for a in phase2_articles if str(a['id']) == str(sid)), None)
            if not art:
                logger.warning("Phase2 clicked id %s not in session feed for person %s. Skipping.", sid, pid)
                continue

            topics = []
            if art.get("topic"):
                topics.append(art["topic"])
            theme = art.get("nlp", {}).get("theme")
            if theme:
                topics.append(theme)

            click_data.append({
                "id": str(sid),
                "title": art.get("title", ""),
                "similarity": art.get("score", 0.0),
                "explore": art.get("explore", False),
                "source": art.get("source_name") or art.get("clean_url") or "",
                "topics": topics,
                "clicked_at": django_timezone.now().isoformat(),
            })

        total_clicked = len(click_data)
        familiar_count = sum(1 for c in click_data if not c.get("explore"))
        percent_familiar = round(familiar_count / total_clicked * 100, 1) if total_clicked else 0.0

        logger.debug("Phase 2 click_data for person %s (%d clicks): %s", pid, total_clicked, click_data)

        # E) Persist the final click data to the database
        click_obj, created = ArticleClick.objects.update_or_create(
            person=person,
            phase=2,
            defaults={
                "session_id": request.session.session_key or '',
                "click_data": click_data,
                "clicked_at": django_timezone.now(),
                "phase2_start": phase2_start,
                "phase2_elapsed": elapsed2,
                "percent_familiar": percent_familiar,
                "total_clicked": total_clicked,
            }
        )
        verb = "Created" if created else "Updated"
        logger.info("%s ArticleClick(id=%s) for Phase 2 (Person: %s): %d items", verb, click_obj.id, pid, total_clicked)

        # F) Handle the final evaluation form and complete Phase 2
        form = ChoiceEvaluationForm2(request.POST)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.person = person
            ev.session_id = request.session.session_key or ''
            ev.save()

            person.phase_two_complete = True
            person.redemption_code_phase2 = generate_redemption_code()  # Ensure this function is imported/defined
            person.save()
            return redirect('Labels_Nudges:ghs_fk2')
        else:
            # If the final form has errors, re-render the page with the errors shown.
            # It's important to pass the original articles and form back to the template.
            messages.error(request, "There was an error in the form below. Please correct it.")
            return render(request, "Labels_Nudges/choice_evaluation2.html", {
                'articles': phase2_articles,  # Use the list from the session
                'form': form,  # The form with error messages
                'saved_articles_json': json.dumps(saved_ids),
            })

    # ----------------------------------------------------------------------------------
    # 3) GET Request Logic: Prepare and display the page for the first time
    # This block only runs when the user first loads the page.
    # ----------------------------------------------------------------------------------
    else:
        try:
            # A) Generate the custom Phase 2 feed ONCE.
            feed = get_phase2_feed_custom(request, person, days_back=1, page_size=30)

            # B) Remove duplicates
            seen = set()
            unique = []
            for art in feed:
                if art['id'] not in seen:
                    seen.add(art['id'])
                    unique.append(art)
            feed = unique

            # C) Store this definitive feed in the session. It's now "frozen" for this visit.
            request.session['phase2_articles'] = feed
            request.session['saved_articles'] = []  # Reset bookmarks on a fresh page load

            logger.debug(
                "Generated Phase 2 feed for person %s (%d items): %s",
                pid, len(feed), [{'id': a['id'], 'score': a.get('score'), 'explore': a.get('explore')} for a in feed]
            )

        except Exception as e:
            logger.exception("Fatal error building Phase 2 feed for person %s: %s", pid, e)
            messages.error(request, "Sorry, we couldn’t load your personalized feed right now.")
            return redirect('Labels_Nudges:topic_preference')

        # D) Prepare an empty form for the user
        form = ChoiceEvaluationForm2()

        # E) Render the page template with the new feed and empty form
        return render(request, "Labels_Nudges/choice_evaluation2.html", {
            'articles': feed,
            'form': form,
            'saved_articles_json': json.dumps([]),
        })


def generate_redemption_code(length=8):
    # You could adapt this to your needs.
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


MAX_PHASES = 2


def ghs_fk2(request):
    # 0) Must be logged in
    pid = request.session.get('person_id')
    if not pid:
        return redirect('Labels_Nudges:home')
    person = get_object_or_404(Personal_info, id=pid)

    # 1) Fetch-or-create our one Ghs_fk2 row
    # --- MODIFIED: Added prolific_id to the creation defaults ---
    ghs, created = Ghs_fk2.objects.get_or_create(
        person=person,
        defaults={
            'session_id': request.session.get('participant_session_id', ''),
            'prolific_id': person.prolific_username  # Sets it on creation
        }
    )
    # -----------------------------------------------------------

    # 2) How many rounds have we already done?
    done = len(ghs.iterations)
    # If they’ve done both, send them on
    if done >= MAX_PHASES:
        return redirect('Labels_Nudges:thank_u')

    current_phase = done + 1  # 1 or 2

    if request.method == 'POST':
        form = Ghs_fk2Form(request.POST)
        if form.is_valid():
            # 3) Collect this round’s answers
            entry = {
                'like_chosen': form.cleaned_data['like_chosen'],
                'looking_forward': form.cleaned_data['looking_forward'],
                'fit_preferences': form.cleaned_data['fit_preferences'],
                'know_better': form.cleaned_data['know_better'],
                'interesting': form.cleaned_data['interesting'],
                'fitted_preferences': form.cleaned_data['fitted_preferences'],
                'relevant': form.cleaned_data['relevant'],
                'similar_to_each_other': form.cleaned_data['similar_to_each_other'],
                'differed_topics': form.cleaned_data['differed_topics'],
                'diversity_high': form.cleaned_data['diversity_high'],
                'timestamp': timezone.now().isoformat(),
            }
            ghs.iterations.append(entry)
            ghs.session_id = request.session.get('participant_session_id', '')

            # --- ADDED THIS LINE, as per the guide ---
            # Ensures the prolific_id is always up-to-date on every save.
            ghs.prolific_id = person.prolific_username
            # ----------------------------------------

            ghs.save()

            # 4) Mark the right phase flag and issue code
            if current_phase == 1:
                person.phase_one_complete = True
                person.redemption_code_phase1 = generate_redemption_code()
                person.last_home = timezone.now()  # Start the 2-day clock now
                person.save()
                # After round 1, go to redemption for phase 1
                return redirect('Labels_Nudges:redemption', phase=1)

            # current_phase == 2
            person.phase_two_complete = True
            person.redemption_code_phase2 = generate_redemption_code()
            person.save()
            # After round 2, send them to the thank-you page
            return redirect('Labels_Nudges:thank_u')

    else:
        form = Ghs_fk2Form()

    return render(request, 'Labels_Nudges/ghs_fk2.html', {
        'form': form,
        'fields': [form[field] for field in form.fields],
        'current_phase': current_phase,
        'max_phases': MAX_PHASES,
    })

# ── Configure your two “complete” URLs here ────────────────────────
COMPLETION_LINKS = {
    1: "https://app.prolific.com/submissions/complete?cc=CBH7XMCP",  # Phase 1 completion code
    2: "https://app.prolific.com/submissions/complete?cc=C11P51U2"  # Phase 2 completion code
}
# ─────────────────────────────────────────────────────────────────

def redemption(request, phase):
    pid = request.session.get('person_id')
    if not pid:
        return redirect('Labels_Nudges:home')
    person = get_object_or_404(Personal_info, id=pid)

    # 1) Grab the Prolific ID from session (fallback to model)
    prolific_id = request.session.get('prolific_username') or getattr(person, 'prolific_username', '')

    # 2) Mark them complete in your DB
    code_field = f"redemption_code_phase{phase}"
    setattr(person, code_field, prolific_id)
    setattr(person, f"phase_{['one','two','three'][phase-1]}_complete", True)
    person.save()
    logger.info("Person %s completed phase %d, code=%s", pid, phase, prolific_id)

    # 3) Build the correct Prolific URL
    base = COMPLETION_LINKS.get(phase)
    if not base:
        # fallback: just link home
        complete_url = reverse('Labels_Nudges:home')
    else:
        complete_url = f"{base}"

    # 4) Clear out news‐related session state
    for k in ('selected_articles','selected_article_ids','article_clusters','saved_articles'):
        request.session.pop(k, None)

    # 5) Decide what your “internal next” is
    if phase == 1:
        next_view = 'Labels_Nudges:topic_preference'
        next_phase = 2
    else:
        next_view = 'Labels_Nudges:thank_u'
        next_phase = None

    return render(request, 'Labels_Nudges/redemption.html', {
        'current_phase':    phase,
        'next_phase_num':   next_phase,
        'next_view_name':   next_view,
        'prolific_code':    prolific_id,
        'complete_url':     complete_url,
    })


def choice_evaluation4(request):
    global Sub_100Articals
    global Sub_100ArticalsDict
    try:
        personDict = request.session[
            'person_id']  # Jeng: Here is the person ID for the Dict and will to be the KEY in Sub_100ArticalsDict below

        # Sub_100ArticalsDict = {personDict: Sub_100Articals} # Jeng: Here I save the 10 news based on different person ID, KEY is person ID Value is 10 NEWS
        print('The Sub_100ArticalsDict for this person ID below is:')
        print(Sub_100ArticalsDict[personDict])
        print('The NEWS ID for this page is:')
        print(Sub_100ArticalsDict[personDict][3])
        print('The Sub_100ArticalsDict for all is:')
        print(Sub_100ArticalsDict)
        # global size10
        print('The Sub_100Articals below is:')
        print(Sub_100Articals)
        # Sub_100Articals= sample(range(1, 101), 10) # Set a global list involving random 10 news when this function is loaded, and preduce 10 sampling news for other functions from 100 datasets, to narrow down the scope.
        print('The i4 below is:')
        i4 = Sub_100ArticalsDict[personDict][3]
        # i1 = Sub_100Articals[0]
        print('The NEWS ID below is:')
        print(i4)
        print('Person ID is' + str(personDict))
        print('The keys is:')
        print(Sub_100ArticalsDict.keys())
        # EvaNews = EvaluateChoices()
    except:
        print("An exception occurred")
        return redirect('Labels_Nudges:home')

    newsAttributes = NewsRec.objects.get(pk=i4)
    newsList = [newsAttributes.id, newsAttributes.title, newsAttributes.text]
    user_selected = EvaluateChoices4.objects.filter(person_id=request.session['person_id'])
    if user_selected:
        EvaluateChoices4.objects.filter(person_id=request.session['person_id']).delete()

    if request.method == 'POST':
        evaluation_form4 = ChoiceEvaluationForm4(request.POST)
        person4 = request.session['person_id']
        ChoiceEvaltion4 = EvaluateChoices4()
        if evaluation_form4.is_valid():
            # print("-----------here we are")
            # ChoiceEvaltion.person = request.session['person_id']
            evaluation4_ = evaluation_form4.save(commit=False)
            evaluation4_.person_id = person4
            # ChoiceEvaltion.person_id = evaluation_form.foriengkey
            evaluation4_.session_id = request.session['prolific_id']
            evaluation4_.created = i4
            evaluation4_.save()
            return redirect('Labels_Nudges:thank_u')
    else:
        evaluation_form4 = ChoiceEvaluationForm4()
    return render(request, 'Labels_Nudges/choice_evaluation4.html',
                  context={'eval_form': evaluation_form4, 'newsList': newsList})


def choice_evaluation5(request):
    global Sub_100Articals
    global Sub_100ArticalsDict
    try:
        personDict = request.session[
            'person_id']  # Jeng: Here is the person ID for the Dict and will to be the KEY in Sub_100ArticalsDict below

        # Sub_100ArticalsDict = {personDict: Sub_100Articals} # Jeng: Here I save the 10 news based on different person ID, KEY is person ID Value is 10 NEWS
        print('The Sub_100ArticalsDict for this person ID below is:')
        print(Sub_100ArticalsDict[personDict])
        print('The NEWS ID for this page is:')
        print(Sub_100ArticalsDict[personDict][4])
        print('The Sub_100ArticalsDict for all is:')
        print(Sub_100ArticalsDict)
        # global size10
        print('The Sub_100Articals below is:')
        print(Sub_100Articals)
        # Sub_100Articals= sample(range(1, 101), 10) # Set a global list involving random 10 news when this function is loaded, and preduce 10 sampling news for other functions from 100 datasets, to narrow down the scope.
        print('The i5 below is:')
        i5 = Sub_100ArticalsDict[personDict][4]
        # i1 = Sub_100Articals[0]
        print('The NEWS ID below is:')
        print(i5)
        print('Person ID is' + str(personDict))
        print('The keys is:')
        print(Sub_100ArticalsDict.keys())
        # EvaNews = EvaluateChoices()
    except:
        print("An exception occurred")
        return redirect('Labels_Nudges:home')

    newsAttributes = ClimateNews.objects.get(pk=i5)
    newsList = [newsAttributes.id, newsAttributes.image_url, newsAttributes.title, newsAttributes.text,
                newsAttributes.author, newsAttributes.date]
    user_selected = EvaluateChoices5.objects.filter(person_id=request.session['person_id'])
    if user_selected:
        EvaluateChoices5.objects.filter(person_id=request.session['person_id']).delete()

    if request.method == 'POST':
        evaluation_form5 = ChoiceEvaluationForm5(request.POST)
        person5 = request.session['person_id']
        ChoiceEvaltion5 = EvaluateChoices5()
        if evaluation_form5.is_valid():
            # print("-----------here we are")
            # ChoiceEvaltion.person = request.session['person_id']
            evaluation5_ = evaluation_form5.save(commit=False)
            evaluation5_.person_id = person5
            # ChoiceEvaltion.person_id = evaluation_form.foriengkey
            evaluation5_.session_id = request.session['prolific_id']
            evaluation5_.created = i5
            evaluation5_.save()
            return redirect('Labels_Nudges:choice_evaluation6')
    else:
        evaluation_form5 = ChoiceEvaluationForm5()
    return render(request, 'Labels_Nudges/choice_evaluation5.html',
                  context={'eval_form': evaluation_form5, 'newsList': newsList})


def choice_evaluation6(request):
    global Sub_100Articals
    global Sub_100ArticalsDict
    try:
        personDict = request.session[
            'person_id']  # Jeng: Here is the person ID for the Dict and will to be the KEY in Sub_100ArticalsDict below

        # Sub_100ArticalsDict = {personDict: Sub_100Articals} # Jeng: Here I save the 10 news based on different person ID, KEY is person ID Value is 10 NEWS
        print('The Sub_100ArticalsDict for this person ID below is:')
        print(Sub_100ArticalsDict[personDict])
        print('The NEWS ID for this page is:')
        print(Sub_100ArticalsDict[personDict][5])
        print('The Sub_100ArticalsDict for all is:')
        print(Sub_100ArticalsDict)
        # global size10
        print('The Sub_100Articals below is:')
        print(Sub_100Articals)
        # Sub_100Articals= sample(range(1, 101), 10) # Set a global list involving random 10 news when this function is loaded, and preduce 10 sampling news for other functions from 100 datasets, to narrow down the scope.
        print('The i6 below is:')
        i6 = Sub_100ArticalsDict[personDict][5]
        # i1 = Sub_100Articals[0]
        print('The NEWS ID below is:')
        print(i6)
        print('Person ID is' + str(personDict))
        print('The keys is:')
        print(Sub_100ArticalsDict.keys())
        # EvaNews = EvaluateChoices()
    except:
        print("An exception occurred")
        return redirect('Labels_Nudges:home')

    newsAttributes = ClimateNews.objects.get(pk=i6)
    newsList = [newsAttributes.id, newsAttributes.image_url, newsAttributes.title, newsAttributes.text,
                newsAttributes.author, newsAttributes.date]
    user_selected = EvaluateChoices6.objects.filter(person_id=request.session['person_id'])
    if user_selected:
        EvaluateChoices6.objects.filter(person_id=request.session['person_id']).delete()

    if request.method == 'POST':
        evaluation_form6 = ChoiceEvaluationForm6(request.POST)
        person6 = request.session['person_id']
        ChoiceEvaltion6 = EvaluateChoices6()
        if evaluation_form6.is_valid():
            # print("-----------here we are")
            # ChoiceEvaltion.person = request.session['person_id']
            evaluation6_ = evaluation_form6.save(commit=False)
            evaluation6_.person_id = person6
            # ChoiceEvaltion.person_id = evaluation_form.foriengkey
            evaluation6_.session_id = request.session['prolific_id']
            evaluation6_.created = i6
            evaluation6_.save()
            return redirect('Labels_Nudges:choice_evaluation7')
    else:
        evaluation_form6 = ChoiceEvaluationForm6()
    return render(request, 'Labels_Nudges/choice_evaluation6.html',
                  context={'eval_form': evaluation_form6, 'newsList': newsList})


def choice_evaluation7(request):
    global Sub_100Articals
    global Sub_100ArticalsDict
    try:
        personDict = request.session[
            'person_id']  # Jeng: Here is the person ID for the Dict and will to be the KEY in Sub_100ArticalsDict below

        # Sub_100ArticalsDict = {personDict: Sub_100Articals} # Jeng: Here I save the 10 news based on different person ID, KEY is person ID Value is 10 NEWS
        print('The Sub_100ArticalsDict for this person ID below is:')
        print(Sub_100ArticalsDict[personDict])
        print('The NEWS ID for this page is:')
        print(Sub_100ArticalsDict[personDict][6])
        print('The Sub_100ArticalsDict for all is:')
        print(Sub_100ArticalsDict)
        # global size10
        print('The Sub_100Articals below is:')
        print(Sub_100Articals)
        # Sub_100Articals= sample(range(1, 101), 10) # Set a global list involving random 10 news when this function is loaded, and preduce 10 sampling news for other functions from 100 datasets, to narrow down the scope.
        print('The i7 below is:')
        i7 = Sub_100ArticalsDict[personDict][6]
        # i1 = Sub_100Articals[0]
        print('The NEWS ID below is:')
        print(i7)
        print('Person ID is' + str(personDict))
        print('The keys is:')
        print(Sub_100ArticalsDict.keys())
        # EvaNews = EvaluateChoices()
    except:
        print("An exception occurred")
        return redirect('Labels_Nudges:home')

    newsAttributes = ClimateNews.objects.get(pk=i7)
    newsList = [newsAttributes.id, newsAttributes.image_url, newsAttributes.title, newsAttributes.text,
                newsAttributes.author, newsAttributes.date]
    user_selected = EvaluateChoices7.objects.filter(person_id=request.session['person_id'])
    if user_selected:
        EvaluateChoices7.objects.filter(person_id=request.session['person_id']).delete()

    if request.method == 'POST':
        evaluation_form7 = ChoiceEvaluationForm7(request.POST)
        person7 = request.session['person_id']
        ChoiceEvaltion7 = EvaluateChoices7()
        if evaluation_form7.is_valid():
            # print("-----------here we are")
            # ChoiceEvaltion.person = request.session['person_id']
            evaluation7_ = evaluation_form7.save(commit=False)
            evaluation7_.person_id = person7
            # ChoiceEvaltion.person_id = evaluation_form.foriengkey
            evaluation7_.session_id = request.session['prolific_id']
            evaluation7_.created = i7
            evaluation7_.save()
            return redirect('Labels_Nudges:choice_evaluation8')
    else:
        evaluation_form7 = ChoiceEvaluationForm7()
    return render(request, 'Labels_Nudges/choice_evaluation7.html',
                  context={'eval_form': evaluation_form7, 'newsList': newsList})


def choice_evaluation8(request):
    global Sub_100Articals
    global Sub_100ArticalsDict
    try:
        personDict = request.session[
            'person_id']  # Jeng: Here is the person ID for the Dict and will to be the KEY in Sub_100ArticalsDict below

        # Sub_100ArticalsDict = {personDict: Sub_100Articals} # Jeng: Here I save the 10 news based on different person ID, KEY is person ID Value is 10 NEWS
        print('The Sub_100ArticalsDict for this person ID below is:')
        print(Sub_100ArticalsDict[personDict])
        print('The NEWS ID for this page is:')
        print(Sub_100ArticalsDict[personDict][7])
        print('The Sub_100ArticalsDict for all is:')
        print(Sub_100ArticalsDict)
        # global size10
        print('The Sub_100Articals below is:')
        print(Sub_100Articals)
        # Sub_100Articals= sample(range(1, 101), 10) # Set a global list involving random 10 news when this function is loaded, and preduce 10 sampling news for other functions from 100 datasets, to narrow down the scope.
        print('The i8 below is:')
        i8 = Sub_100ArticalsDict[personDict][7]
        # i1 = Sub_100Articals[0]
        print('The NEWS ID below is:')
        print(i8)
        print('Person ID is' + str(personDict))
        print('The keys is:')
        print(Sub_100ArticalsDict.keys())
        # EvaNews = EvaluateChoices()
    except:
        print("An exception occurred")
        return redirect('Labels_Nudges:home')

    newsAttributes = ClimateNews.objects.get(pk=i8)
    newsList = [newsAttributes.id, newsAttributes.image_url, newsAttributes.title, newsAttributes.text,
                newsAttributes.author, newsAttributes.date]
    user_selected = EvaluateChoices8.objects.filter(person_id=request.session['person_id'])
    if user_selected:
        EvaluateChoices8.objects.filter(person_id=request.session['person_id']).delete()

    if request.method == 'POST':
        evaluation_form8 = ChoiceEvaluationForm8(request.POST)
        person8 = request.session['person_id']
        ChoiceEvaltion8 = EvaluateChoices8()
        if evaluation_form8.is_valid():
            # print("-----------here we are")
            # ChoiceEvaltion.person = request.session['person_id']
            evaluation8_ = evaluation_form8.save(commit=False)
            evaluation8_.person_id = person8
            # ChoiceEvaltion.person_id = evaluation_form.foriengkey
            evaluation8_.session_id = request.session['prolific_id']
            evaluation8_.created = i8
            evaluation8_.save()
            return redirect('Labels_Nudges:choice_evaluation9')
    else:
        evaluation_form8 = ChoiceEvaluationForm8()
    return render(request, 'Labels_Nudges/choice_evaluation8.html',
                  context={'eval_form': evaluation_form8, 'newsList': newsList})


def choice_evaluation9(request):
    global Sub_100Articals
    global Sub_100ArticalsDict
    try:
        personDict = request.session[
            'person_id']  # Jeng: Here is the person ID for the Dict and will to be the KEY in Sub_100ArticalsDict below

        # Sub_100ArticalsDict = {personDict: Sub_100Articals} # Jeng: Here I save the 10 news based on different person ID, KEY is person ID Value is 10 NEWS
        print('The Sub_100ArticalsDict for this person ID below is:')
        print(Sub_100ArticalsDict[personDict])
        print('The NEWS ID for this page is:')
        print(Sub_100ArticalsDict[personDict][8])
        print('The Sub_100ArticalsDict for all is:')
        print(Sub_100ArticalsDict)
        # global size10
        print('The Sub_100Articals below is:')
        print(Sub_100Articals)
        # Sub_100Articals= sample(range(1, 101), 10) # Set a global list involving random 10 news when this function is loaded, and preduce 10 sampling news for other functions from 100 datasets, to narrow down the scope.
        print('The i9 below is:')
        i9 = Sub_100ArticalsDict[personDict][8]
        # i1 = Sub_100Articals[0]
        print('The NEWS ID below is:')
        print(i9)
        print('Person ID is' + str(personDict))
        print('The keys is:')
        print(Sub_100ArticalsDict.keys())
        # EvaNews = EvaluateChoices()
    except:
        print("An exception occurred")
        return redirect('Labels_Nudges:home')

    newsAttributes = ClimateNews.objects.get(pk=i9)
    newsList = [newsAttributes.id, newsAttributes.image_url, newsAttributes.title, newsAttributes.text,
                newsAttributes.author, newsAttributes.date]
    user_selected = EvaluateChoices9.objects.filter(person_id=request.session['person_id'])
    if user_selected:
        EvaluateChoices9.objects.filter(person_id=request.session['person_id']).delete()

    if request.method == 'POST':
        evaluation_form9 = ChoiceEvaluationForm9(request.POST)
        person9 = request.session['person_id']
        ChoiceEvaltion9 = EvaluateChoices9()
        if evaluation_form9.is_valid():
            # print("-----------here we are")
            # ChoiceEvaltion.person = request.session['person_id']
            evaluation9_ = evaluation_form9.save(commit=False)
            evaluation9_.person_id = person9
            # ChoiceEvaltion.person_id = evaluation_form.foriengkey
            evaluation9_.session_id = request.session['prolific_id']
            evaluation9_.created = i9
            evaluation9_.save()
            return redirect('Labels_Nudges:choice_evaluation10')
    else:
        evaluation_form9 = ChoiceEvaluationForm9()
    return render(request, 'Labels_Nudges/choice_evaluation9.html',
                  context={'eval_form': evaluation_form9, 'newsList': newsList})


def choice_evaluation10(request):
    global Sub_100Articals
    global Sub_100ArticalsDict
    try:
        personDict = request.session[
            'person_id']  # Jeng: Here is the person ID for the Dict and will to be the KEY in Sub_100ArticalsDict below

        # Sub_100ArticalsDict = {personDict: Sub_100Articals} # Jeng: Here I save the 10 news based on different person ID, KEY is person ID Value is 10 NEWS
        print('The Sub_100ArticalsDict for this person ID below is:')
        print(Sub_100ArticalsDict[personDict])
        print('The NEWS ID for this page is:')
        print(Sub_100ArticalsDict[personDict][9])
        print('The Sub_100ArticalsDict for all is:')
        print(Sub_100ArticalsDict)
        # global size10
        print('The Sub_100Articals below is:')
        print(Sub_100Articals)
        # Sub_100Articals= sample(range(1, 101), 10) # Set a global list involving random 10 news when this function is loaded, and preduce 10 sampling news for other functions from 100 datasets, to narrow down the scope.
        print('The i10 below is:')
        i10 = Sub_100ArticalsDict[personDict][9]
        # i1 = Sub_100Articals[0]
        print('The NEWS ID below is:')
        print(i10)
        print('Person ID is' + str(personDict))
        print('The keys is:')
        print(Sub_100ArticalsDict.keys())
        # EvaNews = EvaluateChoices()

    except:
        print("An exception occurred")
        return redirect('Labels_Nudges:home')

    newsAttributes = ClimateNews.objects.get(pk=i10)

    newsList = [newsAttributes.id, newsAttributes.image_url, newsAttributes.title, newsAttributes.text,
                newsAttributes.author, newsAttributes.date]
    user_selected = EvaluateChoices10.objects.filter(person_id=request.session['person_id'])
    if user_selected:
        EvaluateChoices10.objects.filter(person_id=request.session['person_id']).delete()

    if request.method == 'POST':
        evaluation_form10 = ChoiceEvaluationForm10(request.POST)
        person10 = request.session['person_id']
        ChoiceEvaltion10 = EvaluateChoices10()
        if evaluation_form10.is_valid():
            # print("-----------here we are")
            # ChoiceEvaltion.person = request.session['person_id']
            evaluation10_ = evaluation_form10.save(commit=False)
            evaluation10_.person_id = person10
            # ChoiceEvaltion.person_id = evaluation_form.foriengkey
            evaluation10_.session_id = request.session['prolific_id']
            evaluation10_.created = i10
            evaluation10_.save()
            return redirect('Labels_Nudges:thank_u')
    else:
        evaluation_form10 = ChoiceEvaluationForm10()
    return render(request, 'Labels_Nudges/choice_evaluation10.html',
                  context={'eval_form': evaluation_form10, 'newsList': newsList})


def thank_u(request):
    # if there’s anything you need to show on the thank-you page,
    # grab it before you clear the session:
    final_code = request.session.get('session_id')

    # remove only that key
    request.session.pop('session_id', None)

    complete_url = COMPLETION_LINKS.get(2, reverse('Labels_Nudges:home'))
    return render(request, "Labels_Nudges/thank_u.html", {
        "complete_url": complete_url,
    })


def error_404(request, exception):
    data = {}
    return render(request, 'Labels_Nudges/404.html', data)


def error_500(request):
    data = {}
    return render(request, 'Labels_Nudges/404.html', data)
