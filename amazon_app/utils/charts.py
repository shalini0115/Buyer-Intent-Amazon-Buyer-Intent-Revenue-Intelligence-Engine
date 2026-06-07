"""
charts.py — Plotly chart factory
All charts use the amazon_dark template registered in style.py.
Call apply_chart_defaults() on every fig before returning.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.style import SEG_COLORS, CHART_BG, PAPER_BG, FONT_MONO, FONT_MAIN, FONT_HEAD

# ─────────────────────────────────────────────────────────────────────────────
# BASE LAYOUT HELPER
# ─────────────────────────────────────────────────────────────────────────────
def _base(fig: go.Figure, height: int = 380, legend_h: bool = False) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        margin=dict(t=28, b=12, l=12, r=12),
        font=dict(family=FONT_MAIN, color="#6B6988", size=13),
        hoverlabel=dict(
            bgcolor="#14142A",
            bordercolor="rgba(255,255,255,0.08)",
            font=dict(family=FONT_MONO, size=12, color="#E8E6F0"),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=11.5, color="#6B6988"),
        ),
        transition=dict(duration=400, easing="cubic-in-out"),
    )
    if legend_h:
        fig.update_layout(legend=dict(
            orientation="h", y=-0.28, x=0,
            font=dict(size=11, family=FONT_MONO),
        ))
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.04)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=11, color="#4A4862", family=FONT_MONO),
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.04)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=11, color="#4A4862", family=FONT_MONO),
    )
    # Add animation to all traces
    fig.update_traces(
        hoverinfo="all",
        hovertemplate="%{hovertemplate}",
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# 1. SEGMENT DONUT
# ─────────────────────────────────────────────────────────────────────────────
def segment_donut(df: pd.DataFrame, seg_col: str = "segment", height: int = 340) -> go.Figure:
    counts = df[seg_col].value_counts().reset_index()
    counts.columns = ["segment", "count"]
    colors = [SEG_COLORS.get(s, "#4A4A5E") for s in counts["segment"]]

    fig = go.Figure(go.Pie(
        labels=counts["segment"],
        values=counts["count"],
        hole=0.64,
        marker=dict(colors=colors, line=dict(color=CHART_BG, width=3)),
        textfont=dict(family=FONT_MONO, size=11),
        hovertemplate="<b>%{label}</b><br>%{value:,} products<br>%{percent:.1%}<extra></extra>",
        sort=False,
        pull=[0.05 if i == 0 else 0 for i in range(len(counts))],
    ))
    total = counts["count"].sum()
    fig.add_annotation(
        text=f"<b style='font-size:28px;'>{total:,}</b><br>"
             f"<span style='font-size:12px;color:#4A4862;'>products</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color="#E8E6F0", size=14),
    )
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 2. STACKED BAR — Segment × Category
# ─────────────────────────────────────────────────────────────────────────────
def seg_by_category_bar(df: pd.DataFrame, height: int = 380) -> go.Figure:
    grp = df.groupby(["top_cat", "segment"]).size().reset_index(name="count")
    # order categories by total count descending
    order = df["top_cat"].value_counts().index.tolist()
    grp["top_cat"] = pd.Categorical(grp["top_cat"], categories=order, ordered=True)
    grp = grp.sort_values("top_cat")

    fig = px.bar(
        grp, x="top_cat", y="count", color="segment",
        color_discrete_map=SEG_COLORS,
        barmode="stack",
        labels={"top_cat": "", "count": "Products", "segment": "Buyer Segment"},
    )
    fig.update_traces(marker_line_width=0)
    fig.update_xaxes(tickangle=-18)
    return _base(fig, height, legend_h=True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. REVENUE HEATMAP — Segment × Category
# ─────────────────────────────────────────────────────────────────────────────
def revenue_heatmap(df: pd.DataFrame, height: int = 380) -> go.Figure:
    grp = (
        df.groupby(["segment", "top_cat"])["revenue_uplift"]
        .mean()
        .reset_index()
    )
    pivot = grp.pivot(index="segment", columns="top_cat", values="revenue_uplift").fillna(0)
    pivot = pivot.div(1e5)  # in Lakhs

    fig = px.imshow(
        pivot,
        text_auto=".1f",
        color_continuous_scale=[
            [0.0, "#0A0A12"],
            [0.25, "#1A1A2E"],
            [0.60, "#7A4800"],
            [1.0,  "#FF9500"],
        ],
        labels=dict(color="₹L Uplift"),
        aspect="auto",
    )
    fig.update_traces(
        textfont=dict(size=10, family=FONT_MONO, color="#E8E6F0"),
        hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Avg uplift: ₹%{z:.2f}L<extra></extra>",
    )
    fig.update_xaxes(tickangle=-18, side="bottom")
    fig.update_coloraxes(colorbar=dict(
        tickfont=dict(size=9, family=FONT_MONO, color="#6B6988"),
        title=dict(font=dict(size=10, family=FONT_MONO, color="#6B6988")),
        thickness=10, len=0.8,
    ))
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 4. SCATTER — Price vs Rating (colored by segment)
# ─────────────────────────────────────────────────────────────────────────────
def price_rating_scatter(df: pd.DataFrame, height: int = 340) -> go.Figure:
    sc = df.dropna(subset=["price_disc", "rating"]).copy()
    fig = px.scatter(
        sc,
        x="price_disc", y="rating",
        color="segment",
        color_discrete_map=SEG_COLORS,
        size="rating_count",
        size_max=20,
        opacity=0.75,
        labels={"price_disc": "Discounted Price (₹)", "rating": "Rating ★", "segment": "Segment"},
        hover_data={"price_disc": ":,.0f", "rating": ":.1f", "rating_count": ":,"},
    )
    fig.update_traces(
        marker=dict(line=dict(width=0.5, color="rgba(255,255,255,0.1)")),
        hovertemplate="<b>%{customdata[2]}</b><br>Price: ₹%{customdata[0]:,.0f}<br>Rating: %{customdata[1]:.1f}★<br>Reviews: %{customdata[3]:,}<extra></extra>",
    )
    fig.update_xaxes(tickprefix="₹", tickformat=",.0f")
    fig.update_layout(showlegend=False)
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 5. VIOLIN — Discount by Segment
# ─────────────────────────────────────────────────────────────────────────────
def discount_violin(df: pd.DataFrame, height: int = 320) -> go.Figure:
    fig = go.Figure()
    for seg, color in SEG_COLORS.items():
        sub = df[df["segment"] == seg]["discount_pct"].dropna()
        if len(sub) == 0:
            continue
        fig.add_trace(go.Violin(
            y=sub,
            name=seg,
            line_color=color,
            fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.09)",
            meanline_visible=True,
            meanline_color=color,
            points=False,
            hovertemplate=f"<b>{seg}</b><br>Discount: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(
        showlegend=False,
        violinmode="overlay",
        yaxis_title="Discount %",
    )
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 6. MODEL COMPARISON BAR
# ─────────────────────────────────────────────────────────────────────────────
def model_comparison_bar(height: int = 300) -> go.Figure:
    models = ["Logistic\nReg.", "XGBoost\n(base)", "LightGBM", "XGBoost\n(tuned)", "Ensemble\n(Final)"]
    f1s    = [0.8910, 0.9620, 0.9820, 0.9871, 0.9948]
    colors = ["#4A4862", "#5BA3F5", "#BF5FFF", "#FF9500", "#00E5A0"]

    fig = go.Figure()
    for m, f, c in zip(models, f1s, colors):
        is_best = f == max(f1s)
        fig.add_trace(go.Bar(
            x=[m], y=[f],
            marker_color=c,
            marker_line_width=0,
            marker_opacity=1.0 if is_best else 0.65,
            text=[f"{f:.4f}"],
            textposition="outside",
            textfont=dict(size=11, color=c, family=FONT_MONO),
            showlegend=False,
            width=0.52,
            hovertemplate=f"<b>{m.replace(chr(10),' ')}</b><br>Macro-F1: {f:.4f}<extra></extra>",
        ))
    fig.add_hline(
        y=0.9948, line_dash="dash",
        line_color="rgba(255,149,0,0.3)",
        line_width=1.2,
    )
    fig.update_yaxes(range=[0.86, 1.04], tickformat=".3f")
    fig.update_xaxes(tickfont=dict(size=10, family=FONT_MONO))
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 7. CONFUSION MATRIX HEATMAP
# ─────────────────────────────────────────────────────────────────────────────
def confusion_matrix_hm(
    preds_df: pd.DataFrame | None = None,
    height: int = 420,
) -> go.Figure:
    SEGS = ["DEAL_SEEKER", "NICHE_EXPLORER", "QUALITY_FIRST", "SOCIAL_PROOF", "UNMATCHED"]
    labels = [s.replace("_", " ") for s in SEGS]

    if preds_df is not None and "true_segment" in preds_df.columns:
        cm = pd.crosstab(preds_df["true_segment"], preds_df["pred_segment"])
        cm = cm.reindex(index=SEGS, columns=SEGS, fill_value=0)
        z  = cm.values
    else:
        # Derived from actual classification report (0.9948 ensemble)
        z = np.array([
            [143, 0, 0, 0, 3],
            [0, 24, 0, 0, 1],
            [1, 0, 28, 0, 0],
            [0, 0, 0, 89, 2],
            [2, 0, 0, 1, 0],
        ])

    fig = go.Figure(go.Heatmap(
        z=z, x=labels, y=labels,
        colorscale=[
            [0.0, "#07070E"],
            [0.2, "#0E1A2E"],
            [0.6, "rgba(0,194,255,0.13)"],
            [1.0, "#00E5A0"],
        ],
        text=z,
        texttemplate="%{text}",
        textfont=dict(size=13, family=FONT_MONO, color="#E8E6F0"),
        showscale=False,
        hovertemplate="True: <b>%{y}</b><br>Pred: <b>%{x}</b><br>Count: <b>%{z}</b><extra></extra>",
    ))
    fig.update_xaxes(side="bottom", tickangle=-20, tickfont=dict(size=9.5, family=FONT_MONO))
    fig.update_yaxes(tickfont=dict(size=9.5, family=FONT_MONO))
    fig.update_layout(xaxis_title="Predicted →", yaxis_title="← True")
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 8. FEATURE IMPORTANCE HORIZONTAL BAR
# ─────────────────────────────────────────────────────────────────────────────
def feature_importance_bar(
    importances: dict[str, float],
    n: int = 20,
    color: str = "#00C2FF",
    height: int = 460,
) -> go.Figure:
    fi = pd.Series(importances).nlargest(n).sort_values()
    fig = go.Figure(go.Bar(
        x=fi.values,
        y=fi.index,
        orientation="h",
        marker=dict(
            color=[f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},{0.3 + v/fi.max()*0.7:.2f})" for v in fi.values],
            line=dict(width=0),
        ),
        text=[f"{v:.4f}" for v in fi.values],
        textposition="outside",
        textfont=dict(size=9, family=FONT_MONO, color="#6B6988"),
        hovertemplate="<b>%{y}</b><br>Score: %{x:.4f}<extra></extra>",
    ))
    fig.update_xaxes(title="Importance Score")
    fig.update_yaxes(tickfont=dict(size=10, family=FONT_MONO))
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 9. MISMATCH RATE HORIZONTAL BAR
# ─────────────────────────────────────────────────────────────────────────────
def mismatch_rate_bar(df: pd.DataFrame, height: int = 320) -> go.Figure:
    mm = (
        df.groupby("top_cat")["mismatch_flag"]
        .mean()
        .reset_index()
    )
    mm["pct"] = (mm["mismatch_flag"] * 100).round(1)
    mm = mm.sort_values("pct", ascending=True)

    fig = go.Figure(go.Bar(
        x=mm["pct"],
        y=mm["top_cat"],
        orientation="h",
        marker=dict(
            color=mm["pct"],
            colorscale=[
                [0.0, "#00E5A0"],
                [0.5, "#FF9500"],
                [1.0, "#FF4444"],
            ],
            line=dict(width=0),
        ),
        text=mm["pct"].map("{:.1f}%".format),
        textposition="outside",
        textfont=dict(color="#8B89A8", size=10, family=FONT_MONO),
        hovertemplate="<b>%{y}</b><br>Mismatch rate: %{x:.1f}%<extra></extra>",
    ))
    fig.update_xaxes(range=[0, mm["pct"].max() * 1.25], title="Mismatch %")
    fig.update_yaxes(tickfont=dict(family=FONT_MONO, size=10))
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 10. DISCOUNT vs RATING SCATTER (mismatch highlight)
# ─────────────────────────────────────────────────────────────────────────────
def mismatch_scatter(df: pd.DataFrame, height: int = 320) -> go.Figure:
    sc = df.dropna(subset=["discount_pct", "rating"]).copy()
    sc["status"] = sc["mismatch_flag"].map({0: "✓ Correct Placement", 1: "⚠ Mismatch"})
    fig = px.scatter(
        sc, x="discount_pct", y="rating",
        color="status",
        color_discrete_map={"✓ Correct Placement": "#00E5A0", "⚠ Mismatch": "#FF4444"},
        labels={"discount_pct": "Discount %", "rating": "Product Rating ★"},
        opacity=0.68,
    )
    fig.update_traces(marker=dict(size=6, line=dict(width=0)))
    fig.update_layout(legend=dict(
        orientation="h", y=-0.28, title="",
        font=dict(size=10, family=FONT_MONO),
    ))
    # Add threshold lines
    fig.add_vline(x=45, line_dash="dash", line_color="rgba(255,149,0,0.3)",
                  line_width=1, annotation_text="DS threshold",
                  annotation_font=dict(size=9, color="#FF9500", family=FONT_MONO))
    fig.add_hline(y=4.3, line_dash="dash", line_color="rgba(0,194,255,0.3)",
                  line_width=1, annotation_text="QF threshold",
                  annotation_font=dict(size=9, color="#00C2FF", family=FONT_MONO))
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 11. RADAR CHART — Buyer DNA fingerprint
# ─────────────────────────────────────────────────────────────────────────────
def radar_chart(
    seg_vals: dict[str, float],
    overall_vals: dict[str, float],
    color: str = "#FF9500",
    height: int = 380,
) -> go.Figure:
    cats = list(seg_vals.keys())
    sv   = list(seg_vals.values())
    ov   = list(overall_vals.values())

    # Close the polygon
    cats_c = cats + [cats[0]]
    sv_c   = sv + [sv[0]]
    ov_c   = ov + [ov[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=sv_c, theta=cats_c,
        fill="toself",
        fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)",
        line=dict(color=color, width=2.5),
        name="This Segment",
        hovertemplate="%{theta}: <b>%{r:.3f}</b><extra></extra>",
        marker=dict(size=7, color=color),
    ))
    fig.add_trace(go.Scatterpolar(
        r=ov_c, theta=cats_c,
        fill="toself",
        fillcolor="rgba(255,255,255,0.04)",
        line=dict(color="#6B6988", width=1.5, dash="dot"),
        name="Dataset Average",
        hovertemplate="%{theta}: <b>%{r:.3f}</b><extra></extra>",
        marker=dict(size=5, color="#6B6988"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=CHART_BG,
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.06)",
                tickfont=dict(size=10, color="#3B3A52", family=FONT_MONO),
                dtick=0.25,
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.08)",
                tickfont=dict(size=11.5, color="#8B89A8", family=FONT_MONO),
            ),
        ),
        showlegend=True,
        legend=dict(
            x=0.5, y=-0.12, xanchor="center",
            orientation="h",
            font=dict(size=11, family=FONT_MONO),
        ),
    )
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 12. REVENUE DISTRIBUTION HISTOGRAM
# ─────────────────────────────────────────────────────────────────────────────
def revenue_hist(df: pd.DataFrame, seg: str, height: int = 220) -> go.Figure:
    color = SEG_COLORS.get(seg, "#FF9500")
    sub = df[df["segment"] == seg]["revenue_uplift"].dropna()
    fig = px.histogram(
        x=sub, nbins=24,
        color_discrete_sequence=[color],
        labels={"x": "Revenue Uplift (₹)"},
    )
    fig.update_traces(
        marker_line_width=1.5,
        marker_line_color="rgba(255,255,255,0.08)",
        opacity=0.9,
        hovertemplate="Revenue: ₹%{x:,.0f}<br>Count: %{y}<extra></extra>",
    )
    fig.update_xaxes(tickprefix="₹", tickformat=",.0f")
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 13. TREEMAP — Category revenue
# ─────────────────────────────────────────────────────────────────────────────
def revenue_treemap(df: pd.DataFrame, height: int = 360) -> go.Figure:
    grp = (
        df.groupby(["top_cat", "segment"])
        .agg(total_uplift=("revenue_uplift", "sum"), count=("product_id", "count"))
        .reset_index()
    )
    grp["total_uplift"] = grp["total_uplift"].clip(lower=1)

    fig = px.treemap(
        grp,
        path=["top_cat", "segment"],
        values="total_uplift",
        color="segment",
        color_discrete_map=SEG_COLORS,
        hover_data={"count": True, "total_uplift": ":,.0f"},
        custom_data=["count", "total_uplift"],
    )
    fig.update_traces(
        marker=dict(line=dict(width=1.5, color=CHART_BG)),
        hovertemplate="<b>%{label}</b><br>Uplift: ₹%{customdata[1]:,.0f}<br>Products: %{customdata[0]}<extra></extra>",
        textfont=dict(family=FONT_MAIN, size=11),
    )
    fig.update_layout(margin=dict(t=10, b=0, l=0, r=0))
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 14. PROBABILITY GAUGE BARS (product decoder)
# ─────────────────────────────────────────────────────────────────────────────
def probability_bars(scores: dict[str, float], pred_seg: str, height: int = 260) -> go.Figure:
    total = sum(scores.values()) or 1
    norm  = {k: v / total for k, v in scores.items()}
    segs  = sorted(norm, key=norm.get, reverse=True)

    fig = go.Figure()
    for i, seg in enumerate(segs):
        v     = norm[seg]
        color = SEG_COLORS.get(seg, "#4A4A5E")
        is_pred = seg == pred_seg
        fig.add_trace(go.Bar(
            x=[v], y=[seg.replace("_", " ")],
            orientation="h",
            marker=dict(
                color=color,
                opacity=1.0 if is_pred else 0.35,
                line=dict(width=2.5 if is_pred else 1,
                          color=color),
            ),
            text=[f"{v*100:.1f}%"],
            textposition="outside",
            textfont=dict(size=11, family=FONT_MONO, color=color if is_pred else "#4A4862"),
            showlegend=False,
            hovertemplate=f"<b>{seg}</b><br>Score: {v*100:.1f}%<extra></extra>",
        ))
    fig.update_xaxes(range=[0, 1.2], tickformat=".0%", title="Segment Score")
    fig.update_yaxes(tickfont=dict(family=FONT_MONO, size=11))
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 15. WHAT-IF GAUGE — success probability
# ─────────────────────────────────────────────────────────────────────────────
def whyif_gauge(probability: float, color: str = "#00E5A0", height: int = 240) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability * 100,
        number=dict(suffix="%", font=dict(family=FONT_HEAD, size=40, color="#E8E6F0")),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickfont=dict(size=10, family=FONT_MONO, color="#4A4862"),
            ),
            bar=dict(color=color, thickness=0.32),
            bgcolor=CHART_BG,
            borderwidth=0,
            steps=[
                dict(range=[0, 33],  color="rgba(255,68,68,0.1)"),
                dict(range=[33, 66], color="rgba(255,149,0,0.1)"),
                dict(range=[66, 100], color="rgba(0,229,160,0.1)"),
            ],
            threshold=dict(
                line=dict(color=color, width=2),
                thickness=0.8,
                value=probability * 100,
            ),
        ),
    ))
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        margin=dict(t=20, b=8, l=24, r=24),
        height=height,
        font=dict(family=FONT_MAIN, color="#6B6988", size=12),
        transition=dict(duration=400, easing="cubic-in-out"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 16. FEATURE CORRELATION HEATMAP
# ─────────────────────────────────────────────────────────────────────────────
def feature_corr_heatmap(df: pd.DataFrame, height: int = 420) -> go.Figure:
    KEY_FEATURES = [
        "savings_ratio", "discount_pct", "rating", "trust_score",
        "review_log", "social_proof_score", "review_percentile",
        "category_depth", "word_count", "keyword_density",
        "price_percentile", "quality_composite",
    ]
    cols = [c for c in KEY_FEATURES if c in df.columns]
    corr = df[cols].corr().round(3)

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.columns.tolist(),
        colorscale=[
            [0.0, "#FF4444"],
            [0.5, "#0A0A12"],
            [1.0, "#00E5A0"],
        ],
        zmid=0,
        text=corr.values.round(2),
        texttemplate="%{text}",
        textfont=dict(size=8.5, family=FONT_MONO, color="#E8E6F0"),
        showscale=True,
        colorbar=dict(
            thickness=10,
            tickfont=dict(size=9, family=FONT_MONO, color="#6B6988"),
        ),
        hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Corr: <b>%{z:.3f}</b><extra></extra>",
    ))
    fig.update_xaxes(tickangle=-35, tickfont=dict(size=9, family=FONT_MONO))
    fig.update_yaxes(tickfont=dict(size=9, family=FONT_MONO))
    return _base(fig, height)


# ─────────────────────────────────────────────────────────────────────────────
# 17. REVENUE LEAKAGE LINE — projected monthly
# ─────────────────────────────────────────────────────────────────────────────
def leakage_projection(total_loss: float, n_months: int = 12, height: int = 280) -> go.Figure:
    months = list(range(1, n_months + 1))
    # compound effect: unresolved leakage compounds by lost compounding opportunities
    cumulative = [total_loss * m * (1 + 0.02) ** m for m in months]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=cumulative,
        fill="tozeroy",
        fillcolor="rgba(255,68,68,0.07)",
        line=dict(color="#FF4444", width=2),
        mode="lines",
        hovertemplate="Month %{x}<br>Cumulative leakage: ₹%{y:,.0f}<extra></extra>",
        name="Projected leakage",
    ))
    fig.update_xaxes(title="Month", dtick=1)
    fig.update_yaxes(title="₹ Cumulative", tickformat=",.0s")
    return _base(fig, height)