"""
style.py — Design system: colors, fonts, CSS, HTML component builders
Amazon Buyer Intent Intelligence Platform
v2 — Premium SaaS redesign (Linear / Stripe / Vercel aesthetic)
     Animated KPIs · Strong hovers · Better typography · Richer depth
"""

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────────

SEG_COLORS = {
    "DEAL_SEEKER":    "#F59E0B",
    "QUALITY_FIRST":  "#3B82F6",
    "SOCIAL_PROOF":   "#8B5CF6",
    "NICHE_EXPLORER": "#10B981",
    "UNMATCHED":      "#475569",
}

SEG_ICONS = {
    "DEAL_SEEKER":    "🏷️",
    "QUALITY_FIRST":  "⭐",
    "SOCIAL_PROOF":   "💬",
    "NICHE_EXPLORER": "🔭",
    "UNMATCHED":      "◌",
}

SEG_TAGLINES = {
    "DEAL_SEEKER":    "Discount-Driven Hunters",
    "QUALITY_FIRST":  "Premium Selective Buyers",
    "SOCIAL_PROOF":   "Trust-by-Reviews Shoppers",
    "NICHE_EXPLORER": "Deep-Category Specialists",
    "UNMATCHED":      "Unclassified Behaviour",
}

SEG_DNA = {
    "DEAL_SEEKER": (
        "savings_ratio is the dominant classification signal — above 0.45 is near-certain DEAL_SEEKER "
        "territory. These buyers activate on loss-aversion psychology: the fear of paying full price "
        "outweighs product quality signals. Discount above 45% with rating ≥ 3.8 fires this segment. "
        "High volume, low LTV — loyal to price not brand."
    ),
    "QUALITY_FIRST": (
        "Counter-intuitive SHAP finding: savings_ratio above 0.35 has NEGATIVE SHAP impact here. "
        "Trust_score and rating ≥ 4.3 are the dominant positive drivers. With ≥ 500 reviews and "
        "discount < 35%, these buyers interpret heavy discounting as a quality signal of concern. "
        "Highest weight (1.4) — most commercially valuable segment: high margin, low return rate."
    ),
    "SOCIAL_PROOF": (
        "review_log and social_proof_score dominate. Category-relative top-quartile review count "
        "with rating ≥ 4.0 triggers this segment. 10,000 reviews + 4.0★ beats 50 reviews + 4.8★ "
        "every time. Crowd validation reduces perceived purchase risk — Cialdini's social proof "
        "principle operationalised. Highest revenue uplift segment: ₹48.3M of total ₹96.3M."
    ),
    "NICHE_EXPLORER": (
        "category_depth ≥ 2 and review_count < 200 with rating ≥ 4.2 define the hidden-gem buyer. "
        "Listing richness (word_count, about_length, keyword_density) matters more than price. "
        "Expert buyers self-select via specificity — broad listings are invisible to this archetype. "
        "Rare (n=8, 0.5%) but high-potential: early-adopter seeding unlocks viral review loops."
    ),
}

# Chart palette
CHART_BG  = "#0F172A"
PAPER_BG  = "#0F172A"
GRID_CLR  = "rgba(255,255,255,0.04)"
AXIS_CLR  = "rgba(255,255,255,0.07)"
FONT_MAIN = "Inter"
FONT_MONO = "JetBrains Mono"
FONT_HEAD = "Inter"

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY DARK TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────
import plotly.graph_objects as go
import plotly.io as pio

DARK_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family=FONT_MAIN, color="#94A3B8", size=11),
        title=dict(font=dict(family=FONT_HEAD, color="#F1F5F9", size=14, weight=600)),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=11, color="#94A3B8"),
        ),
        xaxis=dict(
            gridcolor=GRID_CLR,
            linecolor=AXIS_CLR,
            zerolinecolor=AXIS_CLR,
            tickfont=dict(size=11, color="#64748B"),
        ),
        yaxis=dict(
            gridcolor=GRID_CLR,
            linecolor=AXIS_CLR,
            zerolinecolor=AXIS_CLR,
            tickfont=dict(size=11, color="#64748B"),
        ),
        margin=dict(t=32, b=16, l=16, r=16),
        hoverlabel=dict(
            bgcolor="#1E2D45",
            bordercolor="rgba(59,130,246,0.3)",
            font=dict(family=FONT_MONO, size=12, color="#F1F5F9"),
        ),
        colorway=[
            SEG_COLORS["DEAL_SEEKER"],
            SEG_COLORS["QUALITY_FIRST"],
            SEG_COLORS["SOCIAL_PROOF"],
            SEG_COLORS["NICHE_EXPLORER"],
            SEG_COLORS["UNMATCHED"],
        ],
    )
)

pio.templates["amazon_dark"] = DARK_TEMPLATE
pio.templates.default = "amazon_dark"


# ─────────────────────────────────────────────────────────────────────────────
# FULL CSS — injected once in app.py via st.markdown
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500;600&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Outlined');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Round');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Sharp');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Two+Tone');

/* ── CSS Variables ───────────────────────────────────────────────────────── */
:root {
  --bg-base:      #090E1A;
  --bg-surface:   #0D1526;
  --bg-card:      #111D30;
  --bg-card-alt:  #152036;
  --bg-hover:     #1A2840;
  --bg-input:     #111D30;
  --border:       rgba(255,255,255,0.08);
  --border-soft:  rgba(255,255,255,0.05);
  --border-hover: rgba(59,130,246,0.35);
  --text-primary: #F0F4FF;
  --text-secondary:#CBD5E1;
  --text-muted:   #8B9CC0;
  --text-faint:   #4E617A;
  --accent-blue:  #3B82F6;
  --accent-teal:  #14B8A6;
  --accent-amber: #F59E0B;
  --accent-red:   #EF4444;
  --accent-emerald:#10B981;
  --accent-violet:#8B5CF6;
  --radius-sm:    6px;
  --radius-md:    10px;
  --radius-lg:    14px;
  --radius-xl:    20px;
  --shadow-sm:    0 1px 4px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3);
  --shadow-md:    0 4px 20px rgba(0,0,0,0.55), 0 2px 6px rgba(0,0,0,0.35);
  --shadow-lg:    0 10px 40px rgba(0,0,0,0.65), 0 4px 10px rgba(0,0,0,0.4);
  --shadow-xl:    0 20px 60px rgba(0,0,0,0.75), 0 8px 20px rgba(0,0,0,0.5);
  --glow-blue:    0 0 20px rgba(59,130,246,0.18), 0 0 40px rgba(59,130,246,0.08);
  --glow-amber:   0 0 20px rgba(245,158,11,0.18), 0 0 40px rgba(245,158,11,0.08);
  --glow-green:   0 0 20px rgba(16,185,129,0.18), 0 0 40px rgba(16,185,129,0.08);
  --glow-red:     0 0 20px rgba(239,68,68,0.18),  0 0 40px rgba(239,68,68,0.08);
  --glow-violet:  0 0 20px rgba(139,92,246,0.18), 0 0 40px rgba(139,92,246,0.08);
  --transition:   0.2s cubic-bezier(0.4,0,0.2,1);
  --transition-slow: 0.35s cubic-bezier(0.4,0,0.2,1);
}

/* ── Material Icons ──────────────────────────────────────────────────────── */
.material-icons {
  font-family: 'Material Icons' !important;
  font-weight: normal !important;
  font-style: normal !important;
  font-size: 24px !important;
  display: inline-flex !important;
  line-height: 1 !important;
  text-transform: none !important;
  letter-spacing: normal !important;
  word-wrap: normal !important;
  white-space: nowrap !important;
  direction: ltr !important;
  -webkit-font-smoothing: antialiased !important;
  text-rendering: optimizeLegibility !important;
  -moz-osx-font-smoothing: grayscale !important;
}

.material-icons-outlined {
  font-family: 'Material Icons Outlined' !important;
  font-weight: normal !important;
  font-style: normal !important;
  font-size: 24px !important;
  display: inline-flex !important;
  line-height: 1 !important;
  text-transform: none !important;
  letter-spacing: normal !important;
  word-wrap: normal !important;
  white-space: nowrap !important;
  direction: ltr !important;
  -webkit-font-smoothing: antialiased !important;
  text-rendering: optimizeLegibility !important;
  -moz-osx-font-smoothing: grayscale !important;
}

/* ── Reset & Base ────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-base) !important;
    color: var(--text-secondary) !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
}
.main { background: var(--bg-base) !important; }
[data-testid="stMainBlockContainer"] {
    background: var(--bg-base) !important;
    padding-top: 0 !important;
    max-width: 100% !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}
[data-testid="stAppViewBlockContainer"] { max-width: 100% !important; }
header[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stDecoration"]    { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Page entrance animation ─────────────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0);    }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes countUp {
    from { opacity: 0; transform: translateY(6px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-16px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(59,130,246,0); }
    50%       { box-shadow: 0 0 0 4px rgba(59,130,246,0.1); }
}

.main .block-container > div {
    animation: fadeInUp 0.28s ease-out;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #060C18 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-muted) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Sidebar collapse button — more visible */
[data-testid="collapsedControl"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-muted) !important;
    transition: all var(--transition) !important;
}
[data-testid="collapsedControl"]:hover {
    background: var(--bg-hover) !important;
    border-color: var(--border-hover) !important;
    color: var(--text-primary) !important;
    box-shadow: var(--shadow-sm) !important;
}
button[data-testid="stSidebarCollapseButton"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    transition: all var(--transition) !important;
    opacity: 0.7;
}
button[data-testid="stSidebarCollapseButton"]:hover {
    opacity: 1;
    background: var(--bg-hover) !important;
    border-color: var(--border-hover) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* Sidebar collapse button Material Icons support */
button[data-testid="stSidebarCollapseButton"] {
    font-family: 'Material Icons' !important;
}

button[data-testid="stSidebarCollapseButton"] svg {
    display: none !important;
}

button[data-testid="stSidebarCollapseButton"]::before {
    content: 'keyboard_double_arrow_left';
    font-family: 'Material Icons', sans-serif !important;
    font-size: 18px !important;
    font-weight: normal !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
}

[data-testid="stSidebar"].--collapsed button[data-testid="stSidebarCollapseButton"]::before {
    content: 'keyboard_double_arrow_right';
}

[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    transition: all var(--transition) !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div:hover,
[data-testid="stSidebar"] .stMultiSelect > div > div:hover {
    border-color: rgba(59,130,246,0.4) !important;
    background: rgba(59,130,246,0.05) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.08) !important;
}
[data-testid="stSidebar"] .stSelectbox label { display: none; }
[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    margin: 16px 0 !important;
}

/* Sidebar nav items — better active state */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    border-radius: var(--radius-md) !important;
    padding: 8px 14px !important;
    margin-bottom: 2px !important;
    transition: all var(--transition) !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--text-faint) !important;
    display: flex !important;
    align-items: center !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(59,130,246,0.07) !important;
    border-color: rgba(59,130,246,0.18) !important;
    color: var(--text-secondary) !important;
    transform: translateX(2px) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[aria-checked="true"],
[data-testid="stSidebar"] [data-testid="stRadio"] [data-checked="true"] {
    background: rgba(59,130,246,0.12) !important;
    border-color: rgba(59,130,246,0.3) !important;
    color: #93C5FD !important;
}

/* ── Brand / Logo ────────────────────────────────────────────────────────── */
.brand-mark {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 22px 18px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 16px;
}
.brand-icon {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(59,130,246,0.4);
    transition: box-shadow var(--transition), transform var(--transition);
}
.brand-mark:hover .brand-icon {
    box-shadow: 0 6px 20px rgba(59,130,246,0.55);
    transform: scale(1.05);
}
.brand-text-main {
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.015em;
    line-height: 1.2;
}
.brand-text-sub {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important;
    color: var(--text-faint) !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 3px;
}

/* ── Sidebar Nav Labels ──────────────────────────────────────────────────── */
.nav-label {
    font-family: 'Inter', sans-serif !important;
    font-size: 9.5px !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-faint) !important;
    margin-bottom: 6px;
    display: block;
    padding: 0 4px;
}
.sidebar-stat {
    padding: 8px 12px;
    border-radius: var(--radius-md);
    margin-bottom: 4px;
    transition: all var(--transition);
    cursor: default;
}
.sidebar-stat:hover {
    background: rgba(255,255,255,0.04);
    transform: translateX(2px);
}
.sidebar-stat-val {
    font-family: 'Inter', sans-serif !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    line-height: 1.15;
    letter-spacing: -0.03em;
}
.sidebar-stat-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important;
    color: var(--text-faint) !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 2px;
}

/* ── Page Header ─────────────────────────────────────────────────────────── */
.page-header {
    padding: 44px 52px 36px;
    border-bottom: 1px solid var(--border-soft);
    margin-bottom: 36px;
    position: relative;
    overflow: hidden;
    animation: slideInLeft 0.35s ease-out;
}
.page-header::before {
    content: '';
    position: absolute; inset: 0;
    background:
        radial-gradient(ellipse 60% 140% at 0% 50%, rgba(59,130,246,0.06) 0%, transparent 65%),
        radial-gradient(ellipse 30% 80% at 100% 0%, rgba(139,92,246,0.03) 0%, transparent 60%);
    pointer-events: none;
}
.page-header::after {
    content: '';
    position: absolute; bottom: 0; left: 52px; right: 52px; height: 1px;
    background: linear-gradient(90deg, rgba(59,130,246,0.3) 0%, transparent 60%);
}
.page-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--text-faint);
    margin-bottom: 12px;
}
.page-title {
    font-family: 'Inter', sans-serif;
    font-size: clamp(22px, 2.8vw, 34px);
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text-primary);
    margin-bottom: 10px;
    line-height: 1.1;
}
.page-subtitle {
    font-size: 15px;
    color: var(--text-muted);
    line-height: 1.7;
    max-width: 640px;
    font-weight: 400;
}

/* ── Content wrapper ─────────────────────────────────────────────────────── */
.cw { padding-bottom: 60px; }

/* ── Glass Card ──────────────────────────────────────────────────────────── */
.glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px 22px;
    margin-bottom: 12px;
    transition: border-color var(--transition), box-shadow var(--transition), transform var(--transition);
}
.glass-card:hover {
    border-color: rgba(59,130,246,0.22);
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}

/* ── Section Divider ─────────────────────────────────────────────────────── */
.sec-div {
    font-family: 'Inter', sans-serif;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 0 0 10px;
    margin: 28px 0 16px;
    border-bottom: 1px solid var(--border-soft);
    position: relative;
}
.sec-div::before {
    content: '';
    position: absolute; bottom: -1px; left: 0;
    width: 32px; height: 1px;
    background: var(--accent-blue);
    border-radius: 1px;
}

/* ── Hero (Home page) ────────────────────────────────────────────────────── */
.hero-wrap {
    padding: 40px 56px 52px;
    background: linear-gradient(160deg, #08111F 0%, #090E1A 55%, #0B1525 100%);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    position: relative; overflow: hidden;
}
.hero-pills { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 28px; }
.hero-pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 5px 14px; border-radius: 100px;
    font-size: 11px; font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    color: var(--text-faint);
    transition: all var(--transition);
    cursor: default;
}
.hero-pill:hover {
    background: rgba(59,130,246,0.1);
    border-color: rgba(59,130,246,0.3);
    color: #93C5FD;
    transform: translateY(-1px);
}
.accent-pill {
    background: rgba(59,130,246,0.12);
    border-color: rgba(59,130,246,0.3);
    color: #60A5FA;
}
.pill { display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 13px; border-radius: 100px;
    font-size: 11px; font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.04em; border: 1px solid var(--border); color: var(--text-muted); }
.pill-orange { background:rgba(245,158,11,0.09); border-color:rgba(245,158,11,0.25); color:#FBBF24; }
.pill-blue   { background:rgba(59,130,246,0.09); border-color:rgba(59,130,246,0.25); color:#60A5FA; }
.pill-purple { background:rgba(139,92,246,0.09); border-color:rgba(139,92,246,0.25); color:#A78BFA; }
.pill-green  { background:rgba(16,185,129,0.09); border-color:rgba(16,185,129,0.25); color:#34D399; }

.hero-h1 {
    font-family: 'Caldris', sans-serif; !important;
    font-size: clamp(30px, 4vw, 65px);
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: -0.04em;
    color: var(--text-primary);
    margin-bottom: 30px;

}
.acc-orange { color: #F59E0B; }
.acc-blue   { color: #60A5FA; }
.acc-purple { color: #A78BFA; }
.acc-green  { color: #34D399; }
.hero-sub {
    font-size: 16.5px;
    color: var(--text-muted);
    line-height: 1.85;
    max-width: 640px;
    margin-bottom: 48px;
    font-weight: 400;
}
.hero-sub strong { color: var(--text-secondary); font-weight: 600; }

/* ── KPI Strip ───────────────────────────────────────────────────────────── */
.kpi-strip {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: rgba(255,255,255,0.05);
    border-radius: var(--radius-lg);
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 0;
}
.kpi-cell {
    background: var(--bg-card);
    padding: 28px 24px;
    position: relative;
    cursor: default;
    transition: background var(--transition-slow), box-shadow var(--transition-slow), transform var(--transition);
    overflow: hidden;
}
.kpi-cell::after {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    border-radius: 1px;
    transition: opacity var(--transition);
}
.kpi-cell::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(160deg, rgba(255,255,255,0.015) 0%, transparent 60%);
    pointer-events: none;
    transition: opacity var(--transition-slow);
    opacity: 0;
}
.kpi-cell:hover::before { opacity: 1; }
.kpi-cell:hover {
    background: var(--bg-hover);
    transform: translateY(-3px);
}
.kpi-cell-orange:hover { box-shadow: 0 4px 24px rgba(245,158,11,0.12), var(--shadow-md); }
.kpi-cell-blue:hover   { box-shadow: 0 4px 24px rgba(59,130,246,0.12),  var(--shadow-md); }
.kpi-cell-purple:hover { box-shadow: 0 4px 24px rgba(139,92,246,0.12),  var(--shadow-md); }
.kpi-cell-red:hover    { box-shadow: 0 4px 24px rgba(239,68,68,0.12),   var(--shadow-md); }
.kpi-cell-green:hover  { box-shadow: 0 4px 24px rgba(16,185,129,0.12),  var(--shadow-md); }
.kpi-cell-orange::after { background: linear-gradient(90deg, #F59E0B, transparent 75%); }
.kpi-cell-blue::after   { background: linear-gradient(90deg, #3B82F6, transparent 75%); }
.kpi-cell-purple::after { background: linear-gradient(90deg, #8B5CF6, transparent 75%); }
.kpi-cell-red::after    { background: linear-gradient(90deg, #EF4444, transparent 75%); }
.kpi-cell-green::after  { background: linear-gradient(90deg, #10B981, transparent 75%); }
.kpi-label {
    font-family: 'Inter', sans-serif;
    font-size: 10px; font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase; margin-bottom: 14px;
}
.kpi-cell-orange .kpi-label { color: #FBBF24; }
.kpi-cell-blue   .kpi-label { color: #60A5FA; }
.kpi-cell-purple .kpi-label { color: #A78BFA; }
.kpi-cell-red    .kpi-label { color: #FCA5A5; }
.kpi-cell-green  .kpi-label { color: #6EE7B7; }
.kpi-val {
    font-family: 'Inter', sans-serif;
    font-size: 30px;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 8px;
    letter-spacing: -0.04em;
    animation: countUp 0.5s ease-out backwards;
}
.kpi-sub {
    font-size: 12px;
    color: var(--text-faint);
    font-weight: 400;
    line-height: 1.4;
}

/* ── 4-column KPI Grid ───────────────────────────────────────────────────── */
.kpi-grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 0 0 32px;
    padding: 0 48px;
}
.kpi-card {
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: var(--radius-xl);
    padding: 26px 28px;
    position: relative; overflow: hidden;
    cursor: default;
    transition: border-color var(--transition), box-shadow var(--transition), transform var(--transition), background var(--transition-slow);
}
.kpi-card:hover {
    background: var(--bg-hover);
    transform: translateY(-4px);
}
.kpi-card.c-orange:hover { border-color: rgba(245,158,11,0.3);  box-shadow: 0 8px 32px rgba(245,158,11,0.1),  var(--shadow-lg); }
.kpi-card.c-blue:hover   { border-color: rgba(59,130,246,0.35); box-shadow: 0 8px 32px rgba(59,130,246,0.12), var(--shadow-lg); }
.kpi-card.c-purple:hover { border-color: rgba(139,92,246,0.3);  box-shadow: 0 8px 32px rgba(139,92,246,0.1),  var(--shadow-lg); }
.kpi-card.c-red:hover    { border-color: rgba(239,68,68,0.3);   box-shadow: 0 8px 32px rgba(239,68,68,0.1),   var(--shadow-lg); }
.kpi-card.c-green:hover  { border-color: rgba(16,185,129,0.3);  box-shadow: 0 8px 32px rgba(16,185,129,0.1),  var(--shadow-lg); }
.kpi-card::after {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    border-radius: 1px;
}
.kpi-card.c-orange::after { background: linear-gradient(90deg,#F59E0B 0%,rgba(245,158,11,0.2) 70%,transparent 100%); }
.kpi-card.c-blue::after   { background: linear-gradient(90deg,#3B82F6 0%,rgba(59,130,246,0.2) 70%,transparent 100%); }
.kpi-card.c-purple::after { background: linear-gradient(90deg,#8B5CF6 0%,rgba(139,92,246,0.2) 70%,transparent 100%); }
.kpi-card.c-red::after    { background: linear-gradient(90deg,#EF4444 0%,rgba(239,68,68,0.2) 70%,transparent 100%); }
.kpi-card.c-green::after  { background: linear-gradient(90deg,#10B981 0%,rgba(16,185,129,0.2) 70%,transparent 100%); }
/* Subtle inner glow on hover via ::before */
.kpi-card::before {
    content: ''; position: absolute;
    bottom: 0; right: 0; width: 80px; height: 80px;
    border-radius: 50%; opacity: 0;
    transition: opacity var(--transition-slow);
    pointer-events: none;
}
.kpi-card:hover::before { opacity: 1; }
.kpi-card.c-orange::before { background: radial-gradient(circle, rgba(245,158,11,0.07) 0%, transparent 70%); }
.kpi-card.c-blue::before   { background: radial-gradient(circle, rgba(59,130,246,0.09) 0%, transparent 70%); }
.kpi-card.c-purple::before { background: radial-gradient(circle, rgba(139,92,246,0.07) 0%, transparent 70%); }
.kpi-card.c-red::before    { background: radial-gradient(circle, rgba(239,68,68,0.07) 0%, transparent 70%); }
.kpi-card.c-green::before  { background: radial-gradient(circle, rgba(16,185,129,0.07) 0%, transparent 70%); }

.kc-label {
    font-family: 'Inter', sans-serif;
    font-size: 10px; font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase; margin-bottom: 14px;
}
.kpi-card.c-orange .kc-label { color: #FBBF24; }
.kpi-card.c-blue   .kc-label { color: #60A5FA; }
.kpi-card.c-purple .kc-label { color: #A78BFA; }
.kpi-card.c-red    .kc-label { color: #FCA5A5; }
.kpi-card.c-green  .kc-label { color: #6EE7B7; }
.kc-val {
    font-family: 'Inter', sans-serif;
    font-size: 30px; font-weight: 800;
    color: var(--text-primary); line-height: 1;
    margin-bottom: 8px;
    letter-spacing: -0.04em;
    animation: countUp 0.45s ease-out backwards;
}
.kc-sub {
    font-size: 12.5px;
    color: var(--text-muted);
    font-weight: 400;
}

/* ── Segment Badge ───────────────────────────────────────────────────────── */
.seg-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 11px; border-radius: var(--radius-sm);
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px; font-weight: 500;
    letter-spacing: 0.02em;
    transition: all var(--transition);
}
.seg-badge:hover { opacity: 0.85; transform: scale(0.98); }

/* ── Alert Card ──────────────────────────────────────────────────────────── */
.alert-card {
    background: var(--bg-card);
    border: 1px solid rgba(239,68,68,0.15);
    border-left: 3px solid #EF4444;
    border-radius: var(--radius-xl);
    padding: 22px 26px;
    margin-bottom: 14px;
    transition: all var(--transition);
    position: relative;
    overflow: hidden;
}
.alert-card::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(239,68,68,0.025) 0%, transparent 50%);
    pointer-events: none;
    opacity: 0;
    transition: opacity var(--transition-slow);
}
.alert-card:hover {
    box-shadow: 0 8px 32px rgba(239,68,68,0.1), var(--shadow-md);
    transform: translateX(3px);
    border-color: rgba(239,68,68,0.3);
    background: var(--bg-card-alt);
}
.alert-card:hover::before { opacity: 1; }
.alert-name {
    font-size: 14.5px; font-weight: 600;
    color: var(--text-primary); line-height: 1.5;
    margin-bottom: 10px;
}
.alert-badge {
    display: inline-flex; align-items: center;
    padding: 4px 12px; border-radius: var(--radius-sm);
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px; font-weight: 600;
    background: rgba(239,68,68,0.1);
    color: #FCA5A5;
    border: 1px solid rgba(239,68,68,0.25);
    white-space: nowrap;
    transition: all var(--transition);
}
.alert-card:hover .alert-badge {
    background: rgba(239,68,68,0.16);
    border-color: rgba(239,68,68,0.4);
}
.alert-meta { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; }
.chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; padding: 3px 10px;
    border-radius: var(--radius-sm);
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    color: var(--text-muted);
    transition: all var(--transition);
}
.chip:hover {
    background: rgba(255,255,255,0.08);
    color: var(--text-secondary);
    border-color: rgba(255,255,255,0.14);
    transform: translateY(-1px);
}

/* ── SHAP mini cards ─────────────────────────────────────────────────────── */
.shap-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
.shap-mini {
    border-radius: var(--radius-md); padding: 12px 16px;
    transition: all var(--transition);
}
.shap-mini:hover { transform: translateY(-2px); }
.shap-mini.push    {
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.2);
}
.shap-mini.barrier {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.2);
}
.shap-mini.push:hover    { background: rgba(16,185,129,0.1);  box-shadow: 0 4px 12px rgba(16,185,129,0.08); }
.shap-mini.barrier:hover { background: rgba(239,68,68,0.1);   box-shadow: 0 4px 12px rgba(239,68,68,0.08); }
.shap-mini-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 5px;
}
.shap-mini.push    .shap-mini-lbl { color: #6EE7B7; }
.shap-mini.barrier .shap-mini-lbl { color: #FCA5A5; }
.shap-mini-feat {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 3px;
}
.shap-mini-val { font-size: 11px; color: var(--text-muted); }
.rec-box {
    border-radius: var(--radius-md); padding: 14px 18px;
    font-size: 13.5px; line-height: 1.8;
    color: var(--text-secondary);
    background: rgba(59,130,246,0.05);
    border: 1px solid rgba(59,130,246,0.14);
    transition: all var(--transition);
}
.rec-box:hover {
    background: rgba(59,130,246,0.08);
    border-color: rgba(59,130,246,0.25);
}
.rec-box strong { color: var(--text-primary); font-weight: 600; }

/* ── Product Card ────────────────────────────────────────────────────────── */
.product-card {
    border-radius: var(--radius-xl); padding: 26px 30px;
    margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.07);
    border-left-width: 3px;
    position: relative; overflow: hidden;
    background: var(--bg-card);
    transition: all var(--transition);
}
.product-card:hover {
    box-shadow: var(--shadow-xl);
    transform: translateY(-3px);
    background: var(--bg-card-alt);
    border-color: rgba(59,130,246,0.2);
}
.product-name {
    font-size: 15.5px; font-weight: 600;
    color: var(--text-primary); line-height: 1.45; margin-bottom: 14px;
}
.product-meta { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px; }
.meta-chip {
    font-family:'JetBrains Mono',monospace;
    font-size:10px; padding:4px 11px; border-radius:var(--radius-sm);
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.08);
    color:var(--text-muted);
    transition: all var(--transition);
}
.meta-chip:hover {
    background: rgba(255,255,255,0.08);
    color: var(--text-secondary);
}

/* ── SHAP Cards ──────────────────────────────────────────────────────────── */
.shap-card {
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: var(--radius-md); padding: 18px 20px; margin-bottom: 10px;
    transition: all var(--transition);
}
.shap-card:hover {
    border-color: rgba(59,130,246,0.3);
    box-shadow: 0 4px 16px rgba(59,130,246,0.07);
    transform: translateY(-2px);
    background: var(--bg-card-alt);
}
.shap-card-lbl {
    font-family:'JetBrains Mono',monospace;
    font-size:9px; letter-spacing:0.12em;
    text-transform:uppercase; margin-bottom:6px;
    color: var(--text-faint);
}
.shap-card-feat {
    font-family:'JetBrains Mono',monospace;
    font-size:16px; font-weight:600; color:var(--text-primary); margin-bottom:4px;
}
.shap-card-val { font-size:12.5px; color:var(--text-muted); line-height:1.55; }

/* ── Segment Banner ──────────────────────────────────────────────────────── */
.seg-banner {
    border-radius: var(--radius-xl); padding: 32px 36px;
    margin-bottom: 24px;
    border: 1px solid rgba(255,255,255,0.07);
    background: var(--bg-card);
    position: relative; overflow: hidden;
    transition: all var(--transition);
}
.seg-banner:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
    background: var(--bg-card-alt);
}
.seg-banner-title {
    font-family: 'Inter', sans-serif;
    font-size: 22px; font-weight: 800;
    letter-spacing: -0.025em; margin-bottom: 4px;
}
.seg-banner-tagline {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--text-faint); margin-bottom: 12px;
}
.seg-banner-desc {
    font-size: 14px; color: var(--text-muted);
    line-height: 1.8; max-width: 720px;
}
.seg-banner-desc strong { color: var(--text-secondary); font-weight: 600; }

/* ── Feature Bar ─────────────────────────────────────────────────────────── */
.feat-bar-wrap {
    margin-bottom: 16px;
    padding: 10px 14px;
    border-radius: var(--radius-md);
    background: rgba(255,255,255,0.02);
    border: 1px solid transparent;
    transition: all var(--transition);
}
.feat-bar-wrap:hover {
    background: rgba(255,255,255,0.04);
    border-color: rgba(255,255,255,0.07);
    transform: translateX(2px);
}
.feat-bar-hdr {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 8px;
}
.feat-bar-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px; color: var(--text-secondary); font-weight: 500;
}
.feat-bar-info {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; color: var(--text-faint);
}
.feat-bar-track {
    height: 6px; border-radius: 4px;
    background: rgba(255,255,255,0.07);
    overflow: hidden;
}
.feat-bar-fill {
    height: 6px; border-radius: 4px;
    transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
}

/* ── Model Badge ─────────────────────────────────────────────────────────── */
.model-badge {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(16,185,129,0.09);
    border: 1px solid rgba(16,185,129,0.22);
    border-radius: var(--radius-md); padding: 7px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px; color: #6EE7B7;
    margin-right: 8px; margin-bottom: 8px;
    transition: all var(--transition);
    cursor: default;
}
.model-badge:hover {
    background: rgba(16,185,129,0.15);
    border-color: rgba(16,185,129,0.4);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(16,185,129,0.1);
}
.model-badge.orange {
    background: rgba(245,158,11,0.09);
    border-color: rgba(245,158,11,0.22);
    color: #FBBF24;
}
.model-badge.orange:hover {
    background: rgba(245,158,11,0.15);
    border-color: rgba(245,158,11,0.4);
    box-shadow: 0 4px 12px rgba(245,158,11,0.1);
}

/* ── Walk grid (home nav cards) ──────────────────────────────────────────── */
.walk-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 0;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: var(--radius-lg); overflow: hidden;
}
.walk-step {
    padding: 22px 20px;
    border-right: 1px solid rgba(255,255,255,0.06);
    background: var(--bg-card);
    transition: all var(--transition);
    cursor: pointer;
}
.walk-step:last-child { border-right: none; }
.walk-step:hover {
    background: var(--bg-hover);
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(59,130,246,0.08);
}
.walk-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; color: var(--text-faint); margin-bottom: 8px;
    letter-spacing: 0.1em;
}
.walk-icon { font-size: 22px; margin-bottom: 10px; }
.walk-title {
    font-family: 'Inter', sans-serif;
    font-size: 12.5px; font-weight: 700; color: var(--text-secondary); margin-bottom: 5px;
}
.walk-sub { font-size: 11.5px; color: var(--text-faint); line-height: 1.55; }

/* ── PS grid (problem/solution) ──────────────────────────────────────────── */
.ps-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.ps-card {
    border-radius: var(--radius-xl); padding: 26px 28px;
    border: 1px solid rgba(255,255,255,0.07);
    background: var(--bg-card);
    position: relative; overflow: hidden;
    transition: all var(--transition);
}
.ps-card.ps-prob {
    background: rgba(239,68,68,0.025);
    border-color: rgba(239,68,68,0.15);
    border-left: 3px solid #EF4444;
}
.ps-card.ps-soln {
    background: rgba(16,185,129,0.025);
    border-color: rgba(16,185,129,0.15);
    border-left: 3px solid #10B981;
}
.ps-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-3px);
}
.ps-card.ps-prob:hover { border-color: rgba(239,68,68,0.3); box-shadow: 0 8px 32px rgba(239,68,68,0.07), var(--shadow-lg); }
.ps-card.ps-soln:hover { border-color: rgba(16,185,129,0.3); box-shadow: 0 8px 32px rgba(16,185,129,0.07), var(--shadow-lg); }
.ps-eyebrow {
    font-family: 'Inter', sans-serif;
    font-size: 9.5px; font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase; margin-bottom: 12px;
}
.ps-card.ps-prob .ps-eyebrow { color: #FCA5A5; }
.ps-card.ps-soln .ps-eyebrow { color: #6EE7B7; }
.ps-title {
    font-family: 'Inter', sans-serif;
    font-size: 16px; font-weight: 700;
    color: var(--text-primary); margin-bottom: 12px;
    line-height: 1.4;
    letter-spacing: -0.01em;
}
.ps-body { font-size: 13.5px; color: var(--text-muted); line-height: 1.8; }
.ps-body strong { color: var(--text-secondary); font-weight: 600; }

/* ── Info pill ───────────────────────────────────────────────────────────── */
.info-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 7px 15px; border-radius: var(--radius-md);
    font-size: 12px; color: var(--text-muted);
    background: rgba(59,130,246,0.07);
    border: 1px solid rgba(59,130,246,0.18);
    margin-bottom: 16px;
    transition: all var(--transition);
    cursor: default;
}
.info-pill:hover {
    background: rgba(59,130,246,0.12);
    color: var(--text-secondary);
    transform: translateY(-1px);
}

/* ── Leakage Banner ──────────────────────────────────────────────────────── */
.leakage-banner {
    background: var(--bg-card);
    border: 1px solid rgba(239,68,68,0.18);
    border-radius: var(--radius-xl);
    padding: 24px 30px;
    display: flex; align-items: center;
    justify-content: space-between; gap: 20px;
    margin-bottom: 28px;
    position: relative; overflow: hidden;
    transition: all var(--transition);
}
.leakage-banner:hover {
    border-color: rgba(239,68,68,0.3);
    box-shadow: 0 8px 32px rgba(239,68,68,0.07), var(--shadow-md);
    transform: translateY(-2px);
}
.leakage-banner::before {
    content: '';
    position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    background: linear-gradient(180deg, #EF4444, #F59E0B);
    border-radius: 2px;
}
.leakage-banner::after {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 40% 80% at 0% 50%, rgba(239,68,68,0.04) 0%, transparent 60%);
    pointer-events: none;
}
.lb-left { padding-left: 10px; position: relative; z-index: 1; }
.lb-right { font-size: 12.5px; color: var(--text-muted); line-height: 1.9; position: relative; z-index: 1; }
.lb-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5px; letter-spacing: 0.14em;
    text-transform: uppercase; color: #FCA5A5; margin-bottom: 6px;
}
.lb-amount {
    font-family: 'Inter', sans-serif;
    font-size: 32px; font-weight: 800;
    color: var(--text-primary); line-height: 1.05;
    letter-spacing: -0.04em;
}
.lb-desc { font-size: 12.5px; color: var(--text-muted); margin-top: 4px; }
.lb-stat { color: var(--text-muted); }
.lb-stat strong { color: var(--text-secondary); font-weight: 600; }

/* ── Dataframe ───────────────────────────────────────────────────────────── */
.stDataFrame { border-radius: var(--radius-md) !important; overflow: hidden !important; }
[data-testid="stDataFrame"] { border-radius: var(--radius-md) !important; }
[data-testid="stDataFrame"] table {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stDataFrame"] thead th {
    background: #0B1525 !important;
    color: var(--text-muted) !important;
    font-size: 10.5px !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: rgba(59,130,246,0.05) !important;
}

/* ── Metric ──────────────────────────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: var(--radius-lg) !important;
    padding: 18px 22px !important;
    transition: all var(--transition) !important;
}
div[data-testid="stMetric"]:hover {
    border-color: rgba(59,130,246,0.28) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-2px) !important;
}
div[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em !important;
}
div[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    color: var(--text-faint) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.07) !important;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-faint) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em;
    border-radius: 0 !important;
    border: none !important;
    padding: 10px 20px !important;
    transition: color var(--transition) !important;
    position: relative;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-secondary) !important;
    background: rgba(255,255,255,0.03) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    border-bottom: 2px solid var(--accent-blue) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 24px !important; }

/* ── Slider ──────────────────────────────────────────────────────────────── */
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #3B82F6, #1D4ED8) !important;
}
.stSlider .rc-slider-rail { background: var(--border) !important; }
.stSlider .rc-slider-handle {
    border-color: #3B82F6 !important;
    background: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
    transition: box-shadow var(--transition) !important;
}
.stSlider .rc-slider-handle:hover {
    box-shadow: 0 0 0 6px rgba(59,130,246,0.2) !important;
}

/* ── Select / Multiselect ────────────────────────────────────────────────── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-input) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    transition: all var(--transition) !important;
}
.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {
    border-color: rgba(59,130,246,0.4) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.07) !important;
}
.stSelectbox > div > div:focus-within,
.stMultiSelect > div > div:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.14) !important;
}

/* ── Text Input ──────────────────────────────────────────────────────────── */
.stTextInput > div > div > input {
    background: var(--bg-input) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    transition: all var(--transition) !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--text-faint) !important;
}
.stTextInput > div > div > input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.14) !important;
    outline: none !important;
}
.stTextInput > div > div > input:hover {
    border-color: rgba(59,130,246,0.4) !important;
}

/* ── Segment preview cards (home) ────────────────────────────────────────── */
.seg-preview-grid {
    display: grid; grid-template-columns: repeat(4,1fr);
    gap: 14px; margin-bottom: 36px;
}
.seg-preview-card {
    border-radius: var(--radius-xl); padding: 24px 22px;
    border: 1px solid rgba(255,255,255,0.07);
    background: var(--bg-card);
    cursor: pointer;
    transition: all var(--transition-slow);
    position: relative; overflow: hidden;
}
.seg-preview-card::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(160deg, rgba(255,255,255,0.02) 0%, transparent 60%);
    opacity: 0; pointer-events: none;
    transition: opacity var(--transition-slow);
}
.seg-preview-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow-xl);
    background: var(--bg-card-alt);
}
.seg-preview-card:hover::before { opacity: 1; }
.sp-icon { font-size: 24px; margin-bottom: 14px; }
.sp-name {
    font-family: 'Inter', sans-serif;
    font-size: 13.5px; font-weight: 800; margin-bottom: 6px;
    letter-spacing: -0.02em;
}
.sp-driver {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5px; letter-spacing: 0.06em;
    color: var(--text-faint); margin-bottom: 10px; text-transform: uppercase;
}
.sp-desc { font-size: 12.5px; color: var(--text-muted); line-height: 1.65; }
.sp-count {
    margin-top: 16px; font-family: 'JetBrains Mono', monospace;
    font-size: 11px; font-weight: 600;
}

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.09);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.16); }

/* ── Expander ────────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: var(--radius-md) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    transition: all var(--transition) !important;
}
.streamlit-expanderHeader:hover {
    border-color: rgba(59,130,246,0.3) !important;
    color: var(--text-secondary) !important;
    background: var(--bg-hover) !important;
    transform: translateX(1px) !important;
}
.streamlit-expanderContent {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    background: var(--bg-card) !important;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--bg-card) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 9px 20px !important;
    transition: all var(--transition) !important;
    letter-spacing: 0.01em;
}
.stButton > button:hover {
    background: var(--bg-hover) !important;
    border-color: rgba(59,130,246,0.4) !important;
    color: var(--text-primary) !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.1), var(--shadow-sm) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Notification / Info boxes ───────────────────────────────────────────── */
div[data-testid="stInfo"] {
    background: rgba(59,130,246,0.06) !important;
    border: 1px solid rgba(59,130,246,0.2) !important;
    border-radius: var(--radius-md) !important;
    color: #93C5FD !important;
}
div[data-testid="stWarning"] {
    background: rgba(245,158,11,0.07) !important;
    border: 1px solid rgba(245,158,11,0.2) !important;
    border-radius: var(--radius-md) !important;
}
div[data-testid="stError"] {
    background: rgba(239,68,68,0.07) !important;
    border: 1px solid rgba(239,68,68,0.2) !important;
    border-radius: var(--radius-md) !important;
}
div[data-testid="stSuccess"] {
    background: rgba(16,185,129,0.07) !important;
    border: 1px solid rgba(16,185,129,0.2) !important;
    border-radius: var(--radius-md) !important;
}

/* ── Radio buttons ───────────────────────────────────────────────────────── */
.stRadio > div { gap: 8px !important; }
.stRadio label {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    color: var(--text-muted) !important;
    padding: 7px 15px !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    background: var(--bg-card) !important;
    transition: all var(--transition) !important;
    cursor: pointer !important;
}
.stRadio label:hover {
    border-color: rgba(59,130,246,0.35) !important;
    color: var(--text-secondary) !important;
    background: var(--bg-hover) !important;
    transform: translateY(-1px) !important;
}

/* ── Checkbox ────────────────────────────────────────────────────────────── */
.stCheckbox label { color: var(--text-muted) !important; font-family: 'Inter', sans-serif !important; }
.stCheckbox label:hover { color: var(--text-secondary) !important; }

/* ── Code blocks ─────────────────────────────────────────────────────────── */
code {
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 4px !important;
    padding: 1px 6px !important;
    font-size: 12px !important;
    color: #93C5FD !important;
}

/* ── Tooltips / popovers ─────────────────────────────────────────────────── */
[data-testid="stTooltipIcon"] { color: var(--text-faint) !important; }

/* ── Focus ring (accessibility) ──────────────────────────────────────────── */
*:focus-visible {
    outline: 2px solid rgba(59,130,246,0.5) !important;
    outline-offset: 2px !important;
}

/* ── Number input ────────────────────────────────────────────────────────── */
.stNumberInput > div > div > input {
    background: var(--bg-input) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    transition: all var(--transition) !important;
}
.stNumberInput > div > div > input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.14) !important;
}

/* ── Sidebar multiselect tags ────────────────────────────────────────────── */
[data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] {
    background: rgba(59,130,246,0.13) !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    border-radius: var(--radius-sm) !important;
    color: #93C5FD !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 11px !important;
}

/* ── Loading spinner ─────────────────────────────────────────────────────── */
[data-testid="stSpinner"] { color: #3B82F6 !important; }

/* ── Staggered card animation ────────────────────────────────────────────── */
.kpi-card:nth-child(1) { animation-delay: 0.05s; }
.kpi-card:nth-child(2) { animation-delay: 0.10s; }
.kpi-card:nth-child(3) { animation-delay: 0.15s; }
.kpi-card:nth-child(4) { animation-delay: 0.20s; }

/* ── Insight banner ──────────────────────────────────────────────────────── */
.insight-banner {
    border-radius: var(--radius-xl);
    padding: 20px 26px;
    margin-bottom: 20px;
    border: 1px solid;
    position: relative; overflow: hidden;
    transition: all var(--transition);
}
.insight-banner:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

/* ═══════════════════════════════════════════════════════════════════════════
   PRODUCT INTELLIGENCE — ANIMATED KPI CARD SYSTEM
   Covers: count-up · card reveal · hover lift · shadow expansion ·
           glow border · number pop · staggered appearance
   ═══════════════════════════════════════════════════════════════════════════ */

/* ── 1. Keyframe library ─────────────────────────────────────────────────── */

/* Card slides up from below on load */
@keyframes p6CardReveal {
    0%   { opacity: 0; transform: translateY(22px) scale(0.97); }
    60%  { opacity: 1; transform: translateY(-3px) scale(1.005); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

/* Value pops at the end of count-up — scales up then settles */
@keyframes p6NumPop {
    0%   { transform: scale(1); }
    45%  { transform: scale(1.12); }
    70%  { transform: scale(0.96); }
    100% { transform: scale(1); }
}

/* Glow border pulses once after card settles */
@keyframes p6GlowPulse {
    0%   { box-shadow: var(--shadow-md); }
    40%  { box-shadow: var(--p6-glow, var(--glow-blue)), var(--shadow-lg); }
    100% { box-shadow: var(--shadow-md); }
}

/* Shimmer sweep across value on reveal */
@keyframes p6Shimmer {
    0%   { background-position: -200% center; }
    100% { background-position: 200% center; }
}

/* Count-up: value fades + rises as if counting */
@keyframes p6CountUp {
    0%   { opacity: 0; transform: translateY(10px) scale(0.92); filter: blur(3px); }
    55%  { opacity: 1; transform: translateY(-2px) scale(1.04); filter: blur(0); }
    100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
}

/* Subtle inner bg shimmer */
@keyframes p6InnerShimmer {
    0%   { opacity: 0; left: -60%; }
    50%  { opacity: 1; }
    100% { opacity: 0; left: 120%; }
}

/* ── 2. Animated KPI card container ─────────────────────────────────────── */
.p6-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin: 0 0 36px;
    padding: 0 48px;
}

.p6-kpi-card {
    --p6-accent:  #3B82F6;              /* overridden per color */
    --p6-accent-r: 59;
    --p6-accent-g: 130;
    --p6-accent-b: 246;
    --p6-glow: 0 0 28px rgba(var(--p6-accent-r),var(--p6-accent-g),var(--p6-accent-b),0.22),
               0 0 56px rgba(var(--p6-accent-r),var(--p6-accent-g),var(--p6-accent-b),0.09);

    position: relative;
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: var(--radius-xl);
    padding: 30px 30px 26px;
    overflow: hidden;
    cursor: default;

    /* reveal animation — stagger set per card via nth-child */
    animation: p6CardReveal 0.62s cubic-bezier(0.34, 1.56, 0.64, 1) both;

    /* transitions for hover */
    transition:
        transform    0.22s cubic-bezier(0.34, 1.56, 0.64, 1),
        box-shadow   0.28s ease,
        border-color 0.22s ease,
        background   0.28s ease;
}

/* ── 2a. Staggered appearance delays ─────────────────────────────────────── */
.p6-kpi-card:nth-child(1) { animation-delay: 0.04s; }
.p6-kpi-card:nth-child(2) { animation-delay: 0.13s; }
.p6-kpi-card:nth-child(3) { animation-delay: 0.22s; }
.p6-kpi-card:nth-child(4) { animation-delay: 0.31s; }

/* ── 2b. Glow pulse fires once after card reveals ────────────────────────── */
.p6-kpi-card:nth-child(1) .p6-kc-val { animation-delay: 0.30s; }
.p6-kpi-card:nth-child(2) .p6-kc-val { animation-delay: 0.39s; }
.p6-kpi-card:nth-child(3) .p6-kc-val { animation-delay: 0.48s; }
.p6-kpi-card:nth-child(4) .p6-kc-val { animation-delay: 0.57s; }

/* The glow border pulse fires once, timed after the card has landed */
.p6-kpi-card:nth-child(1) { animation: p6CardReveal 0.62s cubic-bezier(0.34,1.56,0.64,1) 0.04s both, p6GlowPulse 0.9s ease-out 0.55s 1; }
.p6-kpi-card:nth-child(2) { animation: p6CardReveal 0.62s cubic-bezier(0.34,1.56,0.64,1) 0.13s both, p6GlowPulse 0.9s ease-out 0.64s 1; }
.p6-kpi-card:nth-child(3) { animation: p6CardReveal 0.62s cubic-bezier(0.34,1.56,0.64,1) 0.22s both, p6GlowPulse 0.9s ease-out 0.73s 1; }
.p6-kpi-card:nth-child(4) { animation: p6CardReveal 0.62s cubic-bezier(0.34,1.56,0.64,1) 0.31s both, p6GlowPulse 0.9s ease-out 0.82s 1; }

/* ── 2c. Color variants ──────────────────────────────────────────────────── */
.p6-kpi-card.p6-orange { --p6-accent: #F59E0B; --p6-accent-r:245; --p6-accent-g:158; --p6-accent-b:11; }
.p6-kpi-card.p6-blue   { --p6-accent: #3B82F6; --p6-accent-r:59;  --p6-accent-g:130; --p6-accent-b:246; }
.p6-kpi-card.p6-green  { --p6-accent: #10B981; --p6-accent-r:16;  --p6-accent-g:185; --p6-accent-b:129; }
.p6-kpi-card.p6-red    { --p6-accent: #EF4444; --p6-accent-r:239; --p6-accent-g:68;  --p6-accent-b:68; }
.p6-kpi-card.p6-purple { --p6-accent: #8B5CF6; --p6-accent-r:139; --p6-accent-g:92;  --p6-accent-b:246; }

/* ── 2d. Accent top bar ──────────────────────────────────────────────────── */
.p6-kpi-card::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    border-radius: 3px 3px 0 0;
    background: linear-gradient(
        90deg,
        var(--p6-accent) 0%,
        rgba(var(--p6-accent-r),var(--p6-accent-g),var(--p6-accent-b),0.18) 70%,
        transparent 100%
    );
}

/* ── 2e. Shimmer sweep on load ───────────────────────────────────────────── */
.p6-kpi-card::before {
    content: '';
    position: absolute; top: 0; bottom: 0; left: -60%;
    width: 45%; border-radius: 50%;
    background: linear-gradient(
        90deg, transparent 0%,
        rgba(var(--p6-accent-r),var(--p6-accent-g),var(--p6-accent-b),0.05) 50%,
        transparent 100%
    );
    animation: p6InnerShimmer 0.8s ease-out both;
    pointer-events: none;
}
.p6-kpi-card:nth-child(1)::before { animation-delay: 0.55s; }
.p6-kpi-card:nth-child(2)::before { animation-delay: 0.64s; }
.p6-kpi-card:nth-child(3)::before { animation-delay: 0.73s; }
.p6-kpi-card:nth-child(4)::before { animation-delay: 0.82s; }

/* ── 2f. Corner glow orb ─────────────────────────────────────────────────── */
.p6-kpi-card-orb {
    position: absolute; bottom: -20px; right: -20px;
    width: 90px; height: 90px; border-radius: 50%;
    background: radial-gradient(
        circle,
        rgba(var(--p6-accent-r),var(--p6-accent-g),var(--p6-accent-b),0.10) 0%,
        transparent 70%
    );
    pointer-events: none;
    transition: opacity 0.28s ease, transform 0.28s ease;
    opacity: 0.6;
}
.p6-kpi-card:hover .p6-kpi-card-orb {
    opacity: 1;
    transform: scale(1.3);
}

/* ── 3. Hover: lift + shadow expansion + glow border ─────────────────────── */
.p6-kpi-card:hover {
    transform: translateY(-6px) scale(1.015);
    background: var(--bg-card-alt);
    border-color: rgba(var(--p6-accent-r),var(--p6-accent-g),var(--p6-accent-b),0.35);
    box-shadow:
        0 14px 40px rgba(var(--p6-accent-r),var(--p6-accent-g),var(--p6-accent-b),0.16),
        0 4px 12px  rgba(0,0,0,0.5),
        0 0 0 1px   rgba(var(--p6-accent-r),var(--p6-accent-g),var(--p6-accent-b),0.20);
}

/* ── 4. KPI label ────────────────────────────────────────────────────────── */
.p6-kc-label {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 16px;
    color: rgba(var(--p6-accent-r),var(--p6-accent-g),var(--p6-accent-b),0.9);
    transition: color 0.2s ease;
    position: relative; z-index: 1;
}
.p6-kpi-card:hover .p6-kc-label {
    color: rgba(var(--p6-accent-r),var(--p6-accent-g),var(--p6-accent-b),1);
}

/* ── 5. Count-up value — the hero element ───────────────────────────────── */
.p6-kc-val {
    font-family: 'Inter', sans-serif;
    font-size: 36px;             /* ↑ larger for visibility */
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 10px;
    letter-spacing: -0.04em;
    position: relative; z-index: 1;

    /* Count-up reveal */
    animation: p6CountUp 0.55s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

/* Number pop: fires after count-up completes */
.p6-kpi-card:nth-child(1) .p6-kc-val { animation: p6CountUp 0.55s cubic-bezier(0.34,1.56,0.64,1) 0.30s both, p6NumPop 0.32s ease-out 0.85s 1; }
.p6-kpi-card:nth-child(2) .p6-kc-val { animation: p6CountUp 0.55s cubic-bezier(0.34,1.56,0.64,1) 0.39s both, p6NumPop 0.32s ease-out 0.94s 1; }
.p6-kpi-card:nth-child(3) .p6-kc-val { animation: p6CountUp 0.55s cubic-bezier(0.34,1.56,0.64,1) 0.48s both, p6NumPop 0.32s ease-out 1.03s 1; }
.p6-kpi-card:nth-child(4) .p6-kc-val { animation: p6CountUp 0.55s cubic-bezier(0.34,1.56,0.64,1) 0.57s both, p6NumPop 0.32s ease-out 1.12s 1; }

/* On hover, value nudges up slightly */
.p6-kpi-card:hover .p6-kc-val {
    transform: scale(1.03);
    transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* ── 6. Subtitle ─────────────────────────────────────────────────────────── */
.p6-kc-sub {
    font-size: 13px;             /* ↑ more readable */
    color: var(--text-muted);
    font-weight: 400;
    line-height: 1.45;
    position: relative; z-index: 1;
    transition: color 0.2s ease;
}
.p6-kpi-card:hover .p6-kc-sub {
    color: var(--text-secondary);
}

/* ── 7. Global font-size boosts for p6 readability ──────────────────────── */
.p6-product-name {
    font-family: 'Inter', sans-serif;
    font-size: 17px;             /* ↑ was 15px */
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.45;
    margin-bottom: 14px;
    letter-spacing: -0.01em;
}

.p6-chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;             /* ↑ was 10px */
    padding: 5px 13px;
    border-radius: var(--radius-sm);
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    color: var(--text-muted);
    transition: all var(--transition);
}
.p6-chip:hover {
    background: rgba(255,255,255,0.09);
    color: var(--text-secondary);
    border-color: rgba(255,255,255,0.16);
    transform: translateY(-1px);
}

.p6-shap-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;             /* ↑ was 9.5px */
    letter-spacing: 0.09em;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.p6-shap-feat {
    font-family: 'Inter', sans-serif;
    font-size: 17px;             /* ↑ was 14px */
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 5px;
    letter-spacing: -0.01em;
}

.p6-shap-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;             /* ↑ was 11px */
    margin-bottom: 8px;
    font-weight: 500;
}

.p6-shap-desc {
    font-size: 13.5px;           /* ↑ was 11.5px */
    color: var(--text-muted);
    line-height: 1.7;
}

.p6-feat-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;             /* ↑ was 10.5px */
    color: var(--text-muted);
}
.p6-feat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--text-primary);
    font-weight: 500;
}
.p6-feat-delta {
    font-size: 11.5px;
}

.p6-action-num {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 800;
    flex-shrink: 0;
    margin-top: 1px;
}
.p6-action-text {
    font-size: 14px;             /* ↑ was 12.5px */
    line-height: 1.72;
    color: var(--text-secondary);
}

/* SHAP card enhanced */
.p6-shap-card {
    border-radius: var(--radius-lg);
    padding: 20px 22px;
    margin-bottom: 12px;
    transition: all var(--transition);
    position: relative; overflow: hidden;
}
.p6-shap-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
}
.p6-shap-card.push {
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.22);
}
.p6-shap-card.push:hover {
    background: rgba(16,185,129,0.1);
    border-color: rgba(16,185,129,0.38);
    box-shadow: 0 8px 28px rgba(16,185,129,0.1), var(--shadow-md);
}
.p6-shap-card.barrier {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.22);
}
.p6-shap-card.barrier:hover {
    background: rgba(239,68,68,0.1);
    border-color: rgba(239,68,68,0.38);
    box-shadow: 0 8px 28px rgba(239,68,68,0.1), var(--shadow-md);
}

/* Product card p6 enhanced */
.p6-product-card {
    border-radius: var(--radius-xl);
    padding: 28px 32px;
    margin: 10px 0 20px;
    border: 1px solid rgba(255,255,255,0.08);
    border-left-width: 3px;
    background: var(--bg-card);
    position: relative; overflow: hidden;
    transition: all 0.25s cubic-bezier(0.34, 1.2, 0.64, 1);
}
.p6-product-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
    background: var(--bg-card-alt);
}

/* Segment shift pulse animation */
@keyframes p6ShiftPulse {
    0%   { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
    30%  { box-shadow: 0 0 0 6px rgba(16,185,129,0.15); }
    70%  { box-shadow: 0 0 0 12px rgba(16,185,129,0.05); }
    100% { box-shadow: 0 0 0 16px rgba(16,185,129,0); }
}
.p6-shift-box {
    border-radius: var(--radius-lg);
    padding: 18px 22px;
    margin-top: 16px;
    background: rgba(16,185,129,0.05);
    border: 1px solid rgba(16,185,129,0.25);
    animation: p6ShiftPulse 1.2s cubic-bezier(0.4,0,0.2,1) 0.1s 2;
    position: relative; overflow: hidden;
}
.p6-shift-box::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 60% 80% at 0% 50%, rgba(16,185,129,0.06) 0%, transparent 65%);
    pointer-events: none;
}

/* Delta badge in simulator */
.p6-delta-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 9px; border-radius: 100px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; font-weight: 600;
    transition: all var(--transition);
}
.p6-delta-badge.up   { background: rgba(16,185,129,0.12); color:#34D399; border:1px solid rgba(16,185,129,0.25); }
.p6-delta-badge.down { background: rgba(239,68,68,0.12);  color:#F87171; border:1px solid rgba(239,68,68,0.25); }
.p6-delta-badge.same { background: rgba(255,255,255,0.05);color:var(--text-faint);border:1px solid rgba(255,255,255,0.08); }

/* Simulator slider labels — bigger */
.p6-slider-label {
    font-family: 'Inter', sans-serif;
    font-size: 12.5px;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 4px;
    letter-spacing: 0.01em;
}
.p6-slider-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}

/* Section dividers in p6 */
.p6-sec-div {
    font-family: 'Inter', sans-serif;
    font-size: 13px;             /* ↑ was 11.5px */
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 0 0 11px;
    margin: 30px 0 18px;
    border-bottom: 1px solid var(--border-soft);
    position: relative;
}
.p6-sec-div::before {
    content: '';
    position: absolute; bottom: -1px; left: 0;
    width: 36px; height: 2px;
    background: var(--accent-blue);
    border-radius: 1px;
}

/* Quick-stat cards (empty state) */
.p6-qs-card {
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: var(--radius-xl);
    padding: 28px 20px 24px;
    text-align: center;
    transition: all 0.25s cubic-bezier(0.34, 1.4, 0.64, 1);
    position: relative; overflow: hidden;
    animation: p6CardReveal 0.5s cubic-bezier(0.34, 1.4, 0.64, 1) both;
}
.p6-qs-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: var(--shadow-xl);
    background: var(--bg-card-alt);
}
.p6-qs-card:nth-child(1) { animation-delay: 0.04s; }
.p6-qs-card:nth-child(2) { animation-delay: 0.11s; }
.p6-qs-card:nth-child(3) { animation-delay: 0.18s; }
.p6-qs-card:nth-child(4) { animation-delay: 0.25s; }

/* rec-box bigger for p6 */
.p6-rec-box {
    border-radius: var(--radius-lg); padding: 18px 22px;
    font-size: 14.5px; line-height: 1.85;
    color: var(--text-secondary);
    background: rgba(59,130,246,0.05);
    border: 1px solid rgba(59,130,246,0.16);
    transition: all var(--transition);
    margin-bottom: 28px;
}
.p6-rec-box:hover {
    background: rgba(59,130,246,0.08);
    border-color: rgba(59,130,246,0.28);
    box-shadow: 0 4px 16px rgba(59,130,246,0.07);
}
.p6-rec-box strong { color: var(--text-primary); font-weight: 600; }

/* Simulator expander header override */
[data-testid="stExpander"] summary {
    font-size: 14.5px !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    padding: 14px 18px !important;
}

</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# HTML COMPONENT BUILDERS — all signatures unchanged
# ─────────────────────────────────────────────────────────────────────────────

def page_header(eyebrow: str, title: str, subtitle: str) -> str:
    return f"""
    <div class="page-header">
      <div class="page-eyebrow">{eyebrow}</div>
      <div class="page-title">{title}</div>
      <div class="page-subtitle">{subtitle}</div>
    </div>"""


def kpi_card(label: str, value: str, subtitle: str, color: str = "orange") -> str:
    """4-column KPI card with animated count-up feel and richer hover."""
    return f"""
    <div class="kpi-card c-{color}">
      <div class="kc-label">{label}</div>
      <div class="kc-val">{value}</div>
      <div class="kc-sub">{subtitle}</div>
    </div>"""


def kpi_strip_5(cells: list[dict]) -> str:
    """cells: list of {{label, value, subtitle, color}} — exactly 5"""
    color_map = {
        "orange": "kpi-cell-orange",
        "blue":   "kpi-cell-blue",
        "purple": "kpi-cell-purple",
        "red":    "kpi-cell-red",
        "green":  "kpi-cell-green",
    }
    inner = ""
    for c in cells:
        cls = color_map.get(c.get("color", "orange"), "kpi-cell-orange")
        inner += f"""
        <div class="kpi-cell {cls}">
          <div class="kpi-label">{c['label']}</div>
          <div class="kpi-val">{c['value']}</div>
          <div class="kpi-sub">{c['subtitle']}</div>
        </div>"""
    return f'<div class="kpi-strip">{inner}</div>'


def seg_badge(seg: str, include_icon: bool = True) -> str:
    c    = SEG_COLORS.get(seg, "#888")
    icon = SEG_ICONS.get(seg, "") if include_icon else ""
    r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
    return (
        f'<span class="seg-badge" '
        f'style="background:rgba({r},{g},{b},0.13);color:{c};'
        f'border:1px solid rgba({r},{g},{b},0.28);">'
        f'{icon} {seg}</span>'
    )


def sec_div(label: str) -> str:
    return f'<div class="sec-div">{label}</div>'


def feat_bar(name: str, seg_val: float, overall_val: float, max_val: float, color: str) -> str:
    pct     = min((seg_val / max_val) * 100, 100) if max_val > 0 else 0
    delta   = ((seg_val - overall_val) / overall_val * 100) if overall_val != 0 else 0
    arrow   = "▲" if delta >= 0 else "▼"
    a_color = color if delta >= 0 else "#EF4444"
    return f"""
    <div class="feat-bar-wrap">
      <div class="feat-bar-hdr">
        <span class="feat-bar-name">{name}</span>
        <span class="feat-bar-info" style="color:{a_color};">
          {arrow} {abs(delta):.0f}% · {seg_val:.3f}
        </span>
      </div>
      <div class="feat-bar-track">
        <div class="feat-bar-fill" style="width:{pct:.1f}%;background:{color};"></div>
      </div>
    </div>"""


def model_badge(label: str, color: str = "green") -> str:
    cls = "orange" if color == "orange" else ""
    return f'<span class="model-badge {cls}">{label}</span>'


def alert_card(
    name: str,
    loss: float,
    seg: str,
    discount: float,
    savings: float,
    trust: float,
    rating: float,
    push_feat: str,
    push_val: float,
    barrier_feat: str,
    barrier_val: float,
    recommendation: str,
) -> str:
    sc = SEG_COLORS.get(seg, "#888")
    name_disp = name[:95] + ("…" if len(name) > 95 else "")
    shap_html = ""
    if push_feat and barrier_feat:
        shap_html = f"""
        <div class="shap-row">
          <div class="shap-mini push">
            <div class="shap-mini-lbl">▲ Classification driver (push)</div>
            <div class="shap-mini-feat">{push_feat}</div>
            <div class="shap-mini-val">SHAP = +{float(push_val):.4f}</div>
          </div>
          <div class="shap-mini barrier">
            <div class="shap-mini-lbl">▼ Upgrade blocker (barrier)</div>
            <div class="shap-mini-feat">{barrier_feat}</div>
            <div class="shap-mini-val">SHAP = {float(barrier_val):.4f}</div>
          </div>
        </div>"""
    return f"""
    <div class="alert-card">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px;">
        <div class="alert-name">{name_disp}</div>
        <span class="alert-badge">⚡ {fmt_inr(loss)}/mo</span>
      </div>
      <div class="alert-meta">
        {seg_badge(seg)}
        <span class="chip">Discount {discount:.0f}%</span>
        <span class="chip">savings_ratio {savings:.3f}</span>
        <span class="chip">Trust {trust:.2f}</span>
        <span class="chip">Rating {rating:.1f}★</span>
      </div>
      {shap_html}
      <div class="rec-box"><strong>Seller action →</strong> {recommendation}</div>
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FORMATTERS — unchanged
# ─────────────────────────────────────────────────────────────────────────────

def fmt_inr(v: float) -> str:
    if v is None or (isinstance(v, float) and v != v):
        return "₹0"
    v = float(v)
    if v >= 1e7:
        return f"₹{v/1e7:.2f} Cr"
    if v >= 1e5:
        return f"₹{v/1e5:.2f} L"
    return f"₹{v:,.0f}"


def fmt_num(v: float, decimals: int = 2) -> str:
    if v >= 1e9: return f"{v/1e9:.{decimals}f}B"
    if v >= 1e6: return f"{v/1e6:.{decimals}f}M"
    if v >= 1e3: return f"{v/1e3:.{decimals}f}K"
    return f"{v:.{decimals}f}"


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT INTELLIGENCE — ANIMATED KPI CARD BUILDER
# Used exclusively by p6_product.py for count-up + reveal + glow animations.
# Signature: (label, value, subtitle, color, card_index) → HTML string
# card_index 0-3 drives stagger timing via CSS nth-child
# ─────────────────────────────────────────────────────────────────────────────

_P6_COLOR_CLS = {
    "orange": "p6-orange",
    "blue":   "p6-blue",
    "green":  "p6-green",
    "red":    "p6-red",
    "purple": "p6-purple",
}

# Icon map per color to add visual interest
_P6_ICONS = {
    "orange": "📦",
    "blue":   "💰",
    "green":  "📈",
    "red":    "⚡",
    "purple": "🧠",
}


def kpi_card_animated(
    label: str,
    value: str,
    subtitle: str,
    color: str = "blue",
    card_index: int = 0,
) -> str:
    """
    Animated KPI card for Product Intelligence page.
    Features:
      - card reveal: slides up with spring easing (p6CardReveal)
      - count-up feel: value fades+rises (p6CountUp) with blur-to-clear
      - number pop: scale bounce at animation end (p6NumPop)
      - glow pulse: border glows once after card lands (p6GlowPulse)
      - shimmer sweep: light passes through card body (p6InnerShimmer)
      - hover lift: translateY(-6px) + scale(1.015) + shadow expansion
      - glow border on hover: colored box-shadow matching accent
      - stagger: nth-child delays (0.04s / 0.13s / 0.22s / 0.31s)
      - corner orb: radial glow orb bottom-right, expands on hover
    """
    cls  = _P6_COLOR_CLS.get(color, "p6-blue")
    icon = _P6_ICONS.get(color, "📊")

    return f"""
    <div class="p6-kpi-card {cls}">
      <div class="p6-kpi-card-orb"></div>
      <div class="p6-kc-label">{icon}&nbsp; {label}</div>
      <div class="p6-kc-val">{value}</div>
      <div class="p6-kc-sub">{subtitle}</div>
    </div>"""


def p6_kpi_grid(cards_html: str) -> str:
    """Wraps 4 kpi_card_animated() calls in the p6 grid div."""
    return f'<div class="p6-kpi-grid">{cards_html}</div>'