"""
ml_utils.py — What-if simulator engine for p6_product.py
Rule-based segment scoring, prediction, success probability, seller actions.
"""

import numpy as np
import pandas as pd
from utils.data_loader import CAT_Q75_REVIEWS

# ─────────────────────────────────────────────────────────────────────────────
# SEGMENT CLASSIFICATION RULES
# ─────────────────────────────────────────────────────────────────────────────
SEG_WEIGHTS = {
    "DEAL_SEEKER":    1.2,
    "QUALITY_FIRST":  1.4,
    "SOCIAL_PROOF":   1.1,
    "NICHE_EXPLORER": 1.0,
    "UNMATCHED":      0.0,
}


def _sigmoid(x: float) -> float:
    """Numerically stable sigmoid."""
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))


def compute_segment_scores(
    rating: float,
    discount_pct: float,
    rating_count: int,
    category: str,
    savings_ratio: float,
    category_depth: int,
    trust_score: float,
) -> dict[str, float]:
    """
    Returns raw score for each segment using the 4 classification rules.
    Scores = segment weight if rule fires, else 0.0.
    Multiple may fire — caller picks argmax via predict_segment().
    """
    scores: dict[str, float] = {
        "DEAL_SEEKER":    0.0,
        "QUALITY_FIRST":  0.0,
        "SOCIAL_PROOF":   0.0,
        "NICHE_EXPLORER": 0.0,
    }

    # DEAL_SEEKER: discount_pct > 45 AND rating >= 3.8
    if discount_pct > 45 and rating >= 3.8:
        scores["DEAL_SEEKER"] = 1.2

    # QUALITY_FIRST: rating >= 4.3 AND rating_count >= 500 AND discount_pct < 35
    if rating >= 4.3 and rating_count >= 500 and discount_pct < 35:
        scores["QUALITY_FIRST"] = 1.4

    # SOCIAL_PROOF: rating_count > CAT_Q75[cat] AND rating >= 4.0
    cat_q75 = CAT_Q75_REVIEWS.get(category, 5000.0)
    if rating_count > cat_q75 and rating >= 4.0:
        scores["SOCIAL_PROOF"] = 1.1

    # NICHE_EXPLORER: rating >= 4.2 AND rating_count < 200 AND category_depth >= 2
    if rating >= 4.2 and rating_count < 200 and category_depth >= 2:
        scores["NICHE_EXPLORER"] = 1.0

    return scores


def predict_segment(scores: dict[str, float]) -> str:
    """
    Returns segment with highest score.
    Returns 'UNMATCHED' if all scores are 0.
    Conflict resolution: highest weighted score wins.
    """
    if not scores or all(v == 0.0 for v in scores.values()):
        return "UNMATCHED"
    return max(scores, key=scores.get)


def compute_success_probability(
    rating: float,
    discount_pct: float,
    rating_count: int,
    savings_ratio: float,
    trust_score: float,
    target_seg: str = "QUALITY_FIRST",
) -> float:
    """
    Returns 0.0–1.0 probability of qualifying for target_seg.
    Uses rule-based sigmoid: normalized distance to each threshold.
    """
    if target_seg == "QUALITY_FIRST":
        # Three conditions: rating >= 4.3, rating_count >= 500, discount_pct < 35
        p_rating   = _sigmoid(6.0 * (rating - 4.3) / 0.7)
        p_reviews  = _sigmoid(6.0 * (rating_count - 500) / 500)
        p_discount = _sigmoid(6.0 * (35 - discount_pct) / 15)
        # Trust score bonus (soft signal)
        p_trust    = _sigmoid(4.0 * (trust_score - 3.0) / 1.5)
        # Geometric mean of the 3 hard conditions × trust boost
        p = (p_rating * p_reviews * p_discount) ** (1 / 3) * (0.8 + 0.2 * p_trust)
        return float(np.clip(p, 0.0, 1.0))

    elif target_seg == "DEAL_SEEKER":
        p_discount = _sigmoid(6.0 * (discount_pct - 45) / 15)
        p_rating   = _sigmoid(4.0 * (rating - 3.8) / 0.5)
        return float(np.clip(p_discount * p_rating, 0.0, 1.0))

    elif target_seg == "SOCIAL_PROOF":
        # Soft: high review count + rating >= 4.0
        p_reviews = _sigmoid(5.0 * (rating_count - 5000) / 5000)
        p_rating  = _sigmoid(6.0 * (rating - 4.0) / 0.5)
        return float(np.clip(p_reviews * p_rating, 0.0, 1.0))

    elif target_seg == "NICHE_EXPLORER":
        p_rating  = _sigmoid(6.0 * (rating - 4.2) / 0.4)
        p_reviews = _sigmoid(6.0 * (200 - rating_count) / 100)
        return float(np.clip(p_rating * p_reviews, 0.0, 1.0))

    return 0.0


def generate_seller_actions(
    current_seg: str,
    target_seg: str,
    rating: float,
    discount_pct: float,
    rating_count: int,
    savings_ratio: float,
    trust_score: float,
) -> list[str]:
    """
    Returns 3–5 specific, quantified action strings based on
    current segment and target upgrade path.
    """
    actions: list[str] = []

    # ── Upgrade to QUALITY_FIRST ──────────────────────────────────────────────
    if target_seg == "QUALITY_FIRST" or (current_seg in ("DEAL_SEEKER", "UNMATCHED")
                                          and target_seg != "NICHE_EXPLORER"):
        if discount_pct >= 35:
            gap = discount_pct - 34
            actions.append(
                f"Reduce discount from {discount_pct:.0f}% to below 35% "
                f"(cut {gap:.0f} percentage points) — heavy discounting sends a quality-concern "
                f"signal that repels premium buyers worth 1.4× more revenue."
            )
        else:
            actions.append(
                f"✓ Discount {discount_pct:.0f}% is already below 35% threshold — "
                f"maintain this pricing strategy."
            )

        if rating < 4.3:
            gap = round(4.3 - rating, 1)
            actions.append(
                f"Improve product rating from {rating:.1f}★ to ≥ 4.3★ "
                f"(need +{gap}★) — address top negative review themes, improve packaging "
                f"and post-purchase support to drive organic rating uplift."
            )
        else:
            actions.append(f"✓ Rating {rating:.1f}★ already clears the 4.3★ QUALITY_FIRST threshold.")

        if rating_count < 500:
            need = 500 - rating_count
            actions.append(
                f"Grow review count from {rating_count:,} to 500+ "
                f"(need {need:,} more) — run Amazon Vine program, follow-up email sequence, "
                f"and insert cards encouraging honest reviews."
            )
        else:
            actions.append(
                f"✓ Review count {rating_count:,} already exceeds the 500-review threshold."
            )

        if savings_ratio > 0.35:
            actions.append(
                f"SHAP alert: savings_ratio {savings_ratio:.3f} > 0.35 is a NEGATIVE signal for "
                f"QUALITY_FIRST. Consider reducing price_savings — premium buyers interpret "
                f"deep discounts as a quality red flag, not a value signal."
            )

        if trust_score < 3.5:
            actions.append(
                f"Boost trust score from {trust_score:.2f} to ≥ 3.5 — improve listing completeness, "
                f"add brand story, warranty details, and A+ content to signal product authority."
            )

    # ── Already QUALITY_FIRST ─────────────────────────────────────────────────
    elif current_seg == "QUALITY_FIRST":
        actions.append(
            f"✓ Already in QUALITY_FIRST — highest revenue weight (1.4×). "
            f"Focus on protecting the rating at {rating:.1f}★ and maintaining review velocity."
        )
        actions.append(
            f"Do NOT increase discount beyond 35% — savings_ratio already at {savings_ratio:.3f}. "
            f"SHAP analysis shows discount > 35% reverses QUALITY_FIRST classification."
        )
        actions.append(
            f"Invest in listing richness: A+ content, brand story, high-resolution images "
            f"to deepen conversion without touching price."
        )

    # ── Upgrade to SOCIAL_PROOF ───────────────────────────────────────────────
    elif target_seg == "SOCIAL_PROOF":
        if rating < 4.0:
            actions.append(
                f"Raise rating from {rating:.1f}★ to ≥ 4.0★ (need +{round(4.0-rating,1)}★) — "
                f"SOCIAL_PROOF buyers use rating as a social validation floor."
            )
        if rating_count < 5000:
            actions.append(
                f"Grow review count from {rating_count:,} toward category Q75 threshold — "
                f"run sponsored campaigns to drive volume traffic and review density."
            )
        actions.append(
            "Leverage Amazon's Early Reviewer Program and Vine to accelerate review accumulation."
        )

    # ── Upgrade to NICHE_EXPLORER ─────────────────────────────────────────────
    elif target_seg == "NICHE_EXPLORER":
        actions.append(
            f"Increase listing specificity — word_count and category_depth are the primary SHAP "
            f"drivers. Add technical specs, use-case language, and deep sub-category keywords."
        )
        if rating < 4.2:
            actions.append(
                f"Rating {rating:.1f}★ needs +{round(4.2-rating,1)}★ to clear 4.2★ NICHE threshold."
            )
        actions.append(
            "Keep review count below 200 naturally — niche explorers self-select via listing quality, "
            "not crowd validation. Avoid broad promotional campaigns."
        )

    # ── Generic fallback ──────────────────────────────────────────────────────
    if len(actions) == 0:
        actions = [
            f"Current segment: {current_seg}. Evaluate rating ({rating:.1f}★), "
            f"discount ({discount_pct:.0f}%), and review count ({rating_count:,}) "
            f"against target segment thresholds.",
            "Improve listing quality: title, bullet points, A+ content, and images.",
            "Monitor SHAP feature shifts after each product update via the Product Intelligence page.",
        ]

    return actions[:5]  # cap at 5 actions


def compute_feature_importances(df: pd.DataFrame) -> dict[str, float]:
    """
    Proxy for model feature importance using score correlation.
    Returns dict of feature→importance for top 20 numeric features.
    Computed as abs(correlation of feature with segment_code)
    weighted by segment weight of the dominant class.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    exclude = [
        "segment_code", "top_cat_code", "price_tier_code",
        "score_DEAL_SEEKER", "score_QUALITY_FIRST",
        "score_SOCIAL_PROOF", "score_NICHE_EXPLORER",
        "mismatch_flag", "high_review_flag",
    ]
    # Also exclude derived/computed score cols
    exclude += [c for c in numeric_cols if c.startswith("score_") or c.startswith("tfidf_")]

    feature_cols = [c for c in numeric_cols if c not in exclude]

    if "segment_code" not in df.columns:
        return {}

    target = df["segment_code"].values
    importances: dict[str, float] = {}

    for col in feature_cols:
        vals = df[col].fillna(0).values
        if vals.std() == 0:
            continue
        corr = float(np.corrcoef(vals, target)[0, 1])
        importances[col] = abs(corr)

    # Sort by importance descending, take top 20
    sorted_imp = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True)[:20])
    return sorted_imp