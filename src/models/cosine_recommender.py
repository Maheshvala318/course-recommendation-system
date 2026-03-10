"""
Cosine Similarity-based recommender.

Uses the precomputed sparse top-K similarity index for fast lookups.
"""

from typing import List

import numpy as np

from src.config.settings import DEFAULT_TOP_N


class CosineRecommender:
    """Recommends courses using precomputed cosine similarity scores."""

    def __init__(self, similarity_topk: dict):
        """
        Args:
            similarity_topk: Dict mapping course_idx -> list of
                (similar_idx, score) tuples, sorted by score descending.
        """
        self.similarity_topk = similarity_topk

    def recommend(self, course_idx: int, top_n: int = DEFAULT_TOP_N, diverse: bool = True) -> List[int]:
        """
        Get top-N similar courses for a given course index.

        Args:
            course_idx: Index of the source course.
            top_n: Number of recommendations to return.
            diverse: If true, picks one recommendation from further down the list
                (e.g., between 20-50) for diversity.

        Returns:
            List of recommended course indices.
        """
        if course_idx not in self.similarity_topk:
            return []

        neighbors = self.similarity_topk[course_idx]
        
        if not diverse or len(neighbors) <= top_n or top_n <= 1:
            return [idx for idx, score in neighbors[:top_n]]

        # Pick top_n - 1 from the top
        recommendations = [idx for idx, score in neighbors[:top_n-1]]
        
        # Pick one "diverse" course from further down (e.g., 20-50 range)
        # Use a stable but "random" choice based on course_idx to keep UI consistent
        diverse_pool = neighbors[20:50] if len(neighbors) > 20 else neighbors[top_n:]
        if diverse_pool:
            diverse_idx = diverse_pool[course_idx % len(diverse_pool)][0]
            recommendations.append(diverse_idx)
        else:
            # Fallback to the next top match
            recommendations.append(neighbors[top_n-1][0])
            
        return recommendations
