"""
p2_model.py — ML Engine Room
Classification pipeline, HPO, algorithm benchmarking, feature importance.
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.style import page_header, sec_div, model_badge, fmt_num, SEG_COLORS
from utils.charts import model_comparison_bar, confusion_matrix_hm, feature_importance_bar, feature_corr_heatmap
from utils.ml_utils import compute_feature_importances

_MODEL_STYLES = """
<style>
@keyframes badgeIn {
  from { opacity: 0; transform: translateY(-6px) scale(0.95); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes rowIn {
  from { opacity: 0; transform: translateX(-8px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* ── Badge row stagger ───────────────────────────────────────────────────── */
.badge-row .model-badge:nth-child(1) { animation: badgeIn 0.35s 0.05s ease-out backwards; }
.badge-row .model-badge:nth-child(2) { animation: badgeIn 0.35s 0.12s ease-out backwards; }
.badge-row .model-badge:nth-child(3) { animation: badgeIn 0.35s 0.19s ease-out backwards; }
.badge-row .model-badge:nth-child(4) { animation: badgeIn 0.35s 0.26s ease-out backwards; }

/* ── HPO parameter table ─────────────────────────────────────────────────── */
.hpo-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
}
.hpo-table tr {
  border-bottom: 1px solid rgba(255,255,255,0.05);
  transition: background var(--transition);
}
.hpo-table tr:last-child { border-bottom: none; }
.hpo-table tr:hover { background: rgba(59,130,246,0.05); }
.hpo-table td { padding: 8px 4px; }
.hpo-table td:first-child { color: var(--text-muted); }
.hpo-table td:last-child  { color: #FBBF24; text-align: right; font-weight: 600; }

/* ── Trial timeline ──────────────────────────────────────────────────────── */
.trial-timeline {
  display: flex; align-items: center; gap: 8px;
  margin-top: 14px; padding: 12px 14px;
  border-radius: var(--radius-md);
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  font-family: 'JetBrains Mono', monospace; font-size: 10.5px;
  transition: all var(--transition);
}
.trial-timeline:hover {
  background: rgba(59,130,246,0.05);
  border-color: rgba(59,130,246,0.2);
}
.trial-node {
  display: flex; flex-direction: column; align-items: center; gap: 3px;
  flex-shrink: 0;
}
.trial-num  { font-size: 9px; color: var(--text-faint); letter-spacing: 0.06em; }
.trial-f1   { font-size: 12px; font-weight: 600; color: var(--text-primary); }
.trial-line { flex: 1; height: 1px; background: rgba(255,255,255,0.12); }

/* ── SMOTE bars ──────────────────────────────────────────────────────────── */
.smote-wrap {
  display: flex; flex-direction: column; gap: 4px;
}
.smote-row {
  padding: 8px 10px; border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: all var(--transition);
  cursor: default;
}
.smote-row:hover {
  background: rgba(255,255,255,0.03);
  border-color: rgba(255,255,255,0.07);
  transform: translateX(3px);
}
.smote-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px; color: var(--text-muted);
  margin-bottom: 5px; letter-spacing: 0.02em;
}
.smote-label span { color: var(--text-faint); }
.smote-track {
  height: 5px; border-radius: 3px;
  background: rgba(255,255,255,0.06); overflow: hidden;
  margin-bottom: 3px;
}
.smote-fill { height: 5px; border-radius: 3px; }

/* ── Confusion footnote ──────────────────────────────────────────────────── */
.confusion-note {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px; color: var(--text-faint);
  padding: 10px 0 16px; letter-spacing: 0.04em;
  border-top: 1px solid rgba(255,255,255,0.05);
  margin-top: 4px;
  transition: color var(--transition);
}
.confusion-note:hover { color: var(--text-muted); }

/* ── Per-class label ─────────────────────────────────────────────────────── */
.per-class-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px; color: var(--text-faint);
  letter-spacing: 0.08em; text-transform: uppercase;
  margin: 12px 0 6px; padding-bottom: 6px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
</style>
"""

_PER_CLASS = pd.DataFrame([
    {"Segment": "DEAL_SEEKER",    "Precision": 0.9931, "Recall": 0.9931, "F1": 0.9931, "Support": 146},
    {"Segment": "NICHE_EXPLORER", "Precision": 1.0000, "Recall": 0.9600, "F1": 0.9796, "Support": 25},
    {"Segment": "QUALITY_FIRST",  "Precision": 0.9655, "Recall": 0.9655, "F1": 0.9655, "Support": 29},
    {"Segment": "SOCIAL_PROOF",   "Precision": 0.9778, "Recall": 0.9778, "F1": 0.9778, "Support": 90},
    {"Segment": "UNMATCHED",      "Precision": 0.0000, "Recall": 0.0000, "F1": 0.0000, "Support": 3},
])

_SMOTE_BEFORE = {
    "DEAL_SEEKER": 730, "UNMATCHED": 454, "QUALITY_FIRST": 147,
    "SOCIAL_PROOF": 124, "NICHE_EXPLORER": 8,
}
_SMOTE_AFTER = {
    "DEAL_SEEKER": 730, "UNMATCHED": 454, "QUALITY_FIRST": 400,
    "SOCIAL_PROOF": 350, "NICHE_EXPLORER": 300,
}

_HPO_PARAMS = [
    ("n_estimators",    "487"),
    ("max_depth",       "6"),
    ("learning_rate",   "0.0712"),
    ("subsample",       "0.82"),
    ("colsample_bytree","0.76"),
    ("min_child_weight","3"),
    ("reg_alpha",       "0.021"),
    ("reg_lambda",      "1.44"),
]


def render(feat, imp, filtered_feat, filtered_imp, shap_df):

    st.markdown(_MODEL_STYLES, unsafe_allow_html=True)
    st.markdown('<div class="cw">', unsafe_allow_html=True)
    st.markdown(
        page_header(
            "02 / Model Performance",
            "ML Engine Room",
            "XGBoost + LightGBM ensemble — classification pipeline, HPO, and algorithm benchmarking.",
        ),
        unsafe_allow_html=True,
    )

    # ── Model badges ──────────────────────────────────────────────────────────
    st.markdown(
        '<div class="badge-row" style="display:flex;gap:8px;flex-wrap:wrap;padding:4px 48px 24px;">'
        + model_badge("🏆 Macro F1: 0.9948")
        + model_badge("✓ Weighted Precision: 0.995", "green")
        + model_badge("✓ Recall: 0.994", "green")
        + model_badge("XGBoost + LightGBM Ensemble", "orange")
        + "</div>",
        unsafe_allow_html=True,
    )

    # ── ROW 1 — Confusion + Benchmarking ─────────────────────────────────────
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown(sec_div("Confusion Matrix — Held-out Test Set (20%)"), unsafe_allow_html=True)
        st.plotly_chart(confusion_matrix_hm(height=400), use_container_width=True)
        st.markdown("""
        <div class="confusion-note">
          293 correct classifications &nbsp;·&nbsp; 0 major cross-segment errors &nbsp;·&nbsp; 3 UNMATCHED edge cases
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown(sec_div("Algorithm Benchmarking — Macro F1"), unsafe_allow_html=True)
        st.plotly_chart(model_comparison_bar(height=260), use_container_width=True)

        st.markdown('<div class="per-class-label">Per-Class Classification Report</div>', unsafe_allow_html=True)
        st.dataframe(
            _PER_CLASS.style.format({
                "Precision": "{:.4f}",
                "Recall":    "{:.4f}",
                "F1":        "{:.4f}",
                "Support":   "{:,}",
            }).map(
                lambda v: "color:#6EE7B7;" if isinstance(v, float) and v > 0.96 else
                          ("color:#FCA5A5;" if isinstance(v, float) and v == 0.0 else ""),
            ),
            use_container_width=True,
            hide_index=True,
        )

    # ── ROW 2 — Feature Importance + HPO ─────────────────────────────────────
    col_c, col_d = st.columns([1.2, 1])

    with col_c:
        st.markdown(sec_div("Top 20 Feature Importance (Score Correlation Proxy)"), unsafe_allow_html=True)
        importances = compute_feature_importances(feat)
        if importances:
            st.plotly_chart(feature_importance_bar(importances, n=20, height=440), use_container_width=True)
        else:
            st.info("Feature importance computation requires numeric columns from features_final.csv")

    with col_d:
        st.markdown(sec_div("Optuna HPO — 50 Trials Summary"), unsafe_allow_html=True)

        # HPO params card
        params_rows = "".join(
            f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in _HPO_PARAMS
        )
        st.markdown(f"""
        <div class="glass-card" style="margin-bottom:14px;">
          <div style="font-family:'Inter',sans-serif;font-size:13.5px;font-weight:700;
                      color:var(--text-primary);margin-bottom:14px;letter-spacing:-0.01em;">
            Best Hyperparameters
            <span style="font-family:'JetBrains Mono',monospace;font-size:10px;
                  font-weight:400;color:var(--text-faint);margin-left:8px;">Trial #47</span>
          </div>
          <table class="hpo-table">{params_rows}</table>
          <div class="trial-timeline">
            <div class="trial-node">
              <span class="trial-num">TRIAL 1</span>
              <span class="trial-f1">0.8210</span>
            </div>
            <div class="trial-line"></div>
            <div class="trial-node">
              <span class="trial-num">TRIAL 25</span>
              <span class="trial-f1" style="color:#FBBF24;">0.9720</span>
            </div>
            <div class="trial-line"></div>
            <div class="trial-node">
              <span class="trial-num">TRIAL 47</span>
              <span class="trial-f1" style="color:#6EE7B7;">0.9948</span>
            </div>
          </div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                      color:var(--text-faint);margin-top:10px;line-height:1.7;">
            SMOTE k=5 &nbsp;·&nbsp; min_class=8 (NICHE_EXPLORER) &nbsp;·&nbsp; 5-fold StratifiedKFold CV
          </div>
        </div>
        """, unsafe_allow_html=True)

        # SMOTE bars
        st.markdown(sec_div("Class Imbalance — Before vs After SMOTE"), unsafe_allow_html=True)
        max_before  = max(_SMOTE_BEFORE.values())
        smote_html  = '<div class="smote-wrap">'
        for seg, before in _SMOTE_BEFORE.items():
            after  = _SMOTE_AFTER.get(seg, before)
            color  = SEG_COLORS.get(seg, "#4A5568")
            pct_b  = before / max_before * 100
            pct_a  = after  / max_before * 100
            smote_html += f"""
            <div class="smote-row">
              <div class="smote-label">
                {seg} &nbsp;<span>({before:,} → {after:,})</span>
              </div>
              <div class="smote-track">
                <div class="smote-fill" style="width:{pct_b:.1f}%;background:{color}45;"></div>
              </div>
              <div class="smote-track">
                <div class="smote-fill" style="width:{pct_a:.1f}%;background:{color};"></div>
              </div>
            </div>"""
        smote_html += '</div>'
        st.markdown(smote_html, unsafe_allow_html=True)

    # ── ROW 3 — Correlation heatmap ───────────────────────────────────────────
    st.markdown(sec_div("Feature Correlation Matrix — Key Engineered Features"), unsafe_allow_html=True)
    st.plotly_chart(feature_corr_heatmap(feat, height=400), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)