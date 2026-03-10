"""
Data loader module for the Course Recommendation System.

Handles loading of pickle artifacts and CSV files with Streamlit caching
to avoid reloading on every app rerun.
"""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from scipy import sparse

from src.config.settings import (
    COMBINED_FEATURES_PKL,
    COURSE_DATA_ORIGINAL_PKL,
    COURSE_DATA_PKL,
    SIMILARITY_TOPK_PKL,
    TFIDF_MATRIX_PKL,
    TFIDF_VECTORIZER_PKL,
)


@st.cache_resource(show_spinner="Loading course data...")
def load_course_data() -> pd.DataFrame:
    """Load the normalized (processed) course DataFrame."""
    return pd.read_pickle(COURSE_DATA_PKL)


@st.cache_resource(show_spinner="Loading original course data...")
def load_original_course_data() -> pd.DataFrame:
    """Load the original (unmodified) course DataFrame for display."""
    return pd.read_pickle(COURSE_DATA_ORIGINAL_PKL)


@st.cache_resource(show_spinner="Loading similarity index...")
def load_similarity_topk() -> dict:
    """
    Load the sparse top-K similarity index.

    Returns:
        dict mapping course_idx -> list of (similar_idx, score) tuples,
        sorted by score descending. Each list has at most K entries.
    """
    with open(SIMILARITY_TOPK_PKL, "rb") as f:
        return pickle.load(f)


@st.cache_resource(show_spinner="Loading TF-IDF vectorizer...")
def load_tfidf_vectorizer():
    """Load the fitted TF-IDF vectorizer."""
    with open(TFIDF_VECTORIZER_PKL, "rb") as f:
        return pickle.load(f)


@st.cache_resource(show_spinner="Loading TF-IDF matrix...")
def load_tfidf_matrix():
    """Load the precomputed TF-IDF matrix (sparse)."""
    with open(TFIDF_MATRIX_PKL, "rb") as f:
        return pickle.load(f)


@st.cache_resource(show_spinner="Loading combined features...")
def load_combined_features() -> np.ndarray:
    """Load the combined feature matrix (text + numeric)."""
    with open(COMBINED_FEATURES_PKL, "rb") as f:
        return pickle.load(f)
