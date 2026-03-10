"""
01_eda.py — Exploratory Data Analysis

Quick data profiling and visualization of the Udemy course dataset.

Run from project root:
    python notebooks/01_eda.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import RAW_DATA_DIR

print("=" * 60)
print("EXPLORATORY DATA ANALYSIS — Udemy Courses")
print("=" * 60)

# ── Load Data ──
csv_path = RAW_DATA_DIR / "udemy.csv"
if not csv_path.exists():
    print(f"❌ File not found: {csv_path}")
    print("   Run scripts/organize_files.py first.")
    sys.exit(1)

df = pd.read_csv(csv_path)
print(f"\n📊 Dataset shape: {df.shape}")
print(f"   Rows: {df.shape[0]:,}")
print(f"   Columns: {df.shape[1]}")

# ── Column Info ──
print(f"\n📋 Columns:")
for col in df.columns:
    dtype = df[col].dtype
    nulls = df[col].isnull().sum()
    nunique = df[col].nunique()
    print(f"   {col:30s} | {str(dtype):10s} | nulls: {nulls:5d} | unique: {nunique:6d}")

# ── Basic Statistics ──
print(f"\n📈 Numeric Statistics:")
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if numeric_cols:
    print(df[numeric_cols].describe().round(2).to_string())
else:
    print("   No purely numeric columns found (may need parsing)")

# ── Rating Distribution ──
if "rating" in df.columns:
    ratings = pd.to_numeric(df["rating"], errors="coerce").dropna()
    print(f"\n⭐ Rating Distribution:")
    print(f"   Mean: {ratings.mean():.2f}")
    print(f"   Median: {ratings.median():.2f}")
    print(f"   Std: {ratings.std():.2f}")
    print(f"   Min: {ratings.min():.2f}, Max: {ratings.max():.2f}")
    print(f"   Zero ratings: {(ratings == 0).sum()} ({(ratings == 0).mean()*100:.1f}%)")

# ── Price Analysis ──
if "price" in df.columns:
    prices = df["price"].astype(str).str.replace(r"[£$€,]", "", regex=True)
    prices = pd.to_numeric(prices, errors="coerce").dropna()
    print(f"\n💰 Price Distribution:")
    print(f"   Mean: {prices.mean():.2f}")
    print(f"   Median: {prices.median():.2f}")
    print(f"   Free courses: {(prices == 0).sum()} ({(prices == 0).mean()*100:.1f}%)")
    print(f"   Max: {prices.max():.2f}")

# ── Category Distribution ──
for cat_col in ["category_name", "sub_category_name"]:
    if cat_col in df.columns:
        print(f"\n📁 {cat_col} — Top 10:")
        for cat, count in df[cat_col].value_counts().head(10).items():
            print(f"   {cat:40s} | {count:5d}")

# ── Missing Values Summary ──
missing = df.isnull().sum()
if missing.any():
    print(f"\n⚠️  Missing Values:")
    for col in missing[missing > 0].index:
        pct = missing[col] / len(df) * 100
        print(f"   {col:30s} | {missing[col]:5d} ({pct:.1f}%)")

# ── Data Quality Issues ──
print(f"\n🔍 Data Quality Checks:")
if "duration" in df.columns:
    non_numeric_duration = df["duration"].astype(str).str.contains(r"[a-zA-Z]", na=False).sum()
    print(f"   Duration with text: {non_numeric_duration} (needs parsing)")

if "number_of_subscribers" in df.columns:
    subs = pd.to_numeric(df["number_of_subscribers"], errors="coerce").dropna()
    print(f"   Subscribers — Skewness: {subs.skew():.2f} (needs log-transform if > 2)")
    print(f"   Subscribers — Max: {subs.max():,.0f}")

print(f"\n✅ EDA Complete!")
