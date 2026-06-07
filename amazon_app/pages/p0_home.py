import streamlit as st
import pandas as pd
from utils.style import (
    SEG_COLORS, SEG_ICONS, SEG_TAGLINES, SEG_DNA,
    page_header, kpi_strip_5, sec_div, fmt_inr,
)
from utils.charts import segment_donut


# ── Segment preview metadata ──────────────────────────────────────────────────
_SEG_SIGNALS = {
    "DEAL_SEEKER":    ("savings_ratio > 0.45", "Discount-first activation — loss aversion psychology"),
    "QUALITY_FIRST":  ("rating ≥ 4.3 + trust",  "Premium selective — discount paradox buyers"),
    "SOCIAL_PROOF":   ("review_log + crowd",      "Category Q75 reviews — Cialdini principle"),
    "NICHE_EXPLORER": ("category_depth ≥ 2",      "Expert self-selection via listing specificity"),
}

_WALK_TILES = [
    ("📊", "Market Pulse",         "01", "Segment distribution, revenue landscape, and placement quality across all categories."),
    ("🧠", "ML Engine",            "02", "XGBoost ensemble achieving Macro-F1 = 0.9948 on 5-class imbalanced data."),
    ("🔬", "Explainability",       "03", "SHAP bar, beeswarm, waterfall — the discount paradox visualised."),
    ("🚨", "Mismatch Alerts",      "04", "611 misplaced products · ₹4.97 Cr monthly leakage diagnosed by SHAP."),
    ("🧬", "Buyer DNA",            "05", "Deep-dive into any buyer archetype — fingerprint, radar, top products."),
    ("🔍", "Product Intelligence", "06", "Search any product — decode classification and simulate segment upgrades."),
]

# ── Page-scoped CSS + keyframes ───────────────────────────────────────────────
_HOME_STYLES = """
<style>
/* ── Animated gradient mesh ──────────────────────────────────────────────── */
@keyframes meshFloat1 {
  0%,100% { transform: translate(0,0) scale(1); }
  33%      { transform: translate(30px,-20px) scale(1.07); }
  66%      { transform: translate(-15px,25px) scale(0.96); }
}
@keyframes meshFloat2 {
  0%,100% { transform: translate(0,0) scale(1); }
  40%      { transform: translate(-25px,15px) scale(1.09); }
  75%      { transform: translate(20px,-30px) scale(0.93); }
}
@keyframes meshFloat3 {
  0%,100% { transform: translate(0,0) scale(1); }
  50%      { transform: translate(18px,22px) scale(1.06); }
}
@keyframes heroReveal {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes pillReveal {
  from { opacity: 0; transform: translateY(-8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes kpiCount {
  from { opacity: 0; transform: translateY(10px) scale(0.96); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes staggerIn {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Hero mesh orbs ──────────────────────────────────────────────────────── */
.hero-mesh {
  position: absolute; inset: 0;
  pointer-events: none; overflow: hidden; z-index: 0;
}
.mesh-orb {
  position: absolute; border-radius: 50%;
  filter: blur(80px); opacity: 0.5;
}
.mesh-orb-1 {
  width: 520px; height: 520px;
  background: radial-gradient(circle, rgba(59,130,246,0.2) 0%, transparent 70%);
  top: -130px; right: -80px;
  animation: meshFloat1 16s ease-in-out infinite;
}
.mesh-orb-2 {
  width: 380px; height: 380px;
  background: radial-gradient(circle, rgba(20,184,166,0.14) 0%, transparent 70%);
  bottom: -90px; left: 200px;
  animation: meshFloat2 20s ease-in-out infinite;
}
.mesh-orb-3 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 70%);
  top: 40px; left: -60px;
  animation: meshFloat3 24s ease-in-out infinite;
}
.hero-content {
  position: relative; z-index: 1;
  animation: heroReveal 0.6s cubic-bezier(0.4,0,0.2,1) backwards;
}

/* ── Hero pills stagger ──────────────────────────────────────────────────── */
.hero-pills .hero-pill:nth-child(1) { animation: pillReveal 0.4s 0.1s ease-out backwards; }
.hero-pills .hero-pill:nth-child(2) { animation: pillReveal 0.4s 0.18s ease-out backwards; }
.hero-pills .hero-pill:nth-child(3) { animation: pillReveal 0.4s 0.26s ease-out backwards; }
.hero-pills .hero-pill:nth-child(4) { animation: pillReveal 0.4s 0.34s ease-out backwards; }

/* ── KPI strip animated values ───────────────────────────────────────────── */
.kpi-strip .kpi-cell:nth-child(1) .kpi-val { animation: kpiCount 0.5s 0.20s ease-out backwards; }
.kpi-strip .kpi-cell:nth-child(2) .kpi-val { animation: kpiCount 0.5s 0.32s ease-out backwards; }
.kpi-strip .kpi-cell:nth-child(3) .kpi-val { animation: kpiCount 0.5s 0.44s ease-out backwards; }
.kpi-strip .kpi-cell:nth-child(4) .kpi-val { animation: kpiCount 0.5s 0.56s ease-out backwards; }
.kpi-strip .kpi-cell:nth-child(5) .kpi-val { animation: kpiCount 0.5s 0.68s ease-out backwards; }

/* ── KPI strip first-cell blue anchor ────────────────────────────────────── */
.kpi-strip .kpi-cell:first-child { border-top: 2px solid var(--accent-blue) !important; }

/* ── Walk tile hover arrow ───────────────────────────────────────────────── */
@keyframes arrowSlide {
  from { opacity: 0; transform: translateY(-50%) translateX(-6px); }
  to   { opacity: 1; transform: translateY(-50%) translateX(0); }
}
.walk-tile {
  display: block;
  background: var(--bg-card);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: var(--radius-lg);
  padding: 22px 20px;
  text-decoration: none !important;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: transform var(--transition), box-shadow var(--transition),
              border-color var(--transition), background var(--transition);
}
.walk-tile::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(59,130,246,0.04) 0%, transparent 60%);
  opacity: 0; pointer-events: none;
  transition: opacity var(--transition);
}
.walk-tile:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(59,130,246,0.1), var(--shadow-lg);
  border-color: rgba(59,130,246,0.28);
  background: var(--bg-hover);
}
.walk-tile:hover::before { opacity: 1; }
.walk-tile-arrow {
  position: absolute; right: 16px; top: 50%;
  transform: translateY(-50%) translateX(-4px);
  font-size: 16px; color: var(--text-faint);
  opacity: 0;
  transition: opacity var(--transition), transform var(--transition), color var(--transition);
}
.walk-tile:hover .walk-tile-arrow {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
  color: var(--accent-blue);
  animation: arrowSlide 0.2s ease-out;
}
.walk-tile-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px; color: var(--text-faint);
  letter-spacing: 0.14em; text-transform: uppercase;
  margin-bottom: 10px;
}
.walk-tile-icon { font-size: 24px; margin-bottom: 10px; }
.walk-tile-title {
  font-family: 'Inter', sans-serif;
  font-size: 13.5px; font-weight: 700;
  color: var(--text-secondary); margin-bottom: 6px;
  letter-spacing: -0.01em;
}
.walk-tile-desc {
  font-size: 12px; color: var(--text-faint); line-height: 1.65;
  padding-right: 22px;
}

/* ── Segment cards stagger on load ───────────────────────────────────────── */
.seg-preview-grid .seg-preview-card:nth-child(1) { animation: staggerIn 0.45s 0.1s ease-out backwards; }
.seg-preview-grid .seg-preview-card:nth-child(2) { animation: staggerIn 0.45s 0.2s ease-out backwards; }
.seg-preview-grid .seg-preview-card:nth-child(3) { animation: staggerIn 0.45s 0.3s ease-out backwards; }
.seg-preview-grid .seg-preview-card:nth-child(4) { animation: staggerIn 0.45s 0.4s ease-out backwards; }

/* ── Insight cards ───────────────────────────────────────────────────────── */
.insight-card {
  background: var(--bg-card);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: var(--radius-xl);
  padding: 22px 24px;
  margin-bottom: 14px;
  transition: all var(--transition);
  position: relative; overflow: hidden;
}
.insight-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
  background: var(--bg-card-alt);
}
.insight-card-title {
  font-family: 'Inter', sans-serif;
  font-size: 13.5px; font-weight: 700;
  margin-bottom: 10px;
  line-height: 1.4;
}
.insight-card-body {
  font-size: 13.5px; color: var(--text-muted);
  line-height: 1.75;
}
.insight-card-body strong { color: var(--text-secondary); font-weight: 600; }

/* ── PS cards override for home ──────────────────────────────────────────── */
.ps-grid { animation: staggerIn 0.4s 0.15s ease-out backwards; }

/* ── Section reveal ──────────────────────────────────────────────────────── */
.home-section { animation: staggerIn 0.4s ease-out backwards; }

/* ── Leakage banner pulse on load ────────────────────────────────────────── */
.leakage-banner { animation: staggerIn 0.5s 0.1s ease-out backwards; }
</style>
"""

# ── Animated KPI strip builder ────────────────────────────────────────────────
def _animated_kpi_strip(cells: list[dict]) -> str:
    """KPI strip with staggered entrance, animated values, blue anchor on first."""
    color_map = {
        "orange": "kpi-cell-orange", "blue":   "kpi-cell-blue",
        "purple": "kpi-cell-purple", "red":    "kpi-cell-red",
        "green":  "kpi-cell-green",
    }
    inner = ""
    for i, c in enumerate(cells):
        cls   = color_map.get(c.get("color", "orange"), "kpi-cell-orange")
        style = 'style="border-top:2px solid var(--accent-blue);"' if i == 0 else ""
        inner += f"""
        <div class="kpi-cell {cls}" {style}>
          <div class="kpi-label">{c['label']}</div>
          <div class="kpi-val">{c['value']}</div>
          <div class="kpi-sub">{c['subtitle']}</div>
        </div>"""
    return f'<div class="kpi-strip">{inner}</div>'


def render(feat, imp, filtered_feat, filtered_imp, shap_df):

    # Inject page-scoped styles
    st.markdown(_HOME_STYLES, unsafe_allow_html=True)
    st.markdown('<div class="cw">', unsafe_allow_html=True)

    # ── SECTION 1 — HERO ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-wrap" style="position:relative;overflow:hidden;">
      <div class="hero-mesh">
        <div class="mesh-orb mesh-orb-1"></div>
        <div class="mesh-orb mesh-orb-2"></div>
        <div class="mesh-orb mesh-orb-3"></div>
      </div>
      <div class="hero-content">
        <h1 class="hero-h1" style="
font-family:'Caldris',sans-serif !important;
font-size:72px;
font-weight:400;
letter-spacing:-0.04em;
line-height:1.05;
">
          When Amazon Shows the<br>
          <span class="acc-amber">Wrong Product</span> to the
          <span class="acc-blue">Wrong Buyer</span>
        </h1>
        <p class="hero-sub">
          Every Amazon listing emits hidden intent signals — discount depth, review velocity,
          trust score, listing richness. This platform decodes those signals into
          <strong>4 buyer archetypes</strong> using an XGBoost ensemble trained on
          <strong>69 engineered features</strong>. The result: SHAP-diagnosed placement
          mismatches turned into precise seller actions that unlock
          <strong>₹9.63 Cr in untapped monthly revenue</strong>.
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 2 — Animated KPI Strip ───────────────────────────────────────
    st.markdown(_animated_kpi_strip([
        {"label": "Products Analysed",   "value": "1,463",    "subtitle": "full catalogue",            "color": "orange"},
        {"label": "Placement Accuracy",  "value": "58.3%",    "subtitle": "correct segment alignment", "color": "blue"},
        {"label": "Macro F1 Score",      "value": "0.9948",   "subtitle": "XGBoost ensemble",          "color": "green"},
        {"label": "Misplaced Products",  "value": "611",      "subtitle": "across all segments",       "color": "red"},
        {"label": "Revenue at Risk",     "value": "₹4.97 Cr", "subtitle": "monthly mismatch leakage",  "color": "purple"},
    ]), unsafe_allow_html=True)

    # ── SECTION 3 — Leakage Alert Banner ─────────────────────────────────────
    st.markdown("""
    <div class="leakage-banner">
      <div class="lb-left">
        <div class="lb-eyebrow">⚡ REVENUE INTELLIGENCE ALERT</div>
        <div class="lb-amount">₹49,663,914</div>
        <div class="lb-desc">monthly mismatch leakage identified across 611 products</div>
      </div>
      <div class="lb-right">
        <div class="lb-stat">Home &amp; Kitchen: <strong>70.8% mismatch rate</strong></div>
        <div class="lb-stat">SOCIAL_PROOF segment: <strong>50% misplaced</strong></div>
        <div class="lb-stat">611 products need <strong>immediate re-alignment</strong></div>
        <div class="lb-stat">Top leakage product: Redmi 9 Activ — <strong>₹1.63 Cr/mo</strong></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 4 — Problem / Solution ───────────────────────────────────────
    st.markdown("""
    <div class="ps-grid">
      <div class="ps-card ps-prob">
        <div class="ps-eyebrow">⚠ The Problem</div>
        <div class="ps-title">Amazon's placement engine treats all buyers the same</div>
        <div class="ps-body">
          A deal-seeking buyer and a quality-first buyer see identical search results.
          The deal-seeker ignores the premium-positioned product; the quality buyer is repelled
          by the heavily discounted one. Both lose — the seller sacrifices margin
          to buyers who don't value the discount, while quality-driven buyers
          <strong>abandon the session entirely</strong>.
        </div>
      </div>
      <div class="ps-card ps-soln">
        <div class="ps-eyebrow">✦ The Solution</div>
        <div class="ps-title">Intent classifier turning product signals into buyer archetypes</div>
        <div class="ps-body">
          69 engineered features → XGBoost + LightGBM ensemble → 4 buyer archetypes →
          SHAP attribution → ranked seller action plan.
          <strong>Macro-F1 = 0.9948</strong> on 5-class imbalanced data with
          SMOTE resampling and <strong>Optuna 50-trial HPO</strong>.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 5 — Segment preview cards ────────────────────────────────────
    counts = feat["segment"].value_counts()

    cards_html = '<div class="seg-preview-grid">'
    for seg in ["DEAL_SEEKER", "QUALITY_FIRST", "SOCIAL_PROOF", "NICHE_EXPLORER"]:
        color        = SEG_COLORS[seg]
        icon         = SEG_ICONS[seg]
        signal, desc = _SEG_SIGNALS[seg]
        cnt          = counts.get(seg, 0)
        pct          = cnt / len(feat) * 100
        r, g, b      = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        cards_html += f"""
        <div class="seg-preview-card"
             style="border-color:rgba({r},{g},{b},0.2);
                    border-top:3px solid rgba({r},{g},{b},0.65);">
          <div class="sp-icon">{icon}</div>
          <div class="sp-name" style="color:{color};">{seg.replace("_"," ")}</div>
          <div class="sp-driver">{signal}</div>
          <div class="sp-desc">{desc}</div>
          <div class="sp-count" style="color:{color};">{cnt:,} products &nbsp;·&nbsp; {pct:.1f}%</div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── SECTION 6 — Donut + Insight cards ────────────────────────────────────
    col_d, col_i = st.columns([1, 1])

    with col_d:
        st.markdown(sec_div("Segment Distribution — Full Catalogue"), unsafe_allow_html=True)
        st.plotly_chart(segment_donut(feat), use_container_width=True)

    with col_i:
        st.markdown(sec_div("Key Analytical Insights"), unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-card" style="border-left:3px solid #EF4444;">
          <div class="insight-card-title" style="color:#FCA5A5;">
            ⚠ Counter-intuitive SHAP Finding — The Discount Paradox
          </div>
          <div class="insight-card-body">
            <strong>savings_ratio &gt; 0.35 carries NEGATIVE SHAP weight</strong>
            on QUALITY_FIRST classification. Sellers offering heavy discounts to attract
            premium buyers are actively signalling low quality — repelling the segment
            that delivers <strong style="color:#60A5FA;">1.4× more revenue per product</strong>.
            This is the project's single most actionable finding.
          </div>
        </div>
        <div class="insight-card" style="border-left:3px solid #10B981;">
          <div class="insight-card-title" style="color:#6EE7B7;">
            ✦ 99.48% Macro F1 — Near-Perfect Classification
          </div>
          <div class="insight-card-body">
            5-class imbalanced problem (730 DEAL_SEEKER vs 8 NICHE_EXPLORER).
            <strong>SMOTE k=5</strong> resampling balanced training data.
            <strong>Optuna 50-trial HPO</strong> converged F1 from 0.82 → 0.9948.
            Zero major cross-segment errors on held-out test set.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── SECTION 7 — Platform navigation tiles ────────────────────────────────
    st.markdown(sec_div("Platform Navigation"), unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:14px;color:var(--text-muted);margin:-8px 0 20px;line-height:1.6;">
      Six interconnected analysis modules — explore in sequence or jump to any section.
    </p>
    """, unsafe_allow_html=True)

    tiles_html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:36px;">'
    for icon, title, num, desc in _WALK_TILES:
        tiles_html += f"""
        <div class="walk-tile">
          <div class="walk-tile-num">PAGE {num}</div>
          <div class="walk-tile-icon">{icon}</div>
          <div class="walk-tile-title">{title}</div>
          <div class="walk-tile-desc">{desc}</div>
          <span class="walk-tile-arrow">→</span>
        </div>"""
    tiles_html += '</div>'
    st.markdown(tiles_html, unsafe_allow_html=True)

    # ── SECTION 8 — Methodology footnote ─────────────────────────────────────
    st.markdown("""
    <div style="border:1px solid rgba(255,255,255,0.06);border-radius:var(--radius-lg);
         padding:20px 28px;background:rgba(255,255,255,0.015);margin-bottom:8px;">
      <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
           letter-spacing:0.1em;text-transform:uppercase;color:var(--text-faint);margin-bottom:12px;">
        Methodology at a Glance
      </div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:20px;">
        <div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:18px;font-weight:700;
               color:var(--text-primary);letter-spacing:-0.03em;">69</div>
          <div style="font-size:11.5px;color:var(--text-faint);margin-top:2px;">Engineered features</div>
        </div>
        <div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:18px;font-weight:700;
               color:var(--text-primary);letter-spacing:-0.03em;">50</div>
          <div style="font-size:11.5px;color:var(--text-faint);margin-top:2px;">Optuna HPO trials</div>
        </div>
        <div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:18px;font-weight:700;
               color:var(--text-primary);letter-spacing:-0.03em;">5-fold</div>
          <div style="font-size:11.5px;color:var(--text-faint);margin-top:2px;">Stratified CV</div>
        </div>
        <div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:18px;font-weight:700;
               color:var(--text-primary);letter-spacing:-0.03em;">SMOTE</div>
          <div style="font-size:11.5px;color:var(--text-faint);margin-top:2px;">k=5 resampling</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)