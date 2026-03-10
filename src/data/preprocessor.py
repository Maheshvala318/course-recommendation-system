"""
Text preprocessing utilities for the Course Recommendation System.

Provides query cleaning and text normalization functions used by
the recommendation models and the data pipeline.
"""

import re


def preprocess_query(text: str) -> str:
    """
    Clean and normalize a user query string.

    Applies the same transformations used during training:
    - Remove non-alphabetic characters (keep spaces)
    - Convert to lowercase
    - Strip leading/trailing whitespace

    Args:
        text: Raw user input string.

    Returns:
        Cleaned, lowercased string.
    """
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = text.lower().strip()
    # Collapse multiple spaces into one
    text = re.sub(r"\s+", " ", text)
    return text
