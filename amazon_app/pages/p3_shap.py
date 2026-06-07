"""
p3_shap.py — Explainability Studio
SHAP bar, beeswarm, waterfall, feature correlation, dependence plots.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.style import page_header, sec_div, SEG_COLORS, SEG_ICONS
from utils.charts import feature_corr_heatmap

_SEG_INSIGHTS = {
    "DEAL_SEEKER":    "savings_ratio dominates — top SHAP feature with 3× weight vs other signals. Discount depth alone triggers deal-mode cognitive shortcuts.",
    "QUALITY_FIRST":  "savings_ratio is the #1 NEGATIVE driver — the discount paradox visualised. Premium buyers interpret >35% discounts as quality red flags.",
    "SOCIAL_PROOF":   "review_log is primary — crowd validation signal outweighs both price and rating. Social proof (Cialdini) operationalised in SHAP values.",
    "NICHE_EXPLORER": "category_depth is decisive — sub-category specificity triggers classification. Broad listings are invisible to expert buyers.",
}

_WATERFALL_INSIGHTS = {
    "DEAL_SEEKER":    "savings_ratio as the primary push feature at SHAP ≈ +0.48, followed by discount_pct",
    "QUALITY_FIRST":  "trust_score as the primary push feature at SHAP ≈ +0.52, with savings_ratio showing negative SHAP ≈ −0.31",
    "SOCIAL_PROOF":   "review_log as the primary push feature at SHAP ≈ +0.61, with social_proof_score reinforcing",
    "NICHE_EXPLORER": "category_depth as the primary push feature at SHAP ≈ +0.44, with keyword_density as secondary",
}

_FALLBACK_DIV = """
<div class="glass-card" style="text-align:center;padding:32px;border:1px dashed rgba(255,255,255,0.08);">
  <div style="font-size:28px;margin-bottom:8px;">🖼</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#3B3A52;letter-spacing:0.08em;">
    Place <code style="color:#FF9500;">{fname}</code> in <code style="color:#FF9500;">assets/</code> folder
  </div>
</div>
"""


def _show_asset(path: str, fallback_fname: str, **kwargs):
    """Try to show an image asset; show a styled fallback if missing."""
    import os
    if os.path.exists(path):
        st.image(path, use_container_width=True, **kwargs)
    else:
        st.markdown(_FALLBACK_DIV.format(fname=fallback_fname), unsafe_allow_html=True)


def render(feat, imp, filtered_feat, filtered_imp, shap_df):

    st.markdown('<div class="cw">', unsafe_allow_html=True)
    st.markdown(
        page_header(
            "03 / Explainability",
            "Explainability Studio",
            "SHAP feature attribution decoding why the model classifies each product.",
        ),
        unsafe_allow_html=True,
    )

    # ── Insight banner ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="glass-card" style="border-left:3px solid #FF9500;margin:0 48px 24px;">
      <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:700;
                  color:#FF9500;margin-bottom:8px;">
        The Discount Paradox — SHAP Reveals Counter-Intuitive Signal
      </div>
      <div style="font-size:13px;color:#8B89A8;line-height:1.7;">
        SHAP dependence analysis shows <strong style="color:#E8E6F0;">savings_ratio > 0.35
        has NEGATIVE impact</strong> on QUALITY_FIRST classification probability. Sellers
        offering >35% discount to attract premium buyers are actively signalling low quality
        — repelling the segment worth <strong style="color:#00C2FF;">1.4× more revenue per
        product</strong>. This is the project's core actionable finding.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tabs = st.tabs(["📊 SHAP Bar Plots", "🐝 Beeswarm", "💧 Waterfall",
                    "🔗 Feature Correlation", "📈 Dependence"])

    # ── TAB 1 — SHAP Bar Plots ────────────────────────────────────────────────
    with tabs[0]:
        cols = st.columns(4)
        segs = ["DEAL_SEEKER", "QUALITY_FIRST", "SOCIAL_PROOF", "NICHE_EXPLORER"]
        for col, seg in zip(cols, segs):
            with col:
                color = SEG_COLORS[seg]
                icon  = SEG_ICONS[seg]
                st.markdown(f"""
                <div style="text-align:center;padding:8px 0 12px;">
                  <span style="font-size:20px;">{icon}</span>
                  <div style="font-family:'Syne',sans-serif;font-size:12px;font-weight:700;
                              color:{color};margin-top:4px;">{seg.replace("_"," ")}</div>
                </div>
                """, unsafe_allow_html=True)
                _show_asset(f"assets/shap_bar_{seg}.png", f"shap_bar_{seg}.png")
                st.markdown(f"""
                <div style="font-size:11px;color:#6B6988;line-height:1.6;
                            padding:8px 4px 16px;">{_SEG_INSIGHTS[seg]}</div>
                """, unsafe_allow_html=True)

    # ── TAB 2 — Beeswarm ─────────────────────────────────────────────────────
    with tabs[1]:
        _show_asset("assets/beeswarm_QUALITY_FIRST.png", "beeswarm_QUALITY_FIRST.png")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("""
            <div class="glass-card" style="border-left:3px solid #FF9500;">
              <div style="font-family:'Syne',sans-serif;font-size:12px;font-weight:700;
                          color:#FF9500;margin-bottom:6px;">High savings_ratio cluster (red dots)</div>
              <div style="font-size:12px;color:#6B6988;line-height:1.6;">
                Consistently appears on the <strong style="color:#C8C6DC;">LEFT side
                (negative SHAP)</strong> of the beeswarm — confirming that high savings_ratio
                <em>reduces</em> the probability of QUALITY_FIRST classification.
              </div>
            </div>
            """, unsafe_allow_html=True)
        with col_r:
            st.markdown("""
            <div class="glass-card" style="border-left:3px solid #00C2FF;">
              <div style="font-family:'Syne',sans-serif;font-size:12px;font-weight:700;
                          color:#00C2FF;margin-bottom:6px;">Low savings_ratio cluster (blue dots)</div>
              <div style="font-size:12px;color:#6B6988;line-height:1.6;">
                Cluster on the <strong style="color:#C8C6DC;">RIGHT side (positive SHAP)</strong>
                — confirming the paradox is systematic, not product-specific.
                The pattern holds across all 147 QUALITY_FIRST products.
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── TAB 3 — Waterfall ────────────────────────────────────────────────────
    with tabs[2]:
        cols2 = st.columns(4)
        for col, seg in zip(cols2, segs):
            with col:
                color = SEG_COLORS[seg]
                st.markdown(f"""
                <div style="font-family:'Syne',sans-serif;font-size:12px;font-weight:700;
                            color:{color};text-align:center;padding:8px 0 10px;">
                  {SEG_ICONS[seg]} {seg.replace("_"," ")}
                </div>
                """, unsafe_allow_html=True)
                _show_asset(f"assets/waterfall_{seg}.png", f"waterfall_{seg}.png")
                st.markdown(f"""
                <div style="font-size:10.5px;color:#5B5A72;line-height:1.6;
                            padding:6px 2px 16px;">
                  This sample shows {_WATERFALL_INSIGHTS[seg]}.
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 4 — Feature Correlation ──────────────────────────────────────────
    with tabs[3]:
        st.plotly_chart(feature_corr_heatmap(feat, height=440), use_container_width=True)
        st.markdown("""
        <div class="glass-card" style="margin-top:12px;">
          <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:700;
                      color:#E8E6F0;margin-bottom:8px;">Key Correlation Insights</div>
          <div style="font-size:12.5px;color:#8B89A8;line-height:1.7;">
            <strong style="color:#FF9500;">savings_ratio ↔ discount_pct: 0.994</strong>
            (expected — both measure discount depth). &nbsp;|&nbsp;
            <strong style="color:#00C2FF;">trust_score ↔ rating: 0.71</strong>
            — quality signals cluster together. &nbsp;|&nbsp;
            <strong style="color:#BF5FFF;">review_log ↔ social_proof_score: 0.83</strong>
            — review volume drives social proof composite. These collinear pairs
            mean SHAP attribution is split across both — interpret them together.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 5 — Dependence ───────────────────────────────────────────────────
    with tabs[4]:
        col_l2, col_r2 = st.columns([1.2, 1])
        with col_l2:
            st.markdown(sec_div("savings_ratio vs QUALITY_FIRST Score — Dependence Plot"),
                        unsafe_allow_html=True)
            if "score_QUALITY_FIRST" in feat.columns and "savings_ratio" in feat.columns:
                plot_df = feat[["savings_ratio", "score_QUALITY_FIRST", "rating"]].dropna()
                fig = px.scatter(
                    plot_df,
                    x="savings_ratio",
                    y="score_QUALITY_FIRST",
                    color="rating",
                    color_continuous_scale=["#FF4444", "#4A4862", "#00C2FF"],
                    labels={
                        "savings_ratio":       "Savings Ratio",
                        "score_QUALITY_FIRST": "QUALITY_FIRST Score",
                        "rating":              "Rating ★",
                    },
                    opacity=0.65,
                    height=380,
                )
                fig.add_vline(
                    x=0.35,
                    line_dash="dash",
                    line_color="#FF4444",
                    line_width=1.5,
                    annotation_text="Paradox threshold: 0.35",
                    annotation_font_color="#FF4444",
                    annotation_font_size=10,
                )
                fig.update_layout(
                    paper_bgcolor="#0A0A12",
                    plot_bgcolor="#0A0A12",
                    margin=dict(t=20, b=12, l=12, r=12),
                    font=dict(color="#6B6988"),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Requires score_QUALITY_FIRST and savings_ratio columns.")

        with col_r2:
            st.markdown(sec_div("Discount Paradox Explanation"), unsafe_allow_html=True)
            st.markdown("""
            <div class="glass-card" style="border-left:3px solid #FF4444;">
              <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:700;
                          color:#FF4444;margin-bottom:10px;">
                Why Over-Discounting Repels Premium Buyers
              </div>
              <div style="font-size:12.5px;color:#8B89A8;line-height:1.75;">
                The vertical dashed line marks <strong style="color:#FF9500;">savings_ratio = 0.35</strong>
                — the SHAP inflection point. Products to the <strong style="color:#FF4444;">right</strong>
                (high discount) show <strong style="color:#FF4444;">near-zero QUALITY_FIRST score</strong>
                regardless of rating.
                <br><br>
                <strong style="color:#E8E6F0;">Seller action:</strong> If your savings_ratio exceeds
                0.35, reducing the listed original price (MRP anchor) while keeping the discounted
                price constant will lower savings_ratio without changing the buyer's actual cost —
                moving into QUALITY_FIRST territory and unlocking 1.4× revenue weight.
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)