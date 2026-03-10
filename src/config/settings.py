"""
Centralized configuration for the Course Recommendation System.

All paths, model hyperparameters, and environment settings are managed here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# ──────────────────────────────────────────────
# Project Root
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ──────────────────────────────────────────────
# Data Paths
# ──────────────────────────────────────────────
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Pickle artifact paths
COURSE_DATA_PKL = PROCESSED_DATA_DIR / "course_data.pkl"
COURSE_DATA_ORIGINAL_PKL = PROCESSED_DATA_DIR / "course_data_original.pkl"
SIMILARITY_TOPK_PKL = PROCESSED_DATA_DIR / "similarity_topk.pkl"
TFIDF_MATRIX_PKL = PROCESSED_DATA_DIR / "tfidf_matrix.pkl"
TFIDF_VECTORIZER_PKL = PROCESSED_DATA_DIR / "tfidf_vectorizer.pkl"
COMBINED_FEATURES_PKL = PROCESSED_DATA_DIR / "combined_features.pkl"

# Legacy large files (gitignored)
LEGACY_DIR = PROJECT_ROOT / "_legacy_large_files"

# ──────────────────────────────────────────────
# Model Hyperparameters
# ──────────────────────────────────────────────
KNN_N_NEIGHBORS = int(os.getenv("KNN_N_NEIGHBORS", "6"))
KNN_METRIC = os.getenv("KNN_METRIC", "cosine")
DEFAULT_TOP_N = int(os.getenv("DEFAULT_TOP_N", "5"))
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "50"))

# ──────────────────────────────────────────────
# Similarity Weights (text vs numerical)
# ──────────────────────────────────────────────
TEXT_WEIGHT = float(os.getenv("TEXT_WEIGHT", "0.7"))
NUM_WEIGHT = float(os.getenv("NUM_WEIGHT", "0.3"))

# ──────────────────────────────────────────────
# MySQL (for scraping pipeline — reference only)
# ──────────────────────────────────────────────
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "new_udamy")

# ──────────────────────────────────────────────
# Streamlit Config
# ──────────────────────────────────────────────
STREAMLIT_PAGE_TITLE = "🎓 Course Recommendation System"
STREAMLIT_PAGE_ICON = "🎓"
STREAMLIT_LAYOUT = "wide"

# ──────────────────────────────────────────────
# Display columns for recommendation results
# ──────────────────────────────────────────────
DISPLAY_COLUMNS = [
    "course_id",
    "course_title",
    "price",
    "duration",
    "rating",
    "reviews",
    "number_of_subscribers",
]
