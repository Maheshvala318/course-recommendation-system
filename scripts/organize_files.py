"""
Move existing data files to the proper directory structure.

This script:
1. Copies pickle files from root/Model/ to data/processed/
2. Copies CSV files to data/raw/
3. Moves old large files to _legacy_large_files/

Usage:
    python scripts/organize_files.py
"""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import LEGACY_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR


def organize():
    """Organize project files into proper directory structure."""

    # Create directories
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("FILE ORGANIZER — Course Recommendation System")
    print("=" * 60)

    # ── CSV files → data/raw/ ──
    csv_moves = [
        (PROJECT_ROOT / "udemy.csv", RAW_DATA_DIR / "udemy.csv"),
        (PROJECT_ROOT / "coursea_data.csv", RAW_DATA_DIR / "coursera_data.csv"),
        (PROJECT_ROOT / "Notebook" / "Coursera.csv", RAW_DATA_DIR / "coursera_full.csv"),
        (PROJECT_ROOT / "Notebook" / "udemy_courses.csv.xls", RAW_DATA_DIR / "udemy_courses.csv.xls"),
        (PROJECT_ROOT / "Notebook" / "user_data.csv", RAW_DATA_DIR / "user_data.csv"),
        (PROJECT_ROOT / "Dataset" / "udemy.csv", None),  # Skip duplicate
    ]

    print("\n📁 CSV Files → data/raw/")
    for src, dst in csv_moves:
        if src.exists():
            if dst is None:
                print(f"   ⏭️  Skipping duplicate: {src.name}")
                continue
            if not dst.exists():
                shutil.copy2(str(src), str(dst))
                print(f"   ✅ {src.relative_to(PROJECT_ROOT)} → {dst.relative_to(PROJECT_ROOT)}")
            else:
                print(f"   ⏭️  Already exists: {dst.relative_to(PROJECT_ROOT)}")
        else:
            print(f"   ❌ Not found: {src.relative_to(PROJECT_ROOT)}")

    # ── Pickle files → data/processed/ ──
    pkl_sources = {
        "course_data.pkl": [
            PROJECT_ROOT / "Model" / "course_data.pkl",
            PROJECT_ROOT / "course_data.pkl",
        ],
        "course_data_original.pkl": [
            PROJECT_ROOT / "Model" / "course_data_original.pkl",
            PROJECT_ROOT / "course_data_original.pkl",
        ],
        "combined_features.pkl": [
            PROJECT_ROOT / "Model" / "combined_features.pkl",
            PROJECT_ROOT / "combined_features.pkl",
        ],
        "tfidf_matrix.pkl": [
            PROJECT_ROOT / "Model" / "tfidf_matrix.pkl",
            PROJECT_ROOT / "tfidf_matrix.pkl",
        ],
        "tfidf_vectorizer.pkl": [
            PROJECT_ROOT / "Model" / "tfidf_vectorizer.pkl",
            PROJECT_ROOT / "tfidf_vectorizer.pkl",
        ],
    }

    print("\n📁 Pickle Files → data/processed/")
    for target_name, source_paths in pkl_sources.items():
        dst = PROCESSED_DATA_DIR / target_name
        if dst.exists():
            print(f"   ⏭️  Already exists: {dst.relative_to(PROJECT_ROOT)}")
            continue
        for src in source_paths:
            if src.exists():
                shutil.copy2(str(src), str(dst))
                print(f"   ✅ {src.relative_to(PROJECT_ROOT)} → data/processed/{target_name}")
                break
        else:
            print(f"   ❌ Not found: {target_name}")

    # ── Large similarity matrices → _legacy_large_files/ ──
    large_files = [
        PROJECT_ROOT / "similarity_matrix.pkl",
        PROJECT_ROOT / "Model" / "similarity_matrix.pkl",
        PROJECT_ROOT / "Model" / "similarity_matrix_text.pkl",
    ]

    print(f"\n📦 Large Files → _legacy_large_files/ (gitignored)")
    for src in large_files:
        if src.exists():
            dst = LEGACY_DIR / src.name
            if not dst.exists():
                print(f"   📦 Moving {src.relative_to(PROJECT_ROOT)} ({src.stat().st_size / (1024**3):.2f} GB)")
                shutil.move(str(src), str(dst))
            else:
                print(f"   ⏭️  Already in legacy: {src.name}")
        else:
            print(f"   ⏭️  Not found: {src.relative_to(PROJECT_ROOT)}")

    # ── Move Udemy Excel to data/raw/ ──
    xlsx_src = PROJECT_ROOT / "Udemy_course_detail.xlsx"
    if xlsx_src.exists():
        dst = RAW_DATA_DIR / "Udemy_course_detail.xlsx"
        if not dst.exists():
            shutil.copy2(str(xlsx_src), str(dst))
            print(f"\n   ✅ {xlsx_src.name} → data/raw/")

    print("\n✅ File organization complete!")
    print("   Run 'python scripts/convert_similarity_matrix.py' next to create the sparse top-K index.")


if __name__ == "__main__":
    organize()
