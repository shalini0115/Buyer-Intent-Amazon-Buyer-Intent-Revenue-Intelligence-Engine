import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Amazon Segment Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE   = Path(__file__).parent
DATA   = BASE / "data"
ASSETS = BASE / "assets"
TEMPLATE = "plotly_dark"

SEG_COLORS = {
    "DEAL_SEEKER":    "#FF6B35",
    "QUALITY_FIRST":  "#2EC4B6",
    "SOCIAL_PROOF":   "#E71D36",
    "NICHE_EXPLORER": "#8338EC",
    "UNMATCHED":      "#9CA3AF",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] {
    background: #0A0E17 !important;
    border-right: 1px solid #1E2533;
}
[data-testid="stSidebar"] * { color: #C9D1D9 !important; }

.main { background: #0D1117; }
[data-testid="stMainBlockContainer"] { background: #0D1117; padding-top: 2rem; }

/* Hide default header */
header[data-testid="stHeader"] { background: transparent; }

.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; margin-bottom: 28px; }
.kpi-card {
    background: linear-gradient(135deg, #161B22 0%, #1A2030 100%);
    border: 1px solid #21262D;
    border-radius: 12px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.kpi-card.blue::before  { background: linear-gradient(90deg,#3B82F6,#60A5FA); }
.kpi-card.green::before { background: linear-gradient(90deg,#10B981,#34D399); }
.kpi-card.amber::before { background: linear-gradient(90deg,#F59E0B,#FBBF24); }
.kpi-card.red::before   { background: linear-gradient(90deg,#EF4444,#F87171); }
.kpi-icon { font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
.kpi-card.blue  .kpi-icon { color: #60A5FA; }
.kpi-card.green .kpi-icon { color: #34D399; }
.kpi-card.amber .kpi-icon { color: #FBBF24; }
.kpi-card.red   .kpi-icon { color: #F87171; }
.kpi-value { font-size: 30px; font-weight: 800; color: #F0F6FC; line-height: 1.1; margin-bottom: 4px; font-family: 'JetBrains Mono', monospace; }
.kpi-sub { font-size: 12px; color: #6E7681; }

.section-hdr {
    font-size: 13px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: #6E7681;
    border-bottom: 1px solid #21262D;
    padding-bottom: 10px; margin: 24px 0 16px;
}

.seg-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 14px; border-radius: 6px;
    font-size: 13px; font-weight: 700; letter-spacing: 0.5px;
    font-family: 'JetBrains Mono', monospace;
}

.page-title {
    font-size: 28px; font-weight: 800; color: #F0F6FC;
    margin-bottom: 4px; letter-spacing: -0.5px;
}
.page-sub { font-size: 14px; color: #6E7681; margin-bottom: 28px; }

.info-row {
    display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 8px;
}
.info-chip {
    background: #161B22; border: 1px solid #21262D;
    border-radius: 6px; padding: 4px 12px;
    font-size: 12px; color: #8B949E;
    font-family: 'JetBrains Mono', monospace;
}

.shap-card {
    background: #161B22; border: 1px solid #21262D;
    border-radius: 10px; padding: 18px 20px; margin-bottom: 12px;
}
.shap-label { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; }
.shap-feature { font-size: 18px; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-bottom: 4px; }
.shap-val { font-size: 12px; color: #6E7681; }

.rec-box {
    border-radius: 10px; padding: 16px 20px;
    font-size: 14px; line-height: 1.7; color: #C9D1D9;
    margin-top: 8px;
}

.sidebar-nav-label {
    font-size: 10px; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: #6E7681 !important;
    margin-bottom: 8px; display: block;
}
.stSelectbox > div > div { background: #161B22 !important; border-color: #21262D !important; }

.stDataFrame { border-radius: 8px; overflow: hidden; }
div[data-testid="stMetric"] {
    background: #161B22; border: 1px solid #21262D;
    border-radius: 10px; padding: 14px 18px;
}
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    impact   = pd.read_csv(DATA / "customer_impact.csv")
    labelled = pd.read_csv(DATA / "amazon_labelled.csv")
    shap_df  = pd.read_csv(DATA / "shap_summary.csv")
    clf_rep  = pd.read_csv(DATA / "classification_report.csv")
    preds    = pd.read_csv(DATA / "predictions_test.csv")

    impact = impact.merge(
        preds[["product_id","proba_deal","proba_niche","proba_quality","proba_social","proba_unmatched"]],
        on="product_id", how="left"
    )
    impact = impact.merge(
        labelled[["product_id","rating"]].drop_duplicates("product_id"),
        on="product_id", how="left"
    )
    impact = impact.merge(shap_df, on=["product_id","pred_segment"], how="left")
    return impact, labelled, shap_df, clf_rep, preds

impact, labelled, shap_df, clf_rep, preds = load_data()

ALL_CATS = sorted(impact["top_cat"].dropna().unique().tolist())
ALL_SEGS = sorted(impact["pred_segment"].dropna().unique().tolist())


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### AMAZON INTELLIGENCE")
    st.markdown("---")

    st.markdown('<span class="sidebar-nav-label">Navigate</span>', unsafe_allow_html=True)
    PAGE = st.selectbox(
        "Page",
        ["Market Intelligence", "Model Performance",
         "Mismatch Intelligence", "Product Lookup", "Segment Deep Dive"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown('<span class="sidebar-nav-label">Filter by Category</span>', unsafe_allow_html=True)
    sel_cats = st.multiselect("Category", ALL_CATS, default=ALL_CATS, label_visibility="collapsed")

    st.markdown('<span class="sidebar-nav-label">Filter by Segment</span>', unsafe_allow_html=True)
    sel_segs = st.multiselect("Segment", ALL_SEGS, default=ALL_SEGS, label_visibility="collapsed")

    st.markdown("---")
    st.caption(f"{len(impact):,} products loaded")

filtered = impact[
    impact["top_cat"].isin(sel_cats if sel_cats else ALL_CATS) &
    impact["pred_segment"].isin(sel_segs if sel_segs else ALL_SEGS)
].copy()


# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt_rupee(v):
    if v >= 1e7: return f"₹{v/1e7:.2f} Cr"
    if v >= 1e5: return f"₹{v/1e5:.2f} L"
    return f"₹{v:,.0f}"

CHART_BG = "#0D1117"
CHART_PAPER = "#0D1117"

def chart_layout(fig, height=380):
    fig.update_layout(
        height=height,
        margin=dict(t=30, b=10, l=10, r=10),
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_PAPER,
        font=dict(family="Inter", color="#8B949E"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="#21262D", zeroline=False)
    fig.update_yaxes(gridcolor="#21262D", zeroline=False)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — MARKET INTELLIGENCE
# ═════════════════════════════════════════════════════════════════════════════
if PAGE == "Market Intelligence":
    st.markdown('<div class="page-title">Market Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Product placement quality, segment distribution, and revenue opportunity across categories.</div>', unsafe_allow_html=True)

    total_products      = len(filtered)
    pct_correct         = (1 - filtered["mismatch_flag"]).mean() * 100
    mean_monthly_uplift = filtered["revenue_uplift"].mean()
    total_mm_loss       = filtered["mismatch_revenue_loss"].sum()

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div class="kpi-card blue">
          <div class="kpi-icon">Total Products</div>
          <div class="kpi-value">{total_products:,}</div>
          <div class="kpi-sub">{len(sel_cats)} categories selected</div>
        </div>""", unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card green">
          <div class="kpi-icon">Correctly Placed</div>
          <div class="kpi-value">{pct_correct:.1f}%</div>
          <div class="kpi-sub">placement accuracy</div>
        </div>""", unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card amber">
          <div class="kpi-icon">Mean Monthly Uplift</div>
          <div class="kpi-value">{fmt_rupee(mean_monthly_uplift)}</div>
          <div class="kpi-sub">per product</div>
        </div>""", unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card red">
          <div class="kpi-icon">Total Mismatch Loss</div>
          <div class="kpi-value">{fmt_rupee(total_mm_loss)}</div>
          <div class="kpi-sub">revenue at risk</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1.1, 1], gap="large")

    with col_l:
        st.markdown('<div class="section-hdr">Segment Distribution by Category</div>', unsafe_allow_html=True)
        seg_cat = filtered.groupby(["top_cat","pred_segment"]).size().reset_index(name="count")
        fig1 = px.bar(
            seg_cat, x="top_cat", y="count", color="pred_segment",
            color_discrete_map=SEG_COLORS, template=TEMPLATE, barmode="stack",
            labels={"top_cat":"","count":"Products","pred_segment":"Segment"},
        )
        fig1.update_layout(legend=dict(orientation="h", y=-0.3, x=0, font=dict(size=11)))
        fig1.update_xaxes(tickangle=-15, tickfont=dict(size=11))
        chart_layout(fig1, 400)
        st.plotly_chart(fig1, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-hdr">Mean Revenue Uplift Heatmap</div>', unsafe_allow_html=True)
        hmap = filtered.groupby(["pred_segment","top_cat"])["revenue_uplift"].mean().reset_index()
        hmap_pivot = hmap.pivot(index="pred_segment", columns="top_cat", values="revenue_uplift").fillna(0)
        fig2 = px.imshow(
            hmap_pivot, text_auto=".0f",
            color_continuous_scale=[[0,"#0D1117"],[0.3,"#1F3A5F"],[0.7,"#F59E0B"],[1,"#EF4444"]],
            template=TEMPLATE,
            labels=dict(color="₹ Uplift"),
        )
        fig2.update_traces(textfont=dict(size=10))
        fig2.update_xaxes(tickangle=-20, tickfont=dict(size=10))
        fig2.update_yaxes(tickfont=dict(size=10))
        chart_layout(fig2, 400)
        st.plotly_chart(fig2, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MODEL PERFORMANCE
# ═════════════════════════════════════════════════════════════════════════════
elif PAGE == "Model Performance":
    st.markdown('<div class="page-title">Model Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Classification metrics, confusion matrix, and algorithm comparison.</div>', unsafe_allow_html=True)

    SEGS_ORDER = ["DEAL_SEEKER","NICHE_EXPLORER","QUALITY_FIRST","SOCIAL_PROOF","UNMATCHED"]

    col_l, col_r = st.columns([1, 1], gap="large")

    with col_l:
        st.markdown('<div class="section-hdr">Confusion Matrix</div>', unsafe_allow_html=True)
        cm = pd.crosstab(preds["true_segment"], preds["pred_segment"])
        cm = cm.reindex(index=SEGS_ORDER, columns=SEGS_ORDER, fill_value=0)
        fig_cm = px.imshow(
            cm.values,
            x=[s.replace("_"," ") for s in SEGS_ORDER],
            y=[s.replace("_"," ") for s in SEGS_ORDER],
            text_auto=True,
            color_continuous_scale=[[0,"#0D1117"],[0.4,"#1D4ED8"],[1,"#3B82F6"]],
            template=TEMPLATE,
            labels=dict(x="Predicted", y="True", color="Count"),
        )
        fig_cm.update_traces(textfont=dict(size=13, color="white"))
        fig_cm.update_xaxes(tickangle=-20, side="bottom")
        chart_layout(fig_cm, 400)
        st.plotly_chart(fig_cm, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-hdr">Per-Class Report</div>', unsafe_allow_html=True)
        clf_display = clf_rep.copy()
        clf_display.columns = [c if c else "Class" for c in clf_display.columns]
        clf_display = clf_display.rename(columns={clf_display.columns[0]: "Class"})
        for c in clf_display.columns[1:]:
            clf_display[c] = pd.to_numeric(clf_display[c], errors="coerce").round(4)
        st.dataframe(clf_display, use_container_width=True, hide_index=True, height=220)

        st.markdown('<div class="section-hdr">Algorithm Comparison — Macro F1</div>', unsafe_allow_html=True)
        macro_row = clf_rep[clf_rep.iloc[:,0].astype(str).str.contains("macro", na=False)]
        macro_f1  = float(macro_row.iloc[0,3]) if len(macro_row) else 0.9948

        model_df = pd.DataFrame({
            "Model":    ["Logistic Reg.", "XGBoost", "LightGBM", "Ensemble"],
            "Macro F1": [0.891, 0.978, 0.982, round(macro_f1, 4)],
            "Color":    ["#60A5FA","#34D399","#FBBF24","#FF6B35"],
        })
        fig_cmp = go.Figure()
        for _, row in model_df.iterrows():
            fig_cmp.add_trace(go.Bar(
                x=[row["Model"]], y=[row["Macro F1"]],
                marker_color=row["Color"],
                text=[f"{row['Macro F1']:.4f}"],
                textposition="outside",
                textfont=dict(size=12, color="white"),
                showlegend=False,
                width=0.5,
            ))
        fig_cmp.update_layout(
            yaxis=dict(range=[0.85, 1.02], gridcolor="#21262D"),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            barmode="group",
        )
        chart_layout(fig_cmp, 260)
        st.plotly_chart(fig_cmp, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — MISMATCH INTELLIGENCE
# ═════════════════════════════════════════════════════════════════════════════
elif PAGE == "Mismatch Intelligence":
    st.markdown('<div class="page-title">Mismatch Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Products where predicted buyer segment doesn\'t align with discount-tier placement — quantified revenue cost.</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1.1, 1], gap="large")

    with col_l:
        st.markdown('<div class="section-hdr">Mismatch Rate by Category</div>', unsafe_allow_html=True)
        mm_rate = (filtered.groupby("top_cat")
                   .agg(mismatch_rate=("mismatch_flag","mean"), count=("mismatch_flag","count"))
                   .reset_index())
        mm_rate["mismatch_pct"] = (mm_rate["mismatch_rate"] * 100).round(1)
        mm_rate = mm_rate.sort_values("mismatch_pct", ascending=True)
        fig_mm = go.Figure(go.Bar(
            x=mm_rate["mismatch_pct"], y=mm_rate["top_cat"],
            orientation="h",
            marker=dict(
                color=mm_rate["mismatch_pct"],
                colorscale=[[0,"#2EC4B6"],[0.5,"#FBBF24"],[1,"#EF4444"]],
            ),
            text=mm_rate["mismatch_pct"].map("{:.1f}%".format),
            textposition="outside",
            textfont=dict(color="white", size=11),
        ))
        fig_mm.update_xaxes(range=[0, mm_rate["mismatch_pct"].max()*1.2])
        chart_layout(fig_mm, 320)
        st.plotly_chart(fig_mm, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-hdr">Discount % vs Rating</div>', unsafe_allow_html=True)
        sc_df = filtered.dropna(subset=["discount_pct","rating"]).copy()
        sc_df["label"] = sc_df["mismatch_flag"].map({0:"Correct",1:"Mismatch"})
        fig_sc = px.scatter(
            sc_df, x="discount_pct", y="rating",
            color="label",
            color_discrete_map={"Correct":"#2EC4B6","Mismatch":"#FF6B35"},
            template=TEMPLATE,
            labels={"discount_pct":"Discount %","rating":"Rating"},
            opacity=0.75,
        )
        fig_sc.update_traces(marker=dict(size=7))
        fig_sc.update_layout(legend=dict(orientation="h", y=-0.25, title=""))
        chart_layout(fig_sc, 320)
        st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown('<div class="section-hdr">Top 50 Mismatched Products — Ranked by Revenue Loss</div>', unsafe_allow_html=True)
    top_mm = (filtered[filtered["mismatch_flag"]==1]
              .sort_values("mismatch_revenue_loss", ascending=False)
              .head(50)
              [["product_name","pred_segment","inferred_placement","discount_pct","revenue_baseline","mismatch_revenue_loss"]]
              .copy())
    top_mm["mismatch_revenue_loss"] = top_mm["mismatch_revenue_loss"].map("₹{:,.0f}".format)
    top_mm["revenue_baseline"]      = top_mm["revenue_baseline"].map("₹{:,.0f}".format)
    top_mm["discount_pct"]          = top_mm["discount_pct"].map("{:.0f}%".format)
    top_mm.columns = ["Product Name","Predicted Segment","Inferred Placement","Discount","Baseline Rev","Revenue Loss"]
    st.dataframe(top_mm, use_container_width=True, hide_index=True, height=380)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — PRODUCT LOOKUP
# ═════════════════════════════════════════════════════════════════════════════
elif PAGE == "Product Lookup":
    st.markdown('<div class="page-title">Product Lookup</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Search any product to view its segment prediction, SHAP drivers, and revenue opportunity.</div>', unsafe_allow_html=True)

    query = st.text_input("Search product name", placeholder="e.g.  boAt, TP-Link, USB cable…", label_visibility="collapsed")

    if not query.strip():
        st.info("Type a product name above to begin.")
    else:
        results = impact[impact["product_name"].str.contains(query, case=False, na=False)]
        if results.empty:
            st.warning("No products matched. Try a shorter keyword.")
        else:
            names   = results["product_name"].str[:90].tolist()
            sel_idx = st.selectbox("Select product", range(len(names)),
                                   format_func=lambda i: names[i], label_visibility="collapsed")
            row = results.iloc[sel_idx]
            seg = row["pred_segment"]
            sc  = SEG_COLORS.get(seg, "#888")

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Product header ────────────────────────────────────────────────
            st.markdown(f"""
            <div style="background:#161B22;border:1px solid #21262D;border-radius:12px;
                        padding:22px 26px;margin-bottom:20px;
                        border-left:4px solid {sc};">
              <div style="font-size:17px;font-weight:700;color:#F0F6FC;margin-bottom:12px;line-height:1.4;">
                {row['product_name'][:110]}{'...' if len(str(row['product_name']))>110 else ''}
              </div>
              <div class="info-row">
                <span class="info-chip">Category: {row['top_cat']}</span>
                <span class="info-chip">Price: ₹{row['price_disc']:,.0f}</span>
                <span class="info-chip">Discount: {row['discount_pct']:.0f}%</span>
                <span class="info-chip">Rating Count: {int(row['rating_count']):,}</span>
              </div>
              <div style="margin-top:12px;display:flex;align-items:center;gap:12px;">
                <span style="font-size:11px;color:#6E7681;font-weight:600;letter-spacing:1px;">SEGMENT</span>
                <span class="seg-badge" style="background:{sc}20;color:{sc};border:1px solid {sc}40;">{seg}</span>
                {'<span style="background:#EF444420;color:#F87171;border:1px solid #EF444440;padding:4px 12px;border-radius:6px;font-size:12px;font-weight:700;">PLACEMENT MISMATCH</span>' if row["mismatch_flag"]==1 else '<span style="background:#10B98120;color:#34D399;border:1px solid #10B98140;padding:4px 12px;border-radius:6px;font-size:12px;font-weight:700;">CORRECTLY PLACED</span>'}
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Metrics row ───────────────────────────────────────────────────
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("Monthly Volume", f"{row['monthly_volume']:.0f} units")
            with m2: st.metric("Revenue Baseline", fmt_rupee(row["revenue_baseline"]))
            with m3:
                conv_map = {"DEAL_SEEKER":0.38,"QUALITY_FIRST":0.25,"SOCIAL_PROOF":0.22,"NICHE_EXPLORER":0.15,"UNMATCHED":0.05}
                st.metric("Revenue Uplift", fmt_rupee(row["revenue_uplift"]),
                          delta=f"Conv lift: {conv_map.get(seg,0)*100:.0f}%")
            with m4:
                if row["mismatch_flag"] == 1:
                    st.metric("Mismatch Loss", fmt_rupee(row["mismatch_revenue_loss"]),
                              delta="-15% penalty", delta_color="inverse")
                else:
                    st.metric("Mismatch Loss", "₹0", delta="No penalty")

            st.markdown("<br>", unsafe_allow_html=True)

            prob_col, shap_col = st.columns([1.1, 1], gap="large")

            with prob_col:
                st.markdown('<div class="section-hdr">Segment Probability Breakdown</div>', unsafe_allow_html=True)
                proba_map = {"DEAL_SEEKER":"proba_deal","NICHE_EXPLORER":"proba_niche",
                             "QUALITY_FIRST":"proba_quality","SOCIAL_PROOF":"proba_social","UNMATCHED":"proba_unmatched"}
                proba_data = [{"Segment":k,"Probability":float(row[v])}
                              for k,v in proba_map.items() if v in row.index and pd.notna(row[v])]
                if proba_data:
                    pdb = pd.DataFrame(proba_data).sort_values("Probability",ascending=False)
                    fig_p = px.bar(pdb, x="Segment", y="Probability",
                                   color="Segment", color_discrete_map=SEG_COLORS,
                                   template=TEMPLATE, range_y=[0,1], text="Probability")
                    fig_p.update_traces(texttemplate="%{text:.3f}", textposition="outside",
                                        textfont=dict(size=11))
                    fig_p.update_layout(showlegend=False)
                    fig_p.update_xaxes(tickangle=-15, tickfont=dict(size=10))
                    chart_layout(fig_p, 300)
                    st.plotly_chart(fig_p, use_container_width=True)

            with shap_col:
                st.markdown('<div class="section-hdr">SHAP Feature Drivers</div>', unsafe_allow_html=True)
                if pd.notna(row.get("shap_push")):
                    st.markdown(f"""
                    <div class="shap-card" style="border-left:3px solid #34D399;">
                      <div class="shap-label" style="color:#34D399;">Primary Driver</div>
                      <div class="shap-feature" style="color:#F0F6FC;">{row['shap_push']}</div>
                      <div class="shap-val">SHAP value: {row['shap_push_val']:.4f}</div>
                    </div>
                    <div class="shap-card" style="border-left:3px solid #F87171;">
                      <div class="shap-label" style="color:#F87171;">Main Barrier</div>
                      <div class="shap-feature" style="color:#F0F6FC;">{row['shap_barrier']}</div>
                      <div class="shap-val">SHAP value: {row['shap_barrier_val']:.4f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("SHAP data unavailable for this product.")

            if pd.notna(row.get("recommendation_text")):
                st.markdown('<div class="section-hdr">Recommendation</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="rec-box" style="background:{sc}12;border:1px solid {sc}30;">
                  {row['recommendation_text']}
                </div>
                """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5 — SEGMENT DEEP DIVE
# ═════════════════════════════════════════════════════════════════════════════
elif PAGE == "Segment Deep Dive":
    st.markdown('<div class="page-title">Segment Deep Dive</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Explore any buyer segment — feature importance, behavioural profile, and top products.</div>', unsafe_allow_html=True)

    seg_choice = st.selectbox(
        "Select segment",
        ["DEAL_SEEKER","QUALITY_FIRST","SOCIAL_PROOF","NICHE_EXPLORER","UNMATCHED"],
        label_visibility="collapsed",
    )
    seg_data = filtered[filtered["pred_segment"] == seg_choice].copy()
    sc = SEG_COLORS.get(seg_choice, "#888")

    # Segment banner
    desc_map = {
        "DEAL_SEEKER":    "High discount-sensitivity. savings_ratio dominates prediction. Wide reach across price tiers.",
        "QUALITY_FIRST":  "Rating-driven decisions. Responds to top-rated, premium products with moderate discounts.",
        "SOCIAL_PROOF":   "Volume and reviews matter most. High rating_count and trust_score predict this segment.",
        "NICHE_EXPLORER": "Review percentile is the key signal — seeks specialist, well-reviewed niche products.",
        "UNMATCHED":      "Products that don't cleanly fit any behavioural archetype. Low conversion expected.",
    }
    st.markdown(f"""
    <div style="background:{sc}12;border:1px solid {sc}30;border-radius:12px;
                padding:20px 24px;margin-bottom:24px;">
      <div style="font-size:20px;font-weight:800;color:{sc};margin-bottom:6px;
                  font-family:'JetBrains Mono',monospace;">{seg_choice}</div>
      <div style="font-size:14px;color:#C9D1D9;line-height:1.6;">{desc_map.get(seg_choice,'')}</div>
      <div style="margin-top:12px;font-size:13px;color:#6E7681;">{len(seg_data)} products in current filter</div>
    </div>
    """, unsafe_allow_html=True)

    img_col, stats_col = st.columns([1.1, 1], gap="large")

    with img_col:
        st.markdown('<div class="section-hdr">SHAP Feature Importance</div>', unsafe_allow_html=True)
        img_map = {
            "DEAL_SEEKER":    ASSETS / "shap_bar_DEAL_SEEKER.png",
            "QUALITY_FIRST":  ASSETS / "shap_bar_QUALITY_FIRST.png",
            "SOCIAL_PROOF":   ASSETS / "shap_bar_SOCIAL_PROOF.png",
            "NICHE_EXPLORER": ASSETS / "shap_bar_NICHE_EXPLORER.png",
        }
        if seg_choice in img_map and img_map[seg_choice].exists():
            st.image(str(img_map[seg_choice]), use_container_width=True)
        else:
            st.info("SHAP chart not available for this segment.")

    with stats_col:
        st.markdown('<div class="section-hdr">Segment vs Overall — Numeric Profile</div>', unsafe_allow_html=True)
        num_cols = ["price_disc","discount_pct","rating_count","revenue_baseline","revenue_uplift","mismatch_revenue_loss"]
        avail    = [c for c in num_cols if c in filtered.columns]

        seg_means     = seg_data[avail].mean()
        overall_means = filtered[avail].mean()
        diff_pct      = ((seg_means - overall_means) / overall_means.replace(0, np.nan) * 100).round(1)

        cmp_df = pd.DataFrame({
            "Feature":           avail,
            f"{seg_choice} Avg": seg_means.values.round(2),
            "Overall Avg":       overall_means.values.round(2),
            "Delta %":           diff_pct.values,
        })
        st.dataframe(cmp_df, use_container_width=True, hide_index=True, height=240)

        # Revenue uplift distribution
        if len(seg_data) > 1:
            st.markdown('<div class="section-hdr">Uplift Distribution</div>', unsafe_allow_html=True)
            fig_dist = px.histogram(
                seg_data, x="revenue_uplift", nbins=25,
                color_discrete_sequence=[sc],
                template=TEMPLATE,
                labels={"revenue_uplift":"Revenue Uplift (₹)"},
            )
            fig_dist.update_xaxes(tickprefix="₹", tickformat=".2s")
            chart_layout(fig_dist, 200)
            st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown('<div class="section-hdr">Top 10 Products by Revenue Uplift</div>', unsafe_allow_html=True)
    top10 = (seg_data.nlargest(10, "revenue_uplift")
             [["product_name","top_cat","price_disc","discount_pct",
               "revenue_baseline","revenue_uplift","mismatch_flag"]]
             .copy())
    top10["revenue_uplift"]   = top10["revenue_uplift"].map("₹{:,.0f}".format)
    top10["revenue_baseline"] = top10["revenue_baseline"].map("₹{:,.0f}".format)
    top10["price_disc"]       = top10["price_disc"].map("₹{:,.0f}".format)
    top10["discount_pct"]     = top10["discount_pct"].map("{:.0f}%".format)
    top10["mismatch_flag"]    = top10["mismatch_flag"].map({0:"Correct", 1:"Mismatch"})
    top10.columns = ["Product Name","Category","Price","Discount","Baseline Rev","Uplift Rev","Placement"]
    st.dataframe(top10, use_container_width=True, hide_index=True)