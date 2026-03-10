"""
02_feature_engineering.py — Data Cleaning & Feature Engineering

Cleans the raw Udemy dataset and creates processed DataFrames:
- Proper price parsing (strip currency symbols → float)
- Duration parsing (text → float hours)
- Log-transform for subscribers
- Text feature construction (title + description + tags + category)
- Stemming for text features
- Saves: course_data.pkl (processed) + course_data_original.pkl (display)

Run from project root:
    python notebooks/02_feature_engineering.py
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import (
    COURSE_DATA_ORIGINAL_PKL,
    COURSE_DATA_PKL,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)

print("=" * 60)
print("FEATURE ENGINEERING — Course Recommendation System")
print("=" * 60)

# ──────────────────────────────────────────────
# Step 1: Load Raw Data
# ──────────────────────────────────────────────
csv_path = RAW_DATA_DIR / "udemy.csv"
print(f"\n📂 Loading: {csv_path}")
df = pd.read_csv(csv_path)
print(f"   Shape: {df.shape}")

# Save original for display (before any transformations)
original_df = df.copy()


# ──────────────────────────────────────────────
# Step 2: Clean Price
# ──────────────────────────────────────────────
print("\n💰 Step 2: Cleaning price column...")
if "price" in df.columns:
    # Remove currency symbols and whitespace
    df["price"] = (
        df["price"]
        .astype(str)
        .str.replace(r"[£$€,\s]", "", regex=True)
        .str.strip()
    )
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
    print(f"   Price range: {df['price'].min():.2f} — {df['price'].max():.2f}")
    print(f"   Free courses: {(df['price'] == 0).sum()}")


# ──────────────────────────────────────────────
# Step 3: Parse Duration
# ──────────────────────────────────────────────
print("\n⏱️  Step 3: Parsing duration...")
if "duration" in df.columns:
    # Extract numeric part (hours)
    df["duration"] = (
        df["duration"]
        .astype(str)
        .str.extract(r"([\d.]+)", expand=False)
    )
    df["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0.0)
    print(f"   Duration range: {df['duration'].min():.1f} — {df['duration'].max():.1f} hours")


# ──────────────────────────────────────────────
# Step 4: Clean Numeric Columns
# ──────────────────────────────────────────────
print("\n🔢 Step 4: Cleaning numeric columns...")

for col in ["rating", "reviews", "number_of_subscribers", "is_paid"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        print(f"   {col}: min={df[col].min()}, max={df[col].max()}")


# ──────────────────────────────────────────────
# Step 5: Build Text Features
# ──────────────────────────────────────────────
print("\n📝 Step 5: Building text features...")


def clean_text(text: str) -> str:
    """Clean text: lowercase, remove special chars, collapse spaces."""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Try stemming (optional — falls back to simple cleaning)
try:
    from nltk.stem import PorterStemmer

    stemmer = PorterStemmer()

    def stem_text(text: str) -> str:
        words = clean_text(text).split()
        return " ".join(stemmer.stem(w) for w in words)

    print("   Using NLTK PorterStemmer")
except ImportError:
    print("   NLTK not available, using simple text cleaning")

    def stem_text(text: str) -> str:
        return clean_text(text)


# Build composite text_features column
text_columns = []
for col, weight in [
    ("course_title", 2),  # Title is most important — include twice
    ("description", 1),
    ("tag_keyword", 1),
    ("category_name", 1),
    ("sub_category_name", 1),
    ("level", 1),
]:
    if col in df.columns:
        cleaned = df[col].apply(stem_text)
        for _ in range(weight):
            text_columns.append(cleaned)
        print(f"   Added: {col} (weight={weight})")

if text_columns:
    df["text_features"] = text_columns[0]
    for col in text_columns[1:]:
        df["text_features"] = df["text_features"] + " " + col
    print(f"   text_features sample: {df['text_features'].iloc[0][:100]}...")
else:
    print("   ⚠️  No text columns found!")
    df["text_features"] = ""


# ──────────────────────────────────────────────
# Step 6: Handle Missing Values
# ──────────────────────────────────────────────
print("\n🧹 Step 6: Handling missing values...")
nulls_before = df.isnull().sum().sum()
df = df.fillna({"text_features": "", "price": 0, "rating": 0, "reviews": 0, "duration": 0})
for col in df.select_dtypes(include=[np.number]).columns:
    df[col] = df[col].fillna(0)
nulls_after = df.isnull().sum().sum()
print(f"   Nulls: {nulls_before} → {nulls_after}")


# ──────────────────────────────────────────────
# Step 7: Remove Duplicates
# ──────────────────────────────────────────────
print("\n🔄 Step 7: Removing duplicates...")
n_before = len(df)
if "course_id" in df.columns:
    df = df.drop_duplicates(subset=["course_id"], keep="first")
    original_df = original_df.loc[df.index]
n_after = len(df)
print(f"   Rows: {n_before} → {n_after} (removed {n_before - n_after})")

# Reset index
df = df.reset_index(drop=True)
original_df = original_df.reset_index(drop=True)


# ──────────────────────────────────────────────
# Step 8: Save Processed Data
# ──────────────────────────────────────────────
print("\n💾 Step 8: Saving processed DataFrames...")
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

df.to_pickle(COURSE_DATA_PKL)
print(f"   ✅ course_data.pkl ({COURSE_DATA_PKL.stat().st_size / 1e6:.1f} MB)")

original_df.to_pickle(COURSE_DATA_ORIGINAL_PKL)
print(f"   ✅ course_data_original.pkl ({COURSE_DATA_ORIGINAL_PKL.stat().st_size / 1e6:.1f} MB)")

print(f"\n✅ Feature Engineering Complete!")
print(f"   {len(df)} courses processed")
print(f"   Next: Run 'python notebooks/03_model_training.py'")
