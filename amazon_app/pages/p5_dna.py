"""
p5_dna.py — Buyer DNA
Deep-dive into any buyer archetype — fingerprint, SHAP, radar, top products.
"""

import streamlit as st
import pandas as pd
from utils.style import (
    page_header, sec_div, seg_badge, feat_bar, fmt_inr, SEG_COLORS,
    SEG_ICONS, SEG_TAGLINES, SEG_DNA,
)
from utils.charts import radar_chart, revenue_hist
from utils.data_loader import RADAR_FEATURES, SEG_FEATURES


def _show_asset(path: str, fallback_fname: str):
    import os
    if os.path.exists(path):
        st.image(path, use_container_width=True)
    else:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;padding:28px;
                    border:1px dashed rgba(255,255,255,0.07);">
          <div style="font-size:24px;margin-bottom:6px;">🖼</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#3B3A52;">
            Place <code style="color:#FF9500;">{fallback_fname}</code> in
            <code style="color:#FF9500;">assets/</code>
          </div>
        </div>
        """, unsafe_allow_html=True)


def render(feat, imp, filtered_feat, filtered_imp, shap_df):

    st.markdown('<div class="cw">', unsafe_allow_html=True)
    st.markdown(
        page_header(
            "05 / Segment Intelligence",
            "Buyer DNA",
            "Deep-dive into any buyer archetype — behavioural fingerprint, SHAP attribution, top products.",
        ),
        unsafe_allow_html=True,
    )

    # ── Segment selector ──────────────────────────────────────────────────────
    seg_choice = st.selectbox(
        "",
        ["DEAL_SEEKER", "QUALITY_FIRST", "SOCIAL_PROOF", "NICHE_EXPLORER"],
        label_visibility="collapsed",
    )
    seg_data = filtered_feat[filtered_feat["segment"] == seg_choice]
    sc       = SEG_COLORS[seg_choice]
    icon     = SEG_ICONS[seg_choice]
    tagline  = SEG_TAGLINES.get(seg_choice, "")
    dna_text = SEG_DNA.get(seg_choice, "")
    count    = len(seg_data)

    # ── Segment banner ────────────────────────────────────────────────────────
    avg_disc = seg_data["discount_pct"].mean() if count else 0
    avg_rat  = seg_data["rating"].mean() if count else 0
    rev_opp  = seg_data["revenue_uplift"].sum() if count else 0

    st.markdown(f"""
    <div class="seg-banner" style="border-left:4px solid {sc};background:{sc}06;
         border-radius:12px;padding:20px 24px;margin:0 0 20px;">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px;">
        <div style="flex:1;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <span style="font-size:36px;">{icon}</span>
            <div>
              <div class="seg-banner-title" style="font-family:'Syne',sans-serif;
                   font-size:20px;font-weight:800;color:{sc};">{seg_choice.replace("_"," ")}</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#3B3A52;
                   letter-spacing:0.08em;text-transform:uppercase;">{tagline}</div>
            </div>
            <span style="background:{sc}18;color:{sc};border:1px solid {sc}30;
                 border-radius:20px;padding:3px 10px;font-size:11px;
                 font-family:'JetBrains Mono',monospace;margin-left:8px;">
              {count:,} products
            </span>
          </div>
        </div>
        <div style="display:flex;gap:24px;flex-shrink:0;">
          <div style="text-align:center;">
            <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
                 color:{sc};">{avg_disc:.1f}%</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#3B3A52;
                 text-transform:uppercase;">Avg Discount</div>
          </div>
          <div style="text-align:center;">
            <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
                 color:{sc};">{avg_rat:.2f}★</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#3B3A52;
                 text-transform:uppercase;">Avg Rating</div>
          </div>
          <div style="text-align:center;">
            <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
                 color:{sc};">{fmt_inr(rev_opp)}</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#3B3A52;
                 text-transform:uppercase;">Rev Opportunity</div>
          </div>
        </div>
      </div>
      <div style="font-size:12.5px;color:#6B6988;line-height:1.7;margin-top:12px;
           border-top:1px solid rgba(255,255,255,0.04);padding-top:10px;">{dna_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two column layout ─────────────────────────────────────────────────────
    col_l, col_r = st.columns([1.1, 1])

    with col_l:
        st.markdown(sec_div("SHAP Feature Importance"), unsafe_allow_html=True)
        _show_asset(f"assets/shap_bar_{seg_choice}.png", f"shap_bar_{seg_choice}.png")

        if seg_choice == "QUALITY_FIRST":
            st.markdown(sec_div("Beeswarm — The Discount Paradox"), unsafe_allow_html=True)
            _show_asset("assets/beeswarm_QUALITY_FIRST.png", "beeswarm_QUALITY_FIRST.png")

        st.markdown(sec_div(f"Waterfall — Sample {seg_choice} Product"), unsafe_allow_html=True)
        _show_asset(f"assets/waterfall_{seg_choice}.png", f"waterfall_{seg_choice}.png")

    with col_r:
        st.markdown(sec_div("Behavioural Feature Fingerprint"), unsafe_allow_html=True)

        seg_feats = SEG_FEATURES.get(seg_choice, [])
        for feat_name in seg_feats:
            if feat_name not in seg_data.columns:
                continue
            seg_avg     = float(seg_data[feat_name].mean()) if count else 0
            overall_avg = float(filtered_feat[feat_name].mean()) if len(filtered_feat) else 0
            max_val     = float(filtered_feat[feat_name].max()) if len(filtered_feat) else 1
            st.markdown(feat_bar(feat_name, seg_avg, overall_avg, max_val, sc),
                        unsafe_allow_html=True)

        st.markdown(sec_div("5-Feature Radar Profile"), unsafe_allow_html=True)
        seg_norm     = {}
        overall_norm = {}
        for label, col in RADAR_FEATURES.items():
            if col not in feat.columns:
                continue
            mx = feat[col].max() or 1
            seg_norm[label]     = float(seg_data[col].mean() / mx) if count else 0
            overall_norm[label] = float(feat[col].mean() / mx)
        st.plotly_chart(radar_chart(seg_norm, overall_norm, color=sc),
                        use_container_width=True)

        st.markdown(sec_div("Revenue Uplift Distribution"), unsafe_allow_html=True)
        st.plotly_chart(revenue_hist(filtered_feat, seg_choice), use_container_width=True)

    # ── Bottom — Top 10 products ───────────────────────────────────────────────
    st.markdown(sec_div("Top 10 Products by Revenue Opportunity"), unsafe_allow_html=True)

    seg_col = "pred_segment" if "pred_segment" in imp.columns else "segment"
    top10_feat = seg_data.nlargest(10, "revenue_uplift")

    # Merge with imp for product_name
    top10 = top10_feat.merge(
        imp[["product_id", "product_name"]].drop_duplicates("product_id"),
        on="product_id", how="left",
    )

    rows = []
    for _, r in top10.iterrows():
        rows.append({
            "Product":         str(r.get("product_name", r.get("product_id", "")))[:55],
            "Category":        str(r.get("top_cat", "—")),
            "Price":           f"₹{r.get('price_disc', 0):,.0f}",
            "Discount":        f"{r.get('discount_pct', 0):.0f}%",
            "Rating":          f"{r.get('rating', 0):.1f}★",
            "Trust":           f"{r.get('trust_score', 0):.2f}",
            "Rev Opportunity": fmt_inr(r.get("revenue_uplift", 0)),
            "Status":          "⚠ Mismatch" if r.get("mismatch_flag", 0) else "✓ Aligned",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)