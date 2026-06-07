"""
p6_product.py — Product Intelligence + What-If Simulator
Search any product — decode classification, SHAP drivers, simulate segment upgrades.

UI upgrades (style-only, zero logic changes):
  ✓ Animated KPI cards — count-up · reveal · hover lift · shadow expansion
  ✓ Glow border + number pop + staggered appearance (via p6-kpi-grid CSS)
  ✓ Larger fonts throughout for improved readability
  ✓ Enhanced product card, SHAP cards, action plan, simulator
  ✓ Segment shift pulse animation (p6ShiftPulse)
  ✓ Live delta badges on simulator sliders
  ✓ Enriched quick-stat empty state
"""

import streamlit as st
import pandas as pd
import numpy as np

from utils.style import (
    page_header, sec_div, seg_badge, kpi_card, fmt_inr, SEG_COLORS, SEG_ICONS,
    kpi_card_animated, p6_kpi_grid,
)
from utils.charts import probability_bars, whyif_gauge
from utils.data_loader import SEG_FEATURES
from utils.ml_utils import (
    compute_segment_scores,
    predict_segment,
    compute_success_probability,
    generate_seller_actions,
)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _seg_quick_stats(feat, imp):
    """Enhanced 4 quick-stat cards — shown when search is empty."""
    segs = ["DEAL_SEEKER", "QUALITY_FIRST", "SOCIAL_PROOF", "NICHE_EXPLORER"]
    cols = st.columns(4)
    for i, (col, seg) in enumerate(zip(cols, segs)):
        sub   = feat[feat["segment"] == seg]
        color = SEG_COLORS[seg]
        icon  = SEG_ICONS[seg]
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        with col:
            st.markdown(f"""
            <div class="p6-qs-card"
                 style="border-top:2px solid {color};">
              <div style="font-size:28px;margin-bottom:12px;">{icon}</div>
              <div style="font-family:'Inter',sans-serif;font-size:14px;font-weight:700;
                          color:{color};margin-bottom:14px;letter-spacing:-0.01em;">
                {seg.replace("_"," ")}
              </div>
              <div style="font-family:'Inter',sans-serif;font-size:32px;font-weight:800;
                          color:var(--text-primary);letter-spacing:-0.04em;line-height:1;">
                {len(sub):,}
              </div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                          color:var(--text-faint);text-transform:uppercase;
                          letter-spacing:0.08em;margin:4px 0 14px;">products</div>
              <div style="background:rgba({r},{g},{b},0.07);border:1px solid rgba({r},{g},{b},0.16);
                          border-radius:8px;padding:10px 12px;text-align:left;">
                <div style="font-size:12.5px;color:var(--text-muted);line-height:1.75;">
                  Avg discount
                  <strong style="color:{color};float:right;">{sub['discount_pct'].mean():.1f}%</strong>
                </div>
                <div style="font-size:12.5px;color:var(--text-muted);line-height:1.75;">
                  Avg rating
                  <strong style="color:{color};float:right;">{sub['rating'].mean():.2f}★</strong>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)


def _heuristic_shap(feat_row, seg):
    """Derive push/barrier heuristically when shap_df unavailable."""
    push_candidates = {
        "DEAL_SEEKER":    ("savings_ratio",  feat_row.get("savings_ratio", 0),  +1),
        "QUALITY_FIRST":  ("trust_score",    feat_row.get("trust_score", 0),    +1),
        "SOCIAL_PROOF":   ("review_log",     feat_row.get("review_log", 0),     +1),
        "NICHE_EXPLORER": ("category_depth", feat_row.get("category_depth", 0), +1),
    }
    barrier_candidates = {
        "DEAL_SEEKER":    ("rating",        feat_row.get("rating", 3.5) - 4.3,          -1),
        "QUALITY_FIRST":  ("savings_ratio", -(feat_row.get("savings_ratio", 0) - 0.35), -1),
        "SOCIAL_PROOF":   ("trust_score",   feat_row.get("trust_score", 2.5) - 3.5,    -1),
        "NICHE_EXPLORER": ("word_count",    feat_row.get("word_count", 50) - 200,        -1),
    }
    pf, pv, _ = push_candidates.get(seg, ("savings_ratio", 0.3, 1))
    bf, bv, _ = barrier_candidates.get(seg, ("rating", -0.5, -1))
    return pf, float(pv), bf, float(bv)


def _delta_badge(new_val, orig_val, fmt=".1f", unit=""):
    """Render a live delta badge comparing slider to original value."""
    diff = new_val - orig_val
    if abs(diff) < 1e-6:
        return '<span class="p6-delta-badge same">— no change</span>'
    arrow = "▲" if diff > 0 else "▼"
    cls   = "up" if diff > 0 else "down"
    val_str = f"{abs(diff):{fmt}}{unit}"
    return f'<span class="p6-delta-badge {cls}">{arrow} {val_str}</span>'


# ─────────────────────────────────────────────────────────────────────────────
# MAIN RENDER
# ─────────────────────────────────────────────────────────────────────────────

def render(feat, imp, filtered_feat, filtered_imp, shap_df):

    st.markdown('<div class="cw">', unsafe_allow_html=True)
    st.markdown(
        page_header(
            "06 / Product Intelligence",
            "Product Intelligence",
            "Search any product — decode buyer intent classification, SHAP drivers, "
            "and simulate segment upgrades with live revenue impact.",
        ),
        unsafe_allow_html=True,
    )

    # ── Search engine ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:0 48px 8px;">
      <div style="font-family:'Inter',sans-serif;font-size:12px;font-weight:600;
                  color:var(--text-faint);letter-spacing:0.07em;text-transform:uppercase;
                  margin-bottom:8px;">🔍 Product Search</div>
    </div>
    """, unsafe_allow_html=True)

    search_col, _ = st.columns([2, 1])
    with search_col:
        query = st.text_input(
            "Search",
            placeholder="Type brand or product — e.g. boAt, Redmi, cable, speaker, heater…",
            label_visibility="collapsed",
        )

    # ── Empty state ───────────────────────────────────────────────────────────
    if not query.strip():
        st.markdown("""
        <div style="padding:0 48px;">
          <div class="p6-sec-div">Segment Quick-Stats — enter a search query above to explore</div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            _seg_quick_stats(feat, imp)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── Search results ────────────────────────────────────────────────────────
    results = imp[imp["product_name"].str.contains(query.strip(), case=False, na=False)]

    if results.empty:
        st.warning(
            "No products matched. Try a shorter keyword — e.g. 'boAt', 'cable', 'heater'."
        )
        st.markdown('</div>', unsafe_allow_html=True)
        return

    res_col, _ = st.columns([2, 1])
    with res_col:
        sel_idx = st.selectbox(
            f"{len(results):,} products found — select one",
            range(len(results)),
            format_func=lambda i: results.iloc[i]["product_name"][:90],
        )

    row = results.iloc[sel_idx]

    # ── Feature row ───────────────────────────────────────────────────────────
    feat_matches = feat[feat["product_id"] == row["product_id"]]
    if feat_matches.empty:
        st.warning("Feature data not found for this product. Try another.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    feat_row = feat_matches.iloc[0]

    seg = str(row.get("pred_segment", row.get("segment", "UNMATCHED")))
    sc  = SEG_COLORS.get(seg, "#64748B")
    mm  = int(row.get("mismatch_flag", 0))
    r_c, g_c, b_c = int(sc[1:3], 16), int(sc[3:5], 16), int(sc[5:7], 16)

    # ── Product card ──────────────────────────────────────────────────────────
    mm_color  = "#EF4444" if mm else "#10B981"
    mm_bg     = "rgba(239,68,68,0.08)"  if mm else "rgba(16,185,129,0.08)"
    mm_border = "rgba(239,68,68,0.22)"  if mm else "rgba(16,185,129,0.22)"
    mm_label  = "⚡ MISMATCH DETECTED"  if mm else "✓ CORRECTLY PLACED"

    st.markdown(f"""
    <div class="p6-product-card"
         style="border-left-color:{sc};
                border-color:rgba({r_c},{g_c},{b_c},0.22);">
      <div class="p6-product-name">{str(row.get("product_name",""))[:130]}</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;">
        <span class="p6-chip">{row.get("top_cat","—")}</span>
        <span class="p6-chip">₹{float(row.get("price_disc",0)):,.0f}</span>
        <span class="p6-chip">{float(row.get("discount_pct",0)):.0f}% off</span>
        <span class="p6-chip">{float(row.get("rating",0)):.1f}★</span>
        <span class="p6-chip">{int(row.get("rating_count",0)):,} reviews</span>
        <span class="p6-chip">{str(row.get("price_tier","—"))}</span>
      </div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        {seg_badge(seg)}
        <span style="background:{mm_bg};color:{mm_color};
              border:1px solid {mm_border};border-radius:100px;
              padding:4px 14px;font-size:12px;font-weight:600;
              font-family:'JetBrains Mono',monospace;letter-spacing:0.04em;">
          {mm_label}
        </span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:11.5px;
              color:var(--text-faint);">
          ID: {str(row.get("product_id",""))[:24]}
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 4 Animated KPI cards ──────────────────────────────────────────────────
    monthly_vol = float(feat_row.get("monthly_volume", 0))
    rev_base    = float(row.get("revenue_baseline", feat_row.get("revenue_baseline", 0)))
    rev_opp     = float(row.get("revenue_uplift",   feat_row.get("revenue_uplift",   0)))
    mm_cost     = float(row.get("mismatch_revenue_loss", feat_row.get("mismatch_revenue_loss", 0)))

    card4 = (
        kpi_card_animated("Mismatch Cost",   fmt_inr(mm_cost), "monthly leakage",        "red",   3)
        if mm else
        kpi_card_animated("Mismatch Status", "Optimal",        "correctly classified",   "green", 3)
    )

    st.markdown(
        p6_kpi_grid(
            kpi_card_animated("Monthly Volume",     f"{monthly_vol:,.0f}", "units / month proxy",         "orange", 0)
            + kpi_card_animated("Revenue Baseline", fmt_inr(rev_base),    "current monthly est.",        "blue",   1)
            + kpi_card_animated("Rev Opportunity",  fmt_inr(rev_opp),     "with optimal placement",      "green",  2)
            + card4
        ),
        unsafe_allow_html=True,
    )

    # ── Two column layout — scores + SHAP ─────────────────────────────────────
    col_l, col_r = st.columns([1.1, 1])

    with col_l:
        st.markdown('<div class="p6-sec-div">Segment Score Breakdown</div>', unsafe_allow_html=True)
        scores = {
            "DEAL_SEEKER":    float(feat_row.get("score_DEAL_SEEKER",    0)),
            "QUALITY_FIRST":  float(feat_row.get("score_QUALITY_FIRST",  0)),
            "SOCIAL_PROOF":   float(feat_row.get("score_SOCIAL_PROOF",   0)),
            "NICHE_EXPLORER": float(feat_row.get("score_NICHE_EXPLORER", 0)),
            "UNMATCHED":      0.01,
        }
        st.plotly_chart(probability_bars(scores, seg), use_container_width=True)

    with col_r:
        st.markdown('<div class="p6-sec-div">SHAP Intent Drivers</div>', unsafe_allow_html=True)

        # Resolve push / barrier
        if (shap_df is not None
                and "product_id" in shap_df.columns
                and row["product_id"] in shap_df["product_id"].values):
            sr           = shap_df[shap_df["product_id"] == row["product_id"]].iloc[0]
            push_feat    = str(sr.get("shap_push",        "savings_ratio"))
            push_val     = float(sr.get("shap_push_val",   0.3))
            barrier_feat = str(sr.get("shap_barrier",      "rating"))
            barrier_val  = float(sr.get("shap_barrier_val",-0.2))
        else:
            push_feat, push_val, barrier_feat, barrier_val = _heuristic_shap(feat_row, seg)

        push_explain = {
            "savings_ratio":  "High savings ratio is the dominant classification signal for this segment.",
            "trust_score":    "Elevated trust score signals quality positioning to the model.",
            "review_log":     "High review volume (log-scaled) confirms social proof activation.",
            "category_depth": "Deep sub-category specificity triggers niche explorer classification.",
            "discount_pct":   "Discount depth fires the deal-seeking classification rule.",
            "rating":         "Product rating meets or exceeds the segment quality threshold.",
        }
        barrier_explain = {
            "rating":        "Rating below 4.3★ blocks QUALITY_FIRST — the primary upgrade barrier.",
            "savings_ratio": "savings_ratio > 0.35 is NEGATIVE SHAP for QUALITY_FIRST — the discount paradox.",
            "discount_pct":  "Discount above 35% prevents QUALITY_FIRST regardless of other features.",
            "trust_score":   "Trust score below 3.5 limits segment upgrade potential.",
            "word_count":    "Listing richness below niche threshold — deepen product description.",
        }

        st.markdown(f"""
        <div class="p6-shap-card push">
          <div class="p6-shap-label" style="color:#34D399;">▲ Primary Classification Driver</div>
          <div class="p6-shap-feat">{push_feat}</div>
          <div class="p6-shap-val" style="color:#34D399;">SHAP = +{abs(push_val):.4f}</div>
          <div class="p6-shap-desc">
            {push_explain.get(push_feat, "Primary driver for this product's classification.")}
          </div>
        </div>
        <div class="p6-shap-card barrier">
          <div class="p6-shap-label" style="color:#F87171;">▼ Biggest Upgrade Blocker</div>
          <div class="p6-shap-feat">{barrier_feat}</div>
          <div class="p6-shap-val" style="color:#F87171;">SHAP = {barrier_val:.4f}</div>
          <div class="p6-shap-desc">
            {barrier_explain.get(barrier_feat, "Primary barrier preventing segment upgrade.")}
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<div class="p6-sec-div" style="margin-top:22px;">Critical Feature Values vs Segment Average</div>',
            unsafe_allow_html=True,
        )
        seg_data_all = feat[feat["segment"] == seg]
        for feat_name in SEG_FEATURES.get(seg, []):
            if feat_name not in feat_row.index:
                continue
            val     = float(feat_row.get(feat_name, 0))
            seg_avg = float(seg_data_all[feat_name].mean()) if len(seg_data_all) else 0
            delta   = val - seg_avg
            arrow   = "▲" if delta >= 0 else "▼"
            a_color = sc if delta >= 0 else "#EF4444"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                 padding:8px 10px;margin-bottom:4px;
                 border-radius:8px;border:1px solid transparent;
                 transition:all 0.18s ease;"
                 onmouseover="this.style.background='rgba(255,255,255,0.03)';
                              this.style.borderColor='rgba(255,255,255,0.07)'"
                 onmouseout="this.style.background='transparent';
                             this.style.borderColor='transparent'">
              <span class="p6-feat-name">{feat_name}</span>
              <span class="p6-feat-val">{val:.3f}</span>
              <span class="p6-feat-delta" style="color:{a_color};">
                {arrow} {abs(delta):.3f}
                <span style="color:var(--text-faint);font-size:10.5px;"> vs {seg_avg:.3f}</span>
              </span>
            </div>
            """, unsafe_allow_html=True)

    # ── Seller Action Plan ────────────────────────────────────────────────────
    st.markdown('<div class="p6-sec-div">🎯 Seller Action Plan</div>', unsafe_allow_html=True)

    actions = generate_seller_actions(
        current_seg   = seg,
        target_seg    = "QUALITY_FIRST",
        rating        = float(feat_row.get("rating", 0)),
        discount_pct  = float(feat_row.get("discount_pct", 0)),
        rating_count  = int(feat_row.get("rating_count", 0)),
        savings_ratio = float(feat_row.get("savings_ratio", 0)),
        trust_score   = float(feat_row.get("trust_score", 0)),
    )

    actions_html = '<div class="p6-rec-box">'
    for i, action in enumerate(actions, 1):
        actions_html += f"""
        <div style="display:flex;gap:14px;margin-bottom:14px;align-items:flex-start;
                    padding-bottom:14px;
                    border-bottom:1px solid rgba(59,130,246,0.10);"
             {"" if i < len(actions) else 'style="border-bottom:none;margin-bottom:0;"'}>
          <span class="p6-action-num" style="color:{sc};">{i}.</span>
          <span class="p6-action-text">{action}</span>
        </div>"""
    actions_html += '</div>'
    st.markdown(actions_html, unsafe_allow_html=True)

    # ── What-If Simulator ─────────────────────────────────────────────────────
    with st.expander("⚙️  What-If Simulator — Adjust attributes and watch the segment shift live"):

        # Store originals for delta badges
        orig_rating   = float(feat_row.get("rating",       3.5))
        orig_discount = int(feat_row.get("discount_pct",   40))
        orig_reviews  = int(feat_row.get("rating_count",   500))
        orig_trust    = float(feat_row.get("trust_score",  2.5))

        # ── Slider header row ─────────────────────────────────────────────────
        st.markdown("""
        <div style="font-family:'Inter',sans-serif;font-size:11.5px;color:var(--text-faint);
                    letter-spacing:0.06em;text-transform:uppercase;font-weight:600;
                    margin:8px 0 14px;">
          Drag sliders to simulate product changes — results update instantly
        </div>
        """, unsafe_allow_html=True)

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            new_rating = st.slider("Product Rating ★", 0.0, 5.0, orig_rating, 0.1)
            st.markdown(
                f'<div style="text-align:center;margin-top:-10px;">'
                + _delta_badge(new_rating, orig_rating, ".1f", "★")
                + '</div>',
                unsafe_allow_html=True,
            )
        with s2:
            new_discount = st.slider("Discount %", 0, 94, orig_discount, 1)
            st.markdown(
                f'<div style="text-align:center;margin-top:-10px;">'
                + _delta_badge(new_discount, orig_discount, ".0f", "%")
                + '</div>',
                unsafe_allow_html=True,
            )
        with s3:
            new_reviews = st.slider("Review Count", 0, 100_000, orig_reviews, 100)
            delta_rev = new_reviews - orig_reviews
            rev_cls   = "up" if delta_rev > 0 else ("down" if delta_rev < 0 else "same")
            rev_arrow = "▲" if delta_rev > 0 else ("▼" if delta_rev < 0 else "—")
            rev_disp  = f"{abs(delta_rev):,}" if delta_rev != 0 else "no change"
            st.markdown(
                f'<div style="text-align:center;margin-top:-10px;">'
                f'<span class="p6-delta-badge {rev_cls}">{rev_arrow} {rev_disp}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with s4:
            new_trust = st.slider("Trust Score", 0.0, 4.5, orig_trust, 0.05)
            st.markdown(
                f'<div style="text-align:center;margin-top:-10px;">'
                + _delta_badge(new_trust, orig_trust, ".2f")
                + '</div>',
                unsafe_allow_html=True,
            )

        # ── Compute live results (unchanged logic) ────────────────────────────
        new_savings = 1 - new_discount / 100
        new_scores  = compute_segment_scores(
            rating         = new_rating,
            discount_pct   = new_discount,
            rating_count   = new_reviews,
            category       = str(feat_row.get("top_cat", "Electronics")),
            savings_ratio  = new_savings,
            category_depth = int(feat_row.get("category_depth", 1)),
            trust_score    = new_trust,
        )
        new_seg     = predict_segment(new_scores)
        new_prob_qf = compute_success_probability(
            rating        = new_rating,
            discount_pct  = new_discount,
            rating_count  = new_reviews,
            savings_ratio = new_savings,
            trust_score   = new_trust,
            target_seg    = "QUALITY_FIRST",
        )
        new_rev   = (new_reviews / 12) * float(feat_row.get("price_disc", 0)) * 0.38
        old_rev   = rev_base * float(feat_row.get("uplift_rate", 0.1))
        rev_delta = new_rev - old_rev

        st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:20px 0;'>",
                    unsafe_allow_html=True)

        r1, r2, r3 = st.columns(3)

        with r1:
            new_sc    = SEG_COLORS.get(new_seg, "#64748B")
            changed   = new_seg != seg
            new_r, new_g, new_b = int(new_sc[1:3],16), int(new_sc[3:5],16), int(new_sc[5:7],16)
            change_row = (
                f'<div style="margin-top:10px;font-family:\'JetBrains Mono\',monospace;'
                f'font-size:11.5px;color:#34D399;font-weight:600;">'
                f'✦ Changed from {seg.replace("_"," ")}</div>'
                if changed else
                f'<div style="margin-top:10px;font-size:11.5px;color:var(--text-faint);">'
                f'No segment change</div>'
            )
            st.markdown(f"""
            <div class="glass-card"
                 style="text-align:center;
                        border-top:2px solid {new_sc};
                        border-color:rgba({new_r},{new_g},{new_b},0.22);">
              <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
                   color:var(--text-faint);text-transform:uppercase;letter-spacing:0.09em;
                   margin-bottom:12px;">New Predicted Segment</div>
              {seg_badge(new_seg)}
              {change_row}
            </div>
            """, unsafe_allow_html=True)

        with r2:
            st.markdown("""
            <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
                 color:var(--text-faint);text-transform:uppercase;letter-spacing:0.09em;
                 margin-bottom:6px;">QUALITY_FIRST Probability</div>
            """, unsafe_allow_html=True)
            st.plotly_chart(whyif_gauge(new_prob_qf), use_container_width=True)

        with r3:
            d_color = "#10B981" if rev_delta >= 0 else "#EF4444"
            d_arrow = "▲" if rev_delta >= 0 else "▼"
            d_r, d_g, d_b = int(d_color[1:3],16), int(d_color[3:5],16), int(d_color[5:7],16)
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;
                 border-color:rgba({d_r},{d_g},{d_b},0.20);">
              <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
                   color:var(--text-faint);text-transform:uppercase;letter-spacing:0.09em;
                   margin-bottom:12px;">Revenue Impact</div>
              <div style="font-family:'Inter',sans-serif;font-size:32px;font-weight:800;
                   color:{d_color};letter-spacing:-0.04em;line-height:1;margin-bottom:8px;">
                {d_arrow} {fmt_inr(abs(rev_delta))}
              </div>
              <div style="font-size:12.5px;color:var(--text-faint);margin-top:6px;line-height:1.65;">
                vs current baseline<br>
                <span style="color:var(--text-muted);">
                  New: {fmt_inr(new_rev)} &nbsp;·&nbsp; Old: {fmt_inr(old_rev)}
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Segment shift — pulsing celebration box ───────────────────────────
        if new_seg != seg:
            new_actions = generate_seller_actions(
                current_seg   = new_seg,
                target_seg    = "QUALITY_FIRST" if new_seg != "QUALITY_FIRST" else "SOCIAL_PROOF",
                rating        = new_rating,
                discount_pct  = new_discount,
                rating_count  = new_reviews,
                savings_ratio = new_savings,
                trust_score   = new_trust,
            )
            new_sc2 = SEG_COLORS.get(new_seg, "#10B981")

            st.markdown(f"""
            <div class="p6-shift-box">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <span style="font-size:20px;">🎯</span>
                <div>
                  <div style="font-family:'Inter',sans-serif;font-size:15px;font-weight:700;
                       color:#34D399;letter-spacing:-0.01em;">
                    Segment shift detected
                  </div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:11.5px;
                       color:var(--text-muted);margin-top:2px;">
                    {seg.replace("_"," ")} → {new_seg.replace("_"," ")}
                  </div>
                </div>
              </div>
              <div style="font-size:12.5px;color:var(--text-faint);
                          margin-bottom:14px;line-height:1.6;">
                Seller actions for your simulated configuration:
              </div>
            """, unsafe_allow_html=True)

            for i, action in enumerate(new_actions, 1):
                st.markdown(f"""
                <div style="display:flex;gap:12px;margin-bottom:10px;align-items:flex-start;">
                  <span style="font-family:'Inter',sans-serif;font-size:14px;font-weight:800;
                        color:{new_sc2};flex-shrink:0;">{i}.</span>
                  <span style="font-size:13.5px;color:var(--text-muted);line-height:1.7;">
                    {action}
                  </span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)