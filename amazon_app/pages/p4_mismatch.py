"""
p4_mismatch.py — Mismatch Alerts
SHAP-diagnosed misplaced products, leakage banners, alert cards, pagination.
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.style import (
    page_header, sec_div, kpi_card, alert_card, fmt_inr, SEG_COLORS,
)
from utils.charts import mismatch_rate_bar, mismatch_scatter, leakage_projection


def _fallback_push_barrier(row):
    """Heuristic push/barrier when shap_df is unavailable."""
    seg = str(row.get("segment", row.get("pred_segment", "DEAL_SEEKER")))

    if seg == "DEAL_SEEKER":
        push_feat    = "savings_ratio"
        push_val     = float(row.get("savings_ratio", 0.55))
        barrier_feat = "rating"
        barrier_val  = float(row.get("rating", 3.8)) - 4.3  # negative = below threshold
    elif seg == "SOCIAL_PROOF":
        push_feat    = "review_log"
        push_val     = float(row.get("review_log", 8.0))
        barrier_feat = "trust_score"
        barrier_val  = float(row.get("trust_score", 2.5)) - 3.5
    elif seg == "QUALITY_FIRST":
        push_feat    = "trust_score"
        push_val     = float(row.get("trust_score", 3.2))
        barrier_feat = "discount_pct"
        barrier_val  = -(float(row.get("discount_pct", 40)) - 35)  # negative = too high
    else:
        push_feat    = "savings_ratio"
        push_val     = float(row.get("savings_ratio", 0.5))
        barrier_feat = "rating"
        barrier_val  = float(row.get("rating", 3.5)) - 4.3

    return push_feat, push_val, barrier_feat, barrier_val


def _fallback_recommendation(row):
    seg       = str(row.get("segment", row.get("pred_segment", "DEAL_SEEKER")))
    discount  = float(row.get("discount_pct", 50))
    rating    = float(row.get("rating", 3.8))
    savings   = float(row.get("savings_ratio", 0.5))
    rc        = int(row.get("rating_count", 100))

    if seg == "DEAL_SEEKER" and rating >= 4.0:
        return (
            f"Reduce discount from {discount:.0f}% to below 35% — rating {rating:.1f}★ qualifies "
            f"for QUALITY_FIRST tier (1.4× revenue weight). Do NOT over-discount a quality product."
        )
    elif seg == "DEAL_SEEKER":
        return (
            f"Improve rating from {rating:.1f}★ to ≥ 4.3★ and reduce discount to <35% to "
            f"unlock QUALITY_FIRST classification and higher revenue uplift."
        )
    elif seg == "SOCIAL_PROOF":
        return (
            f"Product has strong review volume — ensure rating stays ≥ 4.0★ (currently {rating:.1f}★) "
            f"and reduce reliance on deep discounting to attract quality-focused buyers."
        )
    else:
        return (
            f"Review listing completeness: improve trust_score via A+ content, brand story, "
            f"warranty details. Target QUALITY_FIRST tier with rating ≥ 4.3★ and discount <35%."
        )


def render(feat, imp, filtered_feat, filtered_imp, shap_df):

    st.markdown('<div class="cw">', unsafe_allow_html=True)
    st.markdown(
        page_header(
            "04 / Mismatch Intelligence",
            "Mismatch Alerts",
            "SHAP-diagnosed products where buyer intent misaligns with placement tier.",
        ),
        unsafe_allow_html=True,
    )

    # ── Leakage stats ─────────────────────────────────────────────────────────
    mm_df       = filtered_imp[filtered_imp["mismatch_flag"] == 1].copy()
    total_loss  = filtered_feat["mismatch_revenue_loss"].sum()
    n_mm        = int(filtered_feat["mismatch_flag"].sum())
    avg_loss    = total_loss / n_mm if n_mm else 0
    mismatch_rt = n_mm / len(filtered_feat) * 100 if len(filtered_feat) else 0

    # ── Leakage banner ────────────────────────────────────────────────────────
    col_ban_l, col_ban_r = st.columns([1.3, 1])
    with col_ban_l:
        st.markdown(f"""
        <div class="leakage-banner" style="margin:0 0 20px;">
          <div class="lb-left">
            <div class="lb-eyebrow">⚡ REVENUE LEAKAGE IDENTIFIED</div>
            <div class="lb-amount">{fmt_inr(total_loss)}</div>
            <div class="lb-desc">monthly loss from {n_mm:,} misplaced products</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col_ban_r:
        st.plotly_chart(leakage_projection(total_loss, n_months=12, height=120),
                        use_container_width=True)

    # ── 4 KPI cards ───────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Misplaced Products", f"{n_mm:,}", "flagged by ML model", "red"),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Total Leakage", fmt_inr(total_loss), "monthly", "red"),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Avg Loss / Product", fmt_inr(avg_loss), "per misplaced product", "orange"),
                    unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Mismatch Rate", f"{mismatch_rt:.1f}%", "of products in view", "purple"),
                    unsafe_allow_html=True)

    # ── ROW 1 ─────────────────────────────────────────────────────────────────
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown(sec_div("Mismatch Rate by Category"), unsafe_allow_html=True)
        st.plotly_chart(mismatch_rate_bar(filtered_feat), use_container_width=True)
    with col_b:
        st.markdown(sec_div("Discount % vs Rating — Mismatch Pattern"), unsafe_allow_html=True)
        st.plotly_chart(mismatch_scatter(filtered_feat), use_container_width=True)

    # ── Alert cards section ───────────────────────────────────────────────────
    st.markdown(sec_div("⚡ SHAP-Diagnosed Mismatch Cases — Sorted by Revenue Impact"),
                unsafe_allow_html=True)

    # Source: filtered_imp where mismatch_flag == 1
    source_df = filtered_imp[filtered_imp["mismatch_flag"] == 1].copy()
    if "mismatch_revenue_loss" not in source_df.columns:
        source_df = source_df.merge(
            filtered_feat[["product_id", "mismatch_revenue_loss"]].drop_duplicates("product_id"),
            on="product_id", how="left",
        )
    source_df = source_df.sort_values("mismatch_revenue_loss", ascending=False)

    if source_df.empty:
        st.info("No mismatch cases in current filter. Adjust category/segment filters.")
    else:
        # Pagination
        PAGE_SIZE = 5
        n_pages   = max(1, int(np.ceil(len(source_df) / PAGE_SIZE)))
        page_num  = st.selectbox(
            f"Page — showing 5 per page ({len(source_df)} total mismatches)",
            range(1, n_pages + 1),
            format_func=lambda p: f"Page {p} of {n_pages}",
        )
        start = (page_num - 1) * PAGE_SIZE
        page_rows = source_df.iloc[start: start + PAGE_SIZE]

        seg_col = "pred_segment" if "pred_segment" in page_rows.columns else "segment"

        for _, row in page_rows.iterrows():
            seg   = str(row.get(seg_col, "UNMATCHED"))
            name  = str(row.get("product_name", str(row.get("product_id", "Unknown"))))
            loss  = float(row.get("mismatch_revenue_loss", 0))
            disc  = float(row.get("discount_pct", 0))
            sav   = float(row.get("savings_ratio", 0))
            trust = float(row.get("trust_score", 0))
            rat   = float(row.get("rating", 0))

            # Push / barrier
            if (shap_df is not None and
                    "product_id" in shap_df.columns and
                    row["product_id"] in shap_df["product_id"].values):
                sr = shap_df[shap_df["product_id"] == row["product_id"]].iloc[0]
                push_feat    = str(sr.get("shap_push", "savings_ratio"))
                push_val     = float(sr.get("shap_push_val", 0.3))
                barrier_feat = str(sr.get("shap_barrier", "rating"))
                barrier_val  = float(sr.get("shap_barrier_val", -0.2))
                rec          = str(sr.get("recommendation_text", _fallback_recommendation(row)))
            else:
                push_feat, push_val, barrier_feat, barrier_val = _fallback_push_barrier(row)
                rec = _fallback_recommendation(row)

            st.markdown(
                alert_card(name, loss, seg, disc, sav, trust, rat,
                           push_feat, push_val, barrier_feat, barrier_val, rec),
                unsafe_allow_html=True,
            )

    # ── Bottom sortable table ─────────────────────────────────────────────────
    st.markdown(sec_div("Top 20 Mismatch Cases — Full Details"), unsafe_allow_html=True)

    top20 = filtered_imp[filtered_imp["mismatch_flag"] == 1].sort_values(
        "mismatch_revenue_loss", ascending=False
    ).head(20)

    seg_col = "pred_segment" if "pred_segment" in top20.columns else "segment"
    rows = []
    for _, r in top20.iterrows():
        rows.append({
            "Product":      str(r.get("product_name", r.get("product_id", "")))[:55],
            "Category":     str(r.get("top_cat", "—")),
            "Segment":      str(r.get(seg_col, "—")),
            "Discount":     f"{r.get('discount_pct', 0):.0f}%",
            "Rating":       f"{r.get('rating', 0):.1f}★",
            "Trust":        f"{r.get('trust_score', 0):.2f}",
            "Monthly Loss": fmt_inr(r.get("mismatch_revenue_loss", 0)),
            "Action":       "Reduce discount" if r.get("discount_pct", 0) > 35 else "Improve rating",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)