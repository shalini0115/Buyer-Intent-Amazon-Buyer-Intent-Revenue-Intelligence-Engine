"""
data_loader.py — Single source of truth for all data
All transformations happen here; pages receive clean DataFrames.
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
SEG_MAP = {
    0: "DEAL_SEEKER",
    1: "NICHE_EXPLORER",
    2: "QUALITY_FIRST",
    3: "SOCIAL_PROOF",
    4: "UNMATCHED",
}

# features_final.csv top_cat_code → readable label
CAT_MAP = {
    0: "Electronics",
    1: "Computers",
    2: "Home & Kitchen",
    3: "Accessories",
    4: "Audio",
    5: "Mobiles",
    6: "Cameras",
    7: "Networking",
    8: "Storage",
}

# Segment classification weights (from segmentation_explainer.md)
SEG_WEIGHTS = {
    "DEAL_SEEKER":    1.2,
    "QUALITY_FIRST":  1.4,
    "SOCIAL_PROOF":   1.1,
    "NICHE_EXPLORER": 1.0,
}

# Key features per segment for DNA analysis
SEG_FEATURES = {
    "DEAL_SEEKER":    ["savings_ratio", "discount_pct", "price_savings",
                       "price_percentile", "trust_score"],
    "QUALITY_FIRST":  ["rating", "trust_score", "review_percentile",
                       "savings_ratio", "social_proof_score"],
    "SOCIAL_PROOF":   ["review_log", "social_proof_score", "trust_score",
                       "rating", "high_review_flag"],
    "NICHE_EXPLORER": ["category_depth", "review_percentile", "word_count",
                       "keyword_density", "about_length"],
}

# Radar chart features (normalized 0–1) for Buyer DNA
RADAR_FEATURES = {
    "Savings Signal":  "savings_ratio",
    "Rating Quality":  "rating",
    "Trust Score":     "trust_score",
    "Review Depth":    "review_log",
    "Listing Richness":"keyword_density",
}

# category-relative Q75 for SOCIAL_PROOF (precomputed from full dataset)
# Used in what-if engine
CAT_Q75_REVIEWS = {
    "Accessories":   3663.0,
    "Audio":         7249.0,
    "Cameras":      56552.0,
    "Computers":    20053.0,
    "Electronics":   1118.0,
    "Home & Kitchen": 27970.0,
    "Mobiles":       5134.0,
    "Networking":    6368.0,
    "Storage":      15867.0,
}

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOADER
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_all(data_dir: str = "data") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
        features  — full 1463-row feature frame with derived cols
        impact    — 350-row customer impact frame merged with feature scores
    """
    base = Path(data_dir)

    # ── 1. features_final.csv ────────────────────────────────────────────────
    feat = pd.read_csv(base / "features_final.csv")

    # Readable labels
    feat["segment"]  = feat["segment_code"].map(SEG_MAP).fillna("UNMATCHED")
    feat["top_cat"]  = feat["top_cat_code"].map(CAT_MAP).fillna("Electronics")

    # ── Price-tier label ──────────────────────────────────────────────────────
    tier_map = {0: "Budget", 1: "Mid-Range", 2: "Premium", 3: "Luxury"}
    feat["price_tier"] = feat["price_tier_code"].map(tier_map).fillna("Mid-Range")

    # ── Revenue estimates (mirror customer_impact.csv logic) ──────────────────
    # monthly_volume ≈ rating_count / 12  (proxy for sales velocity)
    feat["monthly_volume"]   = feat["rating_count"] / 12
    feat["revenue_baseline"] = feat["monthly_volume"] * feat["price_disc"]

    # uplift_rate: 38% for high-potential, 5% for placement-locked DEAL_SEEKERs
    def _uplift_rate(row):
        if row["segment"] == "QUALITY_FIRST":  return 0.38
        if row["segment"] == "SOCIAL_PROOF":   return 0.38
        if row["segment"] == "NICHE_EXPLORER":  return 0.25
        if row["segment"] == "DEAL_SEEKER":     return 0.05
        return 0.10  # UNMATCHED

    feat["uplift_rate"]     = feat.apply(_uplift_rate, axis=1)
    feat["revenue_uplift"]  = feat["revenue_baseline"] * feat["uplift_rate"]

    # ── Mismatch flag ─────────────────────────────────────────────────────────
    # A product is misplaced if DEAL_SEEKER with high savings_ratio
    # AND could qualify for a better segment
    feat["mismatch_flag"] = (
        (feat["segment"] == "DEAL_SEEKER") &
        (feat["savings_ratio"] > 0.60) &
        (feat["rating"] >= 4.0)
    ).astype(int)

    # Also flag UNMATCHED with high trust scores (missed QUALITY_FIRST)
    feat.loc[
        (feat["segment"] == "UNMATCHED") &
        (feat["trust_score"] > 3.0) &
        (feat["rating"] >= 4.1),
        "mismatch_flag"
    ] = 1

    feat["mismatch_revenue_loss"] = np.where(
        feat["mismatch_flag"] == 1,
        feat["revenue_baseline"] * 0.15,
        0.0,
    )

    # ── Inferred placement ─────────────────────────────────────────────────────
    feat["inferred_placement"] = np.where(
        feat["discount_pct"] > 40, "DEAL_TIER", "QUALITY_TIER"
    )

    # ── Segment score normalised (0-1 for radar) ──────────────────────────────
    score_cols = ["score_DEAL_SEEKER", "score_QUALITY_FIRST",
                  "score_SOCIAL_PROOF", "score_NICHE_EXPLORER"]
    for c in score_cols:
        mx = feat[c].max()
        feat[f"{c}_norm"] = feat[c] / mx if mx > 0 else 0.0

    # ── TFIDF group: top keyword per row ──────────────────────────────────────
    tfidf_cols = [c for c in feat.columns if c.startswith("tfidf_")]
    feat["top_keyword"] = feat[tfidf_cols].idxmax(axis=1).str.replace("tfidf_", "", regex=False)

    # ── Composite scores ──────────────────────────────────────────────────────
    feat["quality_composite"] = (
        feat["rating"].clip(0, 5) / 5 * 0.40 +
        feat["trust_score"].clip(0, 5) / 5 * 0.35 +
        feat["review_percentile"].clip(0, 1) * 0.25
    ).round(4)

    feat["deal_strength"] = (
        feat["savings_ratio"].clip(0, 1) * 0.60 +
        feat["discount_pct"].clip(0, 100) / 100 * 0.40
    ).round(4)

    feat["social_strength"] = (
        feat["review_log"].clip(0, 15) / 15 * 0.50 +
        feat["social_proof_score"].clip(0, 5) / 5 * 0.30 +
        feat["high_review_flag"] * 0.20
    ).round(4)

    # ── 2. customer_impact.csv ────────────────────────────────────────────────
    imp = pd.read_csv(base / "customer_impact.csv")

    # Merge feature scores into impact for enriched views
    feat_cols = ["product_id", "rating", "discount_pct", "trust_score",
                 "savings_ratio", "review_log", "social_proof_score",
                 "category_depth", "word_count", "review_percentile",
                 "keyword_density", "quality_composite", "deal_strength",
                 "social_strength", "segment",
                 "score_DEAL_SEEKER", "score_QUALITY_FIRST",
                 "score_SOCIAL_PROOF", "score_NICHE_EXPLORER",
                 "top_keyword", "price_tier"]

    imp = imp.merge(
        feat[feat_cols].drop_duplicates("product_id"),
        on="product_id", how="left"
    )

    # Resolve duplicate cols (_x/_y)
    for col in list(imp.columns):
        if col.endswith("_x"):
            base_col = col[:-2]
            imp = imp.rename(columns={col: base_col})
            if f"{base_col}_y" in imp.columns:
                imp = imp.drop(columns=[f"{base_col}_y"])

    imp = imp.loc[:, ~imp.columns.duplicated(keep="first")]

    # Clean segment label
    if "pred_segment" in imp.columns:
        imp["segment"] = imp["pred_segment"]

    return feat, imp


# ─────────────────────────────────────────────────────────────────────────────
# SHAP SUMMARY LOADER (optional — only if shap_summary.csv exists)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_shap(data_dir: str = "data") -> pd.DataFrame | None:
    path = Path(data_dir) / "shap_summary.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# FILTERED VIEW HELPER
# ─────────────────────────────────────────────────────────────────────────────
def apply_filters(
    df: pd.DataFrame,
    sel_cats: list[str],
    sel_segs: list[str],
    cat_col: str = "top_cat",
    seg_col: str = "segment",
) -> pd.DataFrame:
    mask = pd.Series([True] * len(df), index=df.index)
    if sel_cats:
        mask &= df[cat_col].isin(sel_cats)
    if sel_segs:
        mask &= df[seg_col].isin(sel_segs)
    return df[mask].copy()


# ─────────────────────────────────────────────────────────────────────────────
# AGGREGATE HELPERS (used across multiple pages)
# ─────────────────────────────────────────────────────────────────────────────
def seg_counts(df: pd.DataFrame, col: str = "segment") -> pd.Series:
    return df[col].value_counts()


def revenue_by_seg(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("segment")
        .agg(
            products=("product_id", "count"),
            total_uplift=("revenue_uplift", "sum"),
            mean_uplift=("revenue_uplift", "mean"),
            total_leakage=("mismatch_revenue_loss", "sum"),
        )
        .round(0)
        .reset_index()
    )


def category_stats(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("top_cat")
        .agg(
            products=("product_id", "count"),
            mismatch_rate=("mismatch_flag", "mean"),
            mean_rating=("rating", "mean"),
            mean_discount=("discount_pct", "mean"),
            total_uplift=("revenue_uplift", "sum"),
        )
        .round(3)
        .reset_index()
    )
