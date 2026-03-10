"""
Convert the full similarity matrix (~1.9GB) to a sparse top-K representation.

This script reads the large `similarity_matrix.pkl` and creates a compact
`similarity_topk.pkl` that stores only the top-K most similar courses for
each course. This reduces file size by ~99%.

Usage:
    python scripts/convert_similarity_matrix.py

    By default, reads from Model/similarity_matrix_text.pkl (or root similarity_matrix.pkl)
    and writes to data/processed/similarity_topk.pkl.

    Old large files are moved to _legacy_large_files/ (gitignored).
"""

import os
import pickle
import shutil
import sys
from pathlib import Path

import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import (
    LEGACY_DIR,
    PROCESSED_DATA_DIR,
    SIMILARITY_TOP_K,
    SIMILARITY_TOPK_PKL,
)

# ──────────────────────────────────────────────
# Locate the full similarity matrix
# ──────────────────────────────────────────────
POSSIBLE_PATHS = [
    PROJECT_ROOT / "Model" / "similarity_matrix_text.pkl",
    PROJECT_ROOT / "Model" / "similarity_matrix.pkl",
    PROJECT_ROOT / "similarity_matrix.pkl",
]


def find_similarity_matrix() -> Path:
    """Find the first existing similarity matrix file."""
    for path in POSSIBLE_PATHS:
        if path.exists():
            print(f"✅ Found similarity matrix: {path}")
            print(f"   Size: {path.stat().st_size / (1024**3):.2f} GB")
            return path
    raise FileNotFoundError(
        "No similarity matrix found. Looked in:\n"
        + "\n".join(f"  - {p}" for p in POSSIBLE_PATHS)
    )


def convert_to_topk(
    matrix: np.ndarray, top_k: int = SIMILARITY_TOP_K
) -> dict:
    """
    Convert a full (N x N) similarity matrix to a sparse top-K dict.

    Args:
        matrix: Full similarity matrix, shape (N, N).
        top_k: Number of top similar items to keep per course.

    Returns:
        Dict mapping course_idx -> list of (similar_idx, score) tuples,
        sorted by score descending.
    """
    n_courses = matrix.shape[0]
    topk_dict = {}

    print(f"🔄 Converting {n_courses} courses to top-{top_k} representation...")

    for i in range(n_courses):
        if i % 5000 == 0:
            print(f"   Processing course {i}/{n_courses} ({i/n_courses*100:.1f}%)")

        row = matrix[i]
        # Get top-K indices (exclude self)
        # Set self-similarity to -inf to exclude it
        row_copy = row.copy()
        row_copy[i] = -np.inf
        top_indices = np.argsort(row_copy)[-top_k:][::-1]
        top_scores = row[top_indices]

        topk_dict[i] = [(int(idx), float(score)) for idx, score in zip(top_indices, top_scores)]

    return topk_dict


def move_to_legacy(source: Path):
    """Move a large file to the _legacy_large_files directory."""
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    dest = LEGACY_DIR / source.name
    if source.exists():
        print(f"📦 Moving {source.name} → _legacy_large_files/")
        shutil.move(str(source), str(dest))


def main():
    print("=" * 60)
    print("SIMILARITY MATRIX CONVERTER")
    print(f"Top-K: {SIMILARITY_TOP_K} | Output: {SIMILARITY_TOPK_PKL}")
    print("=" * 60)

    # Step 1: Find and load the full matrix
    source_path = find_similarity_matrix()
    print(f"\n📂 Loading full similarity matrix from {source_path}...")
    print("   (This may take a few minutes for ~1.9GB file)")

    with open(source_path, "rb") as f:
        full_matrix = pickle.load(f)

    print(f"   Matrix shape: {full_matrix.shape}")
    print(f"   Matrix dtype: {full_matrix.dtype}")

    # Step 2: Convert to sparse top-K
    topk_dict = convert_to_topk(full_matrix, SIMILARITY_TOP_K)

    # Step 3: Save the compact representation
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n💾 Saving top-K index to {SIMILARITY_TOPK_PKL}...")
    with open(SIMILARITY_TOPK_PKL, "wb") as f:
        pickle.dump(topk_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

    new_size = SIMILARITY_TOPK_PKL.stat().st_size
    old_size = source_path.stat().st_size if source_path.exists() else 0
    reduction = (1 - new_size / old_size) * 100 if old_size > 0 else 0

    print(f"   Old size: {old_size / (1024**3):.2f} GB")
    print(f"   New size: {new_size / (1024**2):.2f} MB")
    print(f"   Reduction: {reduction:.1f}%")

    # Step 4: Move old large files to legacy folder
    print("\n📦 Moving old large files to _legacy_large_files/ (gitignored)...")
    for path in POSSIBLE_PATHS:
        if path.exists():
            move_to_legacy(path)

    # Also move root-level duplicates
    root_pkl_files = [
        PROJECT_ROOT / "similarity_matrix.pkl",
    ]
    for pkl in root_pkl_files:
        if pkl.exists():
            move_to_legacy(pkl)

    print("\n✅ Done! Sparse top-K similarity index created successfully.")
    print(f"   Stored {len(topk_dict)} courses × {SIMILARITY_TOP_K} neighbors each.")


if __name__ == "__main__":
    main()
