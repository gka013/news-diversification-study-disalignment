# More of the Same? A Longitudinal Evaluation of Two Similarity-based Approaches in a News Recommender System  
*(INRA 2025 — News Recommendation Study)*  

This repository contains the code and experiments for the paper:  

**“More of the Same? A Longitudinal Evaluation of Two Similarity-based Approaches in a News Recommender System”**  
Accepted at **INRA 2025**.  

---

Similarity-based personalization is generally assumed to boost engagement in recommender systems. However, is this also true beyond a single session in a news recommender?  

Amid concerns about filter bubbles and preference volatility, we propose an empirical evaluation of both short-term and longer-term effects of a news recommender system with two phases of data collection:  
- **Phase 1**: Initial preference elicitation and evaluation  
- **48-hour interval**  
- **Phase 2**: Personalized follow-up  

We compared two recommendation strategies in a preliminary longitudinal experiment (**N = 166**):  
- **Aligned feed**: Articles that met a ≥70% cosine-similarity threshold  
- **Disaligned feed**: Articles with only a 30% similarity threshold  

We collected:  
- **Behavioral metrics**: Article clicks, time on feed  
- **Evaluative metrics**: Self-reported familiarity, perceived recommendation quality, choice satisfaction, topic preferences  

**Findings:**  
- The *Aligned* feed was perceived to have more familiar content, while perceived diversity did not differ between strategies.  
- Users clicked on significantly fewer articles in Phase 2, particularly in the *Disaligned* condition.  
- We explored the volatility of topic preferences but did not observe significant differences across phases.  

**Conclusion:**  
Short-term increases in feed–profile similarity can enhance familiarity and maintain behavioral engagement (i.e., clicks). However, they do not lead to higher levels of perceived quality and choice satisfaction — raising doubts about the relationship between preference-based similarity and user satisfaction.  

## 📂 Repository Structure  
- `Labels_Nudges/` — Labeling strategies experiments  
- `management/commands/` — Scripts for running management tasks  
- `migrations/` — Database migration files  
- `admin.py`, `app.py`, `apps.py` — Django app setup  
- `choices.py`, `forms.py`, `models.py` — Core components for experiment setup  
- `recommender.py` — Recommendation algorithms (baseline + diversification methods)  
- `import.py` — Data ingestion and preprocessing  
- `log.txt` — Run logs and debugging notes  

---

## Installation  
Clone the repository and install dependencies:  
```bash
git clone https://github.com/yourusername/news-diversification-study.git
cd news-diversification-study
pip install -r requirements.txt
