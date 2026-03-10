# PROJECT.md — Course Recommendation System

## Project Name
Course Recommendation System

## Description
A deployment-ready ML-powered course recommendation system that helps users discover relevant Udemy courses using three recommendation algorithms (Cosine Similarity, KNN, Correlation) and a free-text title search with TF-IDF fallback. Built with Python, scikit-learn, and Streamlit.

## Tech Stack
- **Language:** Python 3.10+
- **UI Framework:** Streamlit
- **ML:** scikit-learn (TF-IDF, KNN, Cosine Similarity)
- **Data:** pandas, numpy, scipy
- **Scraping:** Scrapy, pymysql, requests (reference only)
- **Deployment:** Docker, Streamlit Cloud
- **Config:** python-dotenv, environment variables

## Architecture
```
┌─────────────────────────────────────────────────────┐
│                    Streamlit UI                      │
│              (src/app/streamlit_app.py)              │
├─────────────────────────────────────────────────────┤
│          Recommendation Engines Layer                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │  Cosine   │ │   KNN    │ │  Corr    │ │ Title  │ │
│  │Recommender│ │Recommender│ │Recommender│ │Search  │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
├─────────────────────────────────────────────────────┤
│              Data Layer                              │
│  ┌──────────────────┐ ┌────────────────────┐        │
│  │   Data Loader     │ │   Preprocessor     │        │
│  │  (cached w/ st)   │ │  (text cleaning)   │        │
│  └──────────────────┘ └────────────────────┘        │
├─────────────────────────────────────────────────────┤
│              Config Layer                            │
│          (src/config/settings.py)                    │
├─────────────────────────────────────────────────────┤
│              Storage                                 │
│  data/processed/*.pkl    data/raw/*.csv              │
└─────────────────────────────────────────────────────┘
```

## Key Decisions
1. **Sparse Top-K Similarity:** Store only top-50 similar courses per course (~99% size reduction from 1.9GB → ~20MB)
2. **Streamlit Caching:** All data loads use `@st.cache_resource` — loads once, persists across reruns
3. **Modular Architecture:** Each recommendation algorithm is a separate class in its own file
4. **Environment Variables:** All sensitive data and configurable params via `.env`
