import streamlit as st
import pandas as pd
from utils.style import (
    SEG_COLORS, page_header, kpi_card, sec_div, seg_badge, fmt_inr, fmt_num,
)
from utils.charts import (
    seg_by_category_bar, revenue_heatmap, discount_violin,
    price_rating_scatter, revenue_treemap,
)
from utils.data_loader import category_stats, revenue_by_seg

_MARKET_STYLES = """
<style>
@keyframes kpiSlideUp {
  from { opacity: 0; transform: translateY(14px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes bannerIn {
  from { opacity: 0; transform: translateX(-12px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* ── KPI grid stagger ─────────────────────────────────────────────────────── */
.kpi-grid-4 .kpi-card:nth-child(1) { animation: kpiSlideUp 0.4s 0.05s ease-out backwards; }
.kpi-grid-4 .kpi-card:nth-child(2) { animation: kpiSlideUp 0.4s 0.13s ease-out backwards; }
.kpi-grid-4 .kpi-card:nth-child(3) { animation: kpiSlideUp 0.4s 0.21s ease-out backwards; }
.kpi-grid-4 .kpi-card:nth-child(4) { animation: kpiSlideUp 0.4s 0.29s ease-out backwards; }

/* ── Market insight banner ──────────────────────────────────────────────── */
.market-insight-banner {
  background: var(--bg-card);
  border: 1px solid rgba(59,130,246,0.18);
  border-left: 3px solid var(--accent-blue);
  border-radius: var(--radius-xl);
  padding: 18px 26px;
  margin: 0 0 28px;
  animation: bannerIn 0.4s 0.1s ease-out backwards;
  transition: all var(--transition);
}
.market-insight-banner:hover {
  border-color: rgba(59,130,246,0.35);
  box-shadow: 0 6px 24px rgba(59,130,246,0.07), var(--shadow-md);
  transform: translateY(-2px);
}
.mib-title {
  font-family: 'Inter', sans-serif;
  font-size: 13px; font-weight: 700;
  color: #60A5FA; margin-bottom: 7px;
}
.mib-body {
  font-size: 13.5px; color: var(--text-muted);
  line-height: 1.75;
}
.mib-body strong { color: var(--text-secondary); font-weight: 600; }

/* ── Chart section cards ─────────────────────────────────────────────────── */
.chart-section {
  background: var(--bg-card);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: var(--radius-xl);
  padding: 22px 20px;
  margin-bottom: 16px;
  transition: all var(--transition);
}
.chart-section:hover {
  border-color: rgba(59,130,246,0.2);
  box-shadow: var(--shadow-md);
}

/* ── SMOTE bars hover ────────────────────────────────────────────────────── */
.smote-row {
  margin-bottom: 8px;
  padding: 8px 10px;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: all var(--transition);
}
.smote-row:hover {
  background: rgba(255,255,255,0.03);
  border-color: rgba(255,255,255,0.07);
  transform: translateX(2px);
}
</style>
"""


def render(feat, imp, filtered_feat, filtered_imp, shap_df):

    st.markdown(_MARKET_STYLES, unsafe_allow_html=True)
    st.markdown('<div class="cw">', unsafe_allow_html=True)
    st.markdown(
        page_header(
            "01 / Market Intelligence",
            "Market Pulse",
            "Segment distribution, revenue landscape, and placement quality across the full catalogue.",
        ),
        unsafe_allow_html=True,
    )

    # ── Computed values ───────────────────────────────────────────────────────
    n_products  = len(filtered_feat)
    n_correct   = int((filtered_feat["mismatch_flag"] == 0).sum())
    pct_correct = (n_correct / n_products * 100) if n_products else 0
    mean_uplift = filtered_feat["revenue_uplift"].mean() if n_products else 0
    total_leak  = filtered_feat["mismatch_revenue_loss"].sum()
    n_mismatch  = n_products - n_correct

    # ── ROW 0 — Contextual insight banner ─────────────────────────────────────
    leak_pct = (total_leak / (total_leak + mean_uplift * n_products) * 100) if (total_leak + mean_uplift * n_products) > 0 else 0
    st.markdown(f"""
    <div class="market-insight-banner">
      <div class="mib-title">📊 Market Snapshot — Filtered View</div>
      <div class="mib-body">
        Showing <strong>{n_products:,} products</strong> —
        <strong style="color:#FCA5A5;">{n_mismatch:,} misplaced ({100-pct_correct:.1f}%)</strong>
        contributing <strong style="color:#FCA5A5;">{fmt_inr(total_leak)}</strong> in monthly leakage.
        Average revenue opportunity of <strong style="color:#6EE7B7;">{fmt_inr(mean_uplift)}</strong>
        per product with correct placement. Adjust sidebar filters to drill into specific categories or segments.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ROW 1 — 4 KPI cards ───────────────────────────────────────────────────
    st.markdown(
        f'<div class="kpi-grid-4">'
        + kpi_card("Products in View",    f"{n_products:,}",      "of 1,463 total",          "orange")
        + kpi_card("Correct Placements",  f"{pct_correct:.1f}%",  f"{n_correct:,} products", "blue")
        + kpi_card("Avg Rev Opportunity", fmt_inr(mean_uplift),   "per product",             "green")
        + kpi_card("Revenue Leakage",     fmt_inr(total_leak),    "mismatch loss",           "red")
        + '</div>',
        unsafe_allow_html=True,
    )

    # ── ROW 2 — Bar + Heatmap ─────────────────────────────────────────────────
    col_a, col_b = st.columns([1.2, 1])
    with col_a:
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        st.markdown(sec_div("Buyer Segment Distribution by Category"), unsafe_allow_html=True)
        st.plotly_chart(seg_by_category_bar(filtered_feat), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        st.markdown(sec_div("Revenue Opportunity Heatmap (₹L avg)"), unsafe_allow_html=True)
        st.plotly_chart(revenue_heatmap(filtered_feat), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 3 — Violin + Scatter ──────────────────────────────────────────────
    col_c, col_d = st.columns([1, 1])
    with col_c:
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        st.markdown(sec_div("Discount Depth by Segment"), unsafe_allow_html=True)
        st.plotly_chart(discount_violin(filtered_feat), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_d:
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        st.markdown(sec_div("Price vs Rating — Segment Clusters"), unsafe_allow_html=True)
        st.plotly_chart(price_rating_scatter(filtered_feat), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 4 — Treemap ───────────────────────────────────────────────────────
    st.markdown('<div class="chart-section">', unsafe_allow_html=True)
    st.markdown(sec_div("Revenue Treemap — Category × Segment Opportunity"), unsafe_allow_html=True)
    st.plotly_chart(revenue_treemap(filtered_feat), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 5 — Top 20 table ──────────────────────────────────────────────────
    st.markdown(sec_div("Top 20 Products by Revenue Opportunity"), unsafe_allow_html=True)

    if "revenue_uplift" not in filtered_imp.columns:
        disp = filtered_imp.merge(
            filtered_feat[["product_id", "revenue_uplift", "mismatch_flag"]].drop_duplicates("product_id"),
            on="product_id", how="left",
        )
    else:
        disp = filtered_imp.copy()

    disp    = disp.sort_values("revenue_uplift", ascending=False).head(20)
    seg_col = "pred_segment" if "pred_segment" in disp.columns else "segment"

    rows = []
    for _, r in disp.iterrows():
        seg  = str(r.get(seg_col, r.get("segment", "UNMATCHED")))
        flag = int(r.get("mismatch_flag", 0))
        rows.append({
            "Product Name":    str(r.get("product_name", r.get("product_id", "")))[:62],
            "Category":        str(r.get("top_cat", "—")),
            "Segment":         seg,
            "Price (₹)":       float(r.get("price_disc", 0)),
            "Discount":        float(r.get("discount_pct", 0)),
            "Rating":          float(r.get("rating", 0)),
            "Rev Opportunity": float(r.get("revenue_uplift", 0)),
            "Status":          "⚠ Mismatch" if flag else "✓ Aligned",
        })

    table_df = pd.DataFrame(rows)

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Product Name": st.column_config.TextColumn("Product Name", help="Truncated to 62 chars", width="large"),
            "Category":     st.column_config.TextColumn("Category", width="small"),
            "Segment":      st.column_config.TextColumn("Segment", help="Buyer archetype assigned by the ML model", width="medium"),
            "Price (₹)":    st.column_config.NumberColumn("Price (₹)", format="₹%,.0f", help="Discounted selling price", width="small"),
            "Discount":     st.column_config.NumberColumn("Discount", format="%.0f%%", help="Discount percentage off MRP", width="small"),
            "Rating":       st.column_config.NumberColumn("Rating", format="%.1f ★", min_value=0.0, max_value=5.0, help="Average star rating", width="small"),
            "Rev Opportunity": st.column_config.ProgressColumn(
                "Rev Opportunity",
                help="Estimated monthly revenue uplift with correct placement",
                format="₹%.0f",
                min_value=0,
                max_value=float(table_df["Rev Opportunity"].max()) if len(table_df) else 1,
                width="medium",
            ),
            "Status": st.column_config.TextColumn("Status", help="✓ = correctly placed · ⚠ = mismatched placement", width="small"),
        },
    )

    st.markdown('</div>', unsafe_allow_html=True)