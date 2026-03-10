"""
Title-based search and recommendation engine.

Handles two cases:
1. Title exists in dataset → use precomputed top-K similarity index
2. Title not in dataset → use TF-IDF text similarity as fallback
"""

from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.config.settings import DEFAULT_TOP_N, DISPLAY_COLUMNS
from src.data.preprocessor import preprocess_query


class TitleSearchEngine:
    """Search and recommend courses by title (with TF-IDF fallback)."""

    def __init__(self, original_df, similarity_topk, tfidf_vectorizer, tfidf_matrix):
        """
        Args:
            original_df: Original DataFrame with course details.
            similarity_topk: Sparse top-K similarity dict.
            tfidf_vectorizer: Fitted TF-IDF vectorizer.
            tfidf_matrix: Precomputed TF-IDF matrix.
        """
        self.original_df = original_df
        self.similarity_topk = similarity_topk
        self.tfidf = tfidf_vectorizer
        self.tfidf_matrix = tfidf_matrix

    def search(
        self, title: str, top_n: int = DEFAULT_TOP_N
    ) -> Tuple[pd.DataFrame, pd.DataFrame, bool]:
        """
        Search for a course by title and return recommendations.

        Args:
            title: User-provided course title (can be approximate).
            top_n: Number of recommendations to return.

        Returns:
            Tuple of (base_course_df, recommended_courses_df, found_in_dataset).
        """
        # Case-insensitive exact match check
        mask = self.original_df["course_title"].str.lower() == title.lower()

        if mask.any():
            return self._recommend_from_dataset(mask, top_n)
        else:
            return self._recommend_from_query(title, top_n)

    def _recommend_from_dataset(
        self, mask: pd.Series, top_n: int
    ) -> Tuple[pd.DataFrame, pd.DataFrame, bool]:
        """Recommend using the precomputed top-K similarity index."""
        index = mask.idxmax()

        # Get similar courses from top-K index
        if index in self.similarity_topk:
            neighbors = self.similarity_topk[index]
            rec_indices = [idx for idx, score in neighbors[:top_n]]
        else:
            rec_indices = []

        cols = [c for c in DISPLAY_COLUMNS if c in self.original_df.columns]
        base_course = self.original_df.loc[[index], cols]
        recommended = self.original_df.iloc[rec_indices][cols] if rec_indices else pd.DataFrame(columns=cols)

        return base_course, recommended, True

    def _recommend_from_query(
        self, title: str, top_n: int
    ) -> Tuple[pd.DataFrame, pd.DataFrame, bool]:
        """Recommend using TF-IDF text similarity for unknown titles."""
        query_text = preprocess_query(title)
        query_vec = self.tfidf.transform([query_text])

        sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        rec_indices = np.argsort(-sims)[:top_n]

        base_course = pd.DataFrame(
            {
                "course_id": ["N/A"],
                "course_title": [title],
                "price": ["-"],
                "duration": ["-"],
                "rating": ["-"],
                "reviews": ["-"],
                "number_of_subscribers": ["-"],
            }
        )

        cols = [c for c in DISPLAY_COLUMNS if c in self.original_df.columns]
        recommended = self.original_df.iloc[rec_indices][cols]

        return base_course, recommended, False
