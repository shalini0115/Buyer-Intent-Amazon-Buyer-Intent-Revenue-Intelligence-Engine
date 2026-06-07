"""
app.py — Amazon Buyer Intent Intelligence Platform
Main entry point: page config, CSS injection, sidebar nav, data loading, routing.
"""

import streamlit as st

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="◈ Buyer Intent Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from utils.style import (
    CSS, SEG_COLORS, SEG_ICONS, SEG_TAGLINES, fmt_inr,
)
from utils.data_loader import load_all, load_shap, apply_filters

# ── Inject CSS once ───────────────────────────────────────────────────────────
st.markdown(CSS, unsafe_allow_html=True)

# ── Load data once (cached) ───────────────────────────────────────────────────
feat, imp = load_all("data")
shap_df   = load_shap("data")

# ── Apply global derived stats ────────────────────────────────────────────────
total_products    = len(feat)
total_uplift      = feat["revenue_uplift"].sum()
total_leakage     = feat["mismatch_revenue_loss"].sum()
n_mismatched      = int(feat["mismatch_flag"].sum())

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Brand logo
    st.markdown("""
    <div class="brand-mark">
      <div class="brand-icon">◈</div>
      <div>
        <div class="brand-text-main">Buyer Intent</div>
        <div class="brand-text-sub">Intelligence Platform</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown('<span class="nav-label">Navigation</span>', unsafe_allow_html=True)
    NAV_OPTIONS = [
        "🏠  Home",
        "📊  Market Intelligence",
        "🧠  ML Engine Room",
        "🔬  Explainability Studio",
        "🚨  Mismatch Alerts",
        "🧬  Buyer DNA",
        "🔍  Product Intelligence",
    ]
    page = st.selectbox("", NAV_OPTIONS, label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Category filter
    st.markdown('<span class="nav-label">Filter — Category</span>', unsafe_allow_html=True)
    all_cats = sorted(feat["top_cat"].dropna().unique().tolist())
    sel_cats = st.multiselect(
        "",
        options=all_cats,
        default=all_cats,
        label_visibility="collapsed",
    )

    # Segment filter
    st.markdown('<span class="nav-label">Filter — Segment</span>', unsafe_allow_html=True)
    all_segs = list(SEG_COLORS.keys())
    default_segs = [s for s in all_segs if s != "UNMATCHED"]
    sel_segs = st.multiselect(
        "",
        options=all_segs,
        default=default_segs,
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # Dataset stats
    st.markdown('<span class="nav-label">Dataset Stats</span>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sidebar-stat">
      <div class="sidebar-stat-val">{total_products:,}</div>
      <div class="sidebar-stat-label">Total Products</div>
    </div>
    <div class="sidebar-stat">
      <div class="sidebar-stat-val">{len(SEG_COLORS)}</div>
      <div class="sidebar-stat-label">Buyer Segments</div>
    </div>
    <div class="sidebar-stat">
      <div class="sidebar-stat-val">{fmt_inr(total_uplift)}</div>
      <div class="sidebar-stat-label">Revenue Opportunity</div>
    </div>
    <div class="sidebar-stat">
      <div class="sidebar-stat-val">{fmt_inr(total_leakage)}</div>
      <div class="sidebar-stat-label">Mismatch Leakage</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered_feat = apply_filters(feat, sel_cats, sel_segs)
filtered_imp  = apply_filters(imp,  sel_cats, sel_segs,
                               cat_col="top_cat", seg_col="segment")

# ── Page routing ──────────────────────────────────────────────────────────────
if page == "🏠  Home":
    from pages.p0_home import render
elif page == "📊  Market Intelligence":
    from pages.p1_market import render
elif page == "🧠  ML Engine Room":
    from pages.p2_model import render
elif page == "🔬  Explainability Studio":
    from pages.p3_shap import render
elif page == "🚨  Mismatch Alerts":
    from pages.p4_mismatch import render
elif page == "🧬  Buyer DNA":
    from pages.p5_dna import render
elif page == "🔍  Product Intelligence":
    from pages.p6_product import render

render(feat, imp, filtered_feat, filtered_imp, shap_df)