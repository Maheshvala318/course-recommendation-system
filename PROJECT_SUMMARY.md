# 📋 PROJECT SUMMARY — Course Recommendation System

## 1. What Is This Project?

A **Course Recommendation System** that helps users discover relevant Udemy courses based on similarity analysis. Built with Python, scikit-learn, and Streamlit.

**Core Features:**
- Select a course → get 5 similar courses (3 algorithms)
- Type any course title → get recommendations even if it's not in the dataset
- Three recommendation methods: Cosine Similarity, KNN, Correlation

---

## 2. Data Pipeline

### 2.1 Data Collection (Scrapy)
Three Scrapy spiders scrape Udemy's API and pages:

```
category_link.py → Scrapes all Udemy category/subcategory URLs
         ↓
product_link.py  → For each category, scrapes all course links (paginated)
         ↓
Product_details.py → For each course, scrapes full details (price, tags, description)
         ↓
MySQL Database (new_udamy) → Stores raw scraped data
         ↓
udemy.csv (39MB, ~70K+ courses) → Exported for analysis
```

**Fields Collected:**
`course_id`, `course_title`, `url`, `price`, `is_paid`, `rating`, `reviews`, `number_of_subscribers`, `duration`, `level`, `platform`, `tag_keywords`, `description`, `sub_category_name`, `category_name`

### 2.2 Supplementary Data
- `coursera.csv` (5MB) — Coursera courses dataset (from external source)
- `udemy_courses.csv.xls` — Alternative Udemy dump

### 2.3 Feature Engineering (Notebooks)
Notebooks process raw data into ML-ready artifacts:

| Artifact | Size | Description |
|----------|------|-------------|
| `course_data.pkl` | 66MB | Normalized DataFrame (lowercase, cleaned text) |
| `course_data_original.pkl` | 38MB | Original DataFrame (for display) |
| `tfidf_vectorizer.pkl` | 161KB | Fitted TF-IDF vectorizer |
| `tfidf_matrix.pkl` | 16MB | TF-IDF sparse matrix (text features) |
| `combined_features.pkl` | 1.2MB | Hybrid feature matrix (text + numeric) |
| `similarity_matrix.pkl` | **1.9GB** | Full pairwise cosine similarity matrix |

---

## 3. Recommendation Algorithms

### 3.1 Cosine Similarity (Default)
- Uses precomputed `similarity_matrix.pkl` (hybrid text + numeric features)
- Fastest at runtime (matrix lookup)
- Best for "courses similar to X"

### 3.2 KNN (K-Nearest Neighbors)
- `NearestNeighbors(n_neighbors=6, metric='cosine')` on standardized combined features
- Returns distance-based similarity scores
- Good for exploring feature-space neighborhoods

### 3.3 Correlation-Based
- On-the-fly cosine similarity on z-scored (StandardScaler) combined features
- Avoids storing another massive matrix
- Approximates Pearson correlation on standardized features

### 3.4 Title Search (TF-IDF Fallback)
- User types any title → `preprocess_query()` cleans it
- If title exists in dataset → uses hybrid similarity matrix
- If title NOT in dataset → transforms query with TF-IDF vectorizer, computes cosine similarity against all courses

---

## 4. Current File Inventory

### Source Files (Python)
| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `main.py` | 32 | v1: Basic cosine similarity, no original_df | ❌ Superseded |
| `main2.py` | 35 | v2: Added original_df for display | ❌ Superseded |
| `main3.py` | 81 | v3: Added KNN + Correlation methods | ❌ Superseded |
| `Model/main3.py` | 459 | **v4 (LATEST)**: Full app w/ title search. Has duplicate code block (lines 230-459 repeat 1-229) | ✅ Best version |

### Scraping Files
| File | Lines | Purpose |
|------|-------|---------|
| `Scrapingfiles/category_link.py` | 37 | Scrapy spider: category URLs |
| `Scrapingfiles/product_link.py` | 114 | Scrapy spider: course links per category |
| `Scrapingfiles/Product_details.py` | 76 | Scrapy spider: full course details |
| `Scrapingfiles/udemy.sql` | ~44MB | MySQL dump of scraped data |

### Notebooks
| File | Purpose |
|------|---------|
| `Notebook/Practice.ipynb` | EDA iteration |
| `Notebook/Practice-Copy1.ipynb` | EDA copy |
| `Notebook/model.ipynb` | Model training & artifact export |
| `Untitled1.ipynb` | Root-level experiment notebook |
| `Untitled1-Copy1.ipynb` | Copy of experiment notebook |

### Data Files
| File | Size | Location |
|------|------|----------|
| `udemy.csv` | 39MB | Root + Dataset/ + Notebook/ (3 copies!) |
| `coursea_data.csv` | 85KB | Root |
| `Notebook/Coursera.csv` | 5MB | Notebook/ |
| `udemy_courses.csv.xls` | 694KB | Notebook/ |
| `user_data.csv` | 47B | Notebook/ (nearly empty) |

### Pickle Artifacts (duplicated across root & Model/)
| Artifact | Root | Model/ |
|----------|------|--------|
| `similarity_matrix.pkl` | 1.9GB | 1.9GB (as `similarity_matrix_text.pkl`) |
| `course_data.pkl` | 66MB | 66MB |
| `course_data_original.pkl` | 38MB | 38MB |
| `combined_features.pkl` | 1.2MB | 1.2MB |
| `tfidf_matrix.pkl` | 16MB | 16MB |
| `tfidf_vectorizer.pkl` | 161KB | 161KB |

---

## 5. Problems & Technical Debt

| # | Issue | Severity |
|---|-------|----------|
| 1 | **Duplicate files everywhere** — 3 copies of udemy.csv, 2 copies of every pkl | 🔴 High |
| 2 | **No `.gitignore`** — 1.9GB pkl files in git history | 🔴 High |
| 3 | **Hardcoded MySQL password** in `product_link.py` | 🔴 High |
| 4 | **Duplicate code block** in `Model/main3.py` (lines 230-459 = lines 1-229) | 🟡 Medium |
| 5 | **No modular structure** — everything in flat files | 🟡 Medium |
| 6 | **No dependency management** — no requirements.txt | 🟡 Medium |
| 7 | **No deployment config** — no Docker, no CI/CD | 🟡 Medium |
| 8 | **No Streamlit caching** — 1.9GB loaded on every rerun | 🟡 Medium |
| 9 | **No tests** of any kind | 🟠 Low-Med |
| 10 | **No README** beyond a single line | 🟠 Low-Med |

---

## 6. Deployment Plan

**Target:** Streamlit Cloud / Docker container on any cloud (AWS/GCP/Azure/Railway)

**Key Decisions:**
- Similarity matrix is **too large** (~1.9GB) for most free-tier deployments
  - **Option A:** Compute on-the-fly (slower but no large file needed)
  - **Option B:** Use cloud storage (S3/GCS) and download at startup
  - **Option C:** Compress / reduce matrix (top-K sparse representation)
- Docker image should include only `src/`, `data/processed/` (small pickles), and config
- Large files → `.gitignore` + external storage

---

## 7. Tech Stack Summary

```
Python 3.10+ │ Streamlit │ scikit-learn │ pandas │ numpy │ Scrapy │ pymysql │ Docker
```
