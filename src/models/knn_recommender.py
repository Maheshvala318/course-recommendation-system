"""
KNN-based recommender.

Uses scikit-learn's NearestNeighbors with cosine distance
on standardized combined features.
"""

from typing import List, Tuple

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from src.config.settings import DEFAULT_TOP_N, KNN_METRIC, KNN_N_NEIGHBORS


class KNNRecommender:
    """Recommends courses using K-Nearest Neighbors on combined features."""

    def __init__(self, combined_features: np.ndarray):
        """
        Initialize and fit the KNN model on standardized features.

        Args:
            combined_features: Combined feature matrix (text + numeric),
                shape (n_courses, n_features).
        """
        self.scaler = StandardScaler()
        self.features = self.scaler.fit_transform(combined_features)

        self.model = NearestNeighbors(
            n_neighbors=KNN_N_NEIGHBORS,
            metric=KNN_METRIC,
        )
        self.model.fit(self.features)

    def recommend(
        self, course_idx: int, top_n: int = DEFAULT_TOP_N
    ) -> Tuple[List[int], np.ndarray]:
        """
        Get top-N nearest neighbors for a given course.

        Args:
            course_idx: Index of the source course.
            top_n: Number of recommendations to return.

        Returns:
            Tuple of (recommended_indices, distances).
        """
        distances, indices = self.model.kneighbors(
            [self.features[course_idx]],
            n_neighbors=top_n + 1,
        )
        # Exclude the query course itself (first result)
        recommended_indices = indices[0][1:].tolist()
        recommended_distances = distances[0][1:]
        return recommended_indices, recommended_distances
