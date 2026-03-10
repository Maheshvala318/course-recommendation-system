"""
Correlation-based recommender.

Approximates Pearson correlation by computing cosine similarity
on z-scored (standardized) combined features — on the fly,
avoiding a massive precomputed matrix.
"""

from typing import List, Tuple

import numpy as np
from sklearn.preprocessing import StandardScaler

from src.config.settings import DEFAULT_TOP_N


class CorrelationRecommender:
    """Recommends courses using on-the-fly correlation-style similarity."""

    def __init__(self, combined_features: np.ndarray):
        """
        Standardize features for correlation computation.

        Args:
            combined_features: Combined feature matrix (text + numeric),
                shape (n_courses, n_features).
        """
        scaler = StandardScaler()
        self.features = scaler.fit_transform(combined_features)

    def recommend(
        self, course_idx: int, top_n: int = DEFAULT_TOP_N
    ) -> Tuple[List[int], np.ndarray]:
        """
        Compute correlation-style similarity for a course on the fly.

        Uses cosine similarity on z-scored features, which approximates
        Pearson correlation. This avoids storing a full (N x N) matrix.

        Args:
            course_idx: Index of the source course.
            top_n: Number of recommendations to return.

        Returns:
            Tuple of (recommended_indices, similarity_scores).
        """
        v = self.features[course_idx]  # shape: (n_features,)

        # Cosine similarity: (features @ v) / (||features|| * ||v||)
        norms = np.linalg.norm(self.features, axis=1)
        v_norm = np.linalg.norm(v)
        denom = norms * v_norm
        # Avoid division by zero
        denom = np.where(denom == 0, 1e-10, denom)
        sims = self.features @ v / denom
        sims = np.nan_to_num(sims)

        # Sort descending, exclude self
        sorted_idx = np.argsort(-sims)
        sorted_idx = sorted_idx[sorted_idx != course_idx]

        rec_indices = sorted_idx[:top_n].tolist()
        rec_scores = sims[sorted_idx[:top_n]]

        return rec_indices, rec_scores
