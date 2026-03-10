"""
03_model_training.py — Model Training & Artifact Export

This script builds the recommendation models with the CORRECT approach:
1. SEPARATE similarity matrices for text and numerical features
2. StandardScaler on numerical features BEFORE cosine similarity
3. Weighted hybrid: 0.7 * text_similarity + 0.3 * num_similarity
4. Sparse top-K index for deployment (~99% size reduction)
5. Weighted combined features for KNN

Run from project root:
    python notebooks/03_model_training.py

Prerequisites:
    - data/processed/course_data.pkl must exist
    - data/processed/course_data_original.pkl must exist
    (These are created by the feature engineering notebook/script)
"""

import os
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

# ──────────────────────────────────────────────
# Setup
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import (
    COMBINED_FEATURES_PKL,
    COURSE_DATA_ORIGINAL_PKL,
    COURSE_DATA_PKL,
    PROCESSED_DATA_DIR,
    SIMILARITY_TOP_K,
    SIMILARITY_TOPK_PKL,
    TFIDF_MATRIX_PKL,
    TFIDF_VECTORIZER_PKL,
)

# Weights for hybrid similarity
W_TEXT = 0.7
W_NUM = 0.3

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("MODEL TRAINING — Course Recommendation System")
print(f"Weights: text={W_TEXT}, numerical={W_NUM}")
print(f"Top-K: {SIMILARITY_TOP_K}")
print("=" * 60)


# ──────────────────────────────────────────────
# Step 1: Load Data
# ──────────────────────────────────────────────
print("\n📂 Step 1: Loading data...")
df = pd.read_pickle(COURSE_DATA_PKL)
original_df = pd.read_pickle(COURSE_DATA_ORIGINAL_PKL)
print(f"   Loaded {len(df)} courses")
print(f"   Columns: {list(df.columns)}")


# ──────────────────────────────────────────────
# Step 2: Build Text Features & TF-IDF Matrix
# ──────────────────────────────────────────────
print("\n📝 Step 2: Building TF-IDF text features...")

# Construct text_features column if not present
if "text_features" not in df.columns:
    print("   Building text_features from available columns...")

    text_parts = []

    # Course title (important — add twice for emphasis)
    if "course_title" in df.columns:
        text_parts.append(df["course_title"].fillna("").astype(str))
        text_parts.append(df["course_title"].fillna("").astype(str))

    # Description (most important text signal)
    if "description" in df.columns:
        text_parts.append(df["description"].fillna("").astype(str))
    elif "description_stemmed" in df.columns:
        text_parts.append(df["description_stemmed"].fillna("").astype(str))

    # Tags / keywords
    if "tag_keyword" in df.columns:
        text_parts.append(df["tag_keyword"].fillna("").astype(str))
    elif "tag_keyword_stemmed" in df.columns:
        text_parts.append(df["tag_keyword_stemmed"].fillna("").astype(str))

    # Category and subcategory
    for col in ["category_name", "sub_category_name", "level"]:
        if col in df.columns:
            text_parts.append(df[col].fillna("").astype(str))

    df["text_features"] = text_parts[0]
    for part in text_parts[1:]:
        df["text_features"] = df["text_features"] + " " + part

    print(f"   Built text_features from {len(text_parts)} columns")

texts = df["text_features"].fillna("").values

tfidf = TfidfVectorizer(
    max_features=5000,
    stop_words="english",
    ngram_range=(1, 2),  # Unigrams + bigrams for better matching
    min_df=2,            # Ignore very rare terms
    max_df=0.95,         # Ignore very common terms
)
tfidf_matrix = tfidf.fit_transform(texts)
print(f"   TF-IDF matrix shape: {tfidf_matrix.shape}")


# ──────────────────────────────────────────────
# Step 3: Text Similarity Matrix
# ──────────────────────────────────────────────
print("\n📊 Step 3: Computing TEXT similarity matrix...")
t0 = time.time()
similarity_text = cosine_similarity(tfidf_matrix)
print(f"   Shape: {similarity_text.shape}")
print(f"   Time: {time.time() - t0:.1f}s")
print(f"   Mean: {np.mean(similarity_text):.4f}")
print(f"   Median: {np.median(similarity_text):.4f}")


# ──────────────────────────────────────────────
# Step 4: Numerical Similarity Matrix (NORMALIZED!)
# ──────────────────────────────────────────────
print("\n🔢 Step 4: Computing NUMERICAL similarity matrix (with StandardScaler)...")

# Identify available numerical columns
possible_num_cols = ["price", "rating", "reviews", "duration", "is_paid", "number_of_subscribers"]
num_cols = [c for c in possible_num_cols if c in df.columns]
print(f"   Using columns: {num_cols}")

num_data = df[num_cols].copy()

# ── Fix price: remove currency symbols ──
if "price" in num_data.columns:
    num_data["price"] = (
        num_data["price"]
        .astype(str)
        .str.replace(r"[£$€,]", "", regex=True)
        .str.strip()
    )
    num_data["price"] = pd.to_numeric(num_data["price"], errors="coerce").fillna(0)

# ── Fix duration: extract hours as float ──
if "duration" in num_data.columns:
    num_data["duration"] = (
        num_data["duration"]
        .astype(str)
        .str.extract(r"([\d.]+)", expand=False)
    )
    num_data["duration"] = pd.to_numeric(num_data["duration"], errors="coerce").fillna(0)

# ── Log-transform subscribers (heavy right skew) ──
if "number_of_subscribers" in num_data.columns:
    num_data["number_of_subscribers"] = np.log1p(
        pd.to_numeric(num_data["number_of_subscribers"], errors="coerce").fillna(0)
    )

# ── Ensure all columns are numeric ──
for col in num_data.columns:
    num_data[col] = pd.to_numeric(num_data[col], errors="coerce").fillna(0)

# ── NORMALIZE with StandardScaler (critical fix!) ──
num_scaler = StandardScaler()
num_scaled = num_scaler.fit_transform(num_data.values)

# Handle any NaN/inf that crept in
num_scaled = np.nan_to_num(num_scaled, nan=0.0, posinf=0.0, neginf=0.0)

print(f"   Scaled shape: {num_scaled.shape}")
print(f"   Scaled means: {np.mean(num_scaled, axis=0).round(4)}")  # Should be ~0
print(f"   Scaled stds:  {np.std(num_scaled, axis=0).round(4)}")   # Should be ~1

t0 = time.time()
similarity_num = cosine_similarity(num_scaled)
print(f"   Numerical similarity shape: {similarity_num.shape}")
print(f"   Time: {time.time() - t0:.1f}s")
print(f"   Mean: {np.mean(similarity_num):.4f}")
print(f"   Median: {np.median(similarity_num):.4f}")

# ── Verify normalization helped ──
if np.mean(similarity_num) > 0.8:
    print("   ⚠️  WARNING: Mean numerical similarity still very high.")
    print("      This may indicate insufficient feature variance.")
else:
    print("   ✅ Numerical similarity looks properly distributed.")


# ──────────────────────────────────────────────
# Step 5: Weighted Hybrid Similarity
# ──────────────────────────────────────────────
print(f"\n⚖️  Step 5: Computing HYBRID similarity (text={W_TEXT}, num={W_NUM})...")

assert similarity_text.shape == similarity_num.shape, \
    f"Shape mismatch: text={similarity_text.shape}, num={similarity_num.shape}"

similarity_hybrid = W_TEXT * similarity_text + W_NUM * similarity_num

print(f"   Hybrid shape: {similarity_hybrid.shape}")
print(f"   Mean: {np.mean(similarity_hybrid):.4f}")
print(f"   Median: {np.median(similarity_hybrid):.4f}")
print(f"   Max (non-self): {np.max(similarity_hybrid - np.eye(len(similarity_hybrid))):.4f}")


# ──────────────────────────────────────────────
# Step 6: Sparse Top-K Index
# ──────────────────────────────────────────────
print(f"\n💾 Step 6: Creating sparse top-{SIMILARITY_TOP_K} index...")
n_courses = similarity_hybrid.shape[0]
topk_dict = {}

for i in range(n_courses):
    if i % 5000 == 0:
        print(f"   Processing {i}/{n_courses} ({i/n_courses*100:.1f}%)")

    row = similarity_hybrid[i].copy()
    row[i] = -np.inf  # Exclude self
    top_indices = np.argsort(row)[-SIMILARITY_TOP_K:][::-1]
    topk_dict[i] = [
        (int(idx), float(row[idx]))
        for idx in top_indices
    ]

print(f"   Created index for {len(topk_dict)} courses × {SIMILARITY_TOP_K} neighbors")


# ──────────────────────────────────────────────
# Step 7: Weighted Combined Features for KNN
# ──────────────────────────────────────────────
print("\n🧪 Step 7: Building weighted combined features for KNN...")

tfidf_dense = tfidf_matrix.toarray()
combined_features = np.hstack([
    tfidf_dense * W_TEXT,   # Weight text features
    num_scaled * W_NUM,     # Weight numerical features
])

# Handle NaN/inf
combined_features = np.nan_to_num(combined_features, nan=0.0, posinf=0.0, neginf=0.0)

print(f"   Combined features shape: {combined_features.shape}")
print(f"   (TF-IDF: {tfidf_dense.shape[1]} cols × {W_TEXT} + Numeric: {num_scaled.shape[1]} cols × {W_NUM})")


# ──────────────────────────────────────────────
# Step 8: Save All Artifacts
# ──────────────────────────────────────────────
print("\n💾 Step 8: Saving artifacts...")

artifacts = {
    SIMILARITY_TOPK_PKL: topk_dict,
    TFIDF_VECTORIZER_PKL: tfidf,
    TFIDF_MATRIX_PKL: tfidf_matrix,
    COMBINED_FEATURES_PKL: combined_features,
    PROCESSED_DATA_DIR / "num_scaler.pkl": num_scaler,
}

for path, obj in artifacts.items():
    with open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    size_mb = Path(path).stat().st_size / (1024 * 1024)
    print(f"   ✅ {Path(path).name} ({size_mb:.2f} MB)")


# ──────────────────────────────────────────────
# Step 9: Validation
# ──────────────────────────────────────────────
print("\n🔍 Step 9: Validation — Spot-checking recommendations...")

# Pick a few courses and check if recommendations make sense
test_indices = [0, 100, 5000, 10000]
display_cols = [c for c in ["course_title", "category_name", "sub_category_name", "rating"]
                if c in original_df.columns]

for idx in test_indices:
    if idx >= len(original_df):
        continue
    print(f"\n   Base: {original_df.iloc[idx].get('course_title', 'N/A')}")
    if "category_name" in original_df.columns:
        print(f"   Category: {original_df.iloc[idx].get('category_name', 'N/A')}")
    recs = topk_dict[idx][:3]
    for rec_idx, score in recs:
        title = original_df.iloc[rec_idx].get("course_title", "N/A")
        cat = original_df.iloc[rec_idx].get("category_name", "")
        print(f"     → [{score:.4f}] {title} ({cat})")


print("\n" + "=" * 60)
print("✅ MODEL TRAINING COMPLETE!")
print(f"   Artifacts saved to: {PROCESSED_DATA_DIR}")
print(f"   Top-K index: {SIMILARITY_TOP_K} neighbors per course")
print(f"   Weights: text={W_TEXT}, numerical={W_NUM}")
print("=" * 60)
