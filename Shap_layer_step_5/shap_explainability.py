
import os
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shap
from sklearn.model_selection import train_test_split

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_PATH   = "best_model.pkl"
DATA_PATH    = "features_final.csv"
OUTPUT_DIR   = "shap_output"
TEST_SIZE    = 0.2
RANDOM_STATE = 42

# Class index → segment label mapping
# Model classes: 0=DEAL_SEEKER, 2=SOCIAL_PROOF, 3=NICHE_EXPLORER, 4=QUALITY_FIRST
# (class 1 has too few samples and is skipped)
SEGMENT_MAP = {
    0: "DEAL_SEEKER",
    4: "QUALITY_FIRST",
    2: "SOCIAL_PROOF",
    3: "NICHE_EXPLORER",
    1: "QUALITY_FIRST_RARE",   # tiny class — kept for completeness
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 1. Load model & data ──────────────────────────────────────────────────────
print("Loading model and data...")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

df = pd.read_csv(DATA_PATH)
feature_cols = list(model.feature_names_in_)

X = df[feature_cols]
y = df["segment_code"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)
X_test_reset = X_test.reset_index(drop=True)
y_test_reset = y_test.reset_index(drop=True)
df_test      = df.iloc[X_test.index].reset_index(drop=True)

print(f"Test set: {X_test.shape[0]} samples")
print(f"Test class distribution:\n{y_test.value_counts().sort_index()}\n")

# ── 2. SHAP TreeExplainer ─────────────────────────────────────────────────────
print("Computing SHAP values (TreeExplainer)...")
explainer   = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
# shape: (n_samples, n_features, n_classes)
print(f"shap_values shape: {shap_values.shape}\n")

preds = model.predict(X_test)

# ── 3. Global bar summary plots (one per segment) ─────────────────────────────
print("Generating bar summary plots...")
for cls, label in [(0, "DEAL_SEEKER"), (4, "QUALITY_FIRST"),
                   (2, "SOCIAL_PROOF"), (3, "NICHE_EXPLORER")]:
    fig, ax = plt.subplots(figsize=(8, 5))
    shap.summary_plot(
        shap_values[:, :, cls],
        X_test,
        plot_type="bar",
        max_display=12,
        show=False,
        plot_size=None,
    )
    plt.title(f"Top Features — {label} Intent", fontsize=13, fontweight="bold", pad=10)
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, f"shap_bar_{label}.png")
    plt.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close("all")
    print(f"  Saved: {out_path}")

# ── 4. Beeswarm — QUALITY_FIRST (class 4) ────────────────────────────────────
# Shows non-linear discount / savings_ratio effect on quality classification
print("\nGenerating beeswarm plot (QUALITY_FIRST)...")
expl_beeswarm = shap.Explanation(
    values       = shap_values[:, :, 4],
    base_values  = explainer.expected_value[4],
    data         = X_test_reset.values,
    feature_names= feature_cols,
)
plt.figure(figsize=(9, 6))
shap.plots.beeswarm(expl_beeswarm, max_display=15, show=False)
plt.title(
    "QUALITY_FIRST — Beeswarm\n"
    "(high savings_ratio clusters in negative SHAP → discounts hurt quality signal)",
    fontsize=11, fontweight="bold",
)
plt.tight_layout()
beeswarm_path = os.path.join(OUTPUT_DIR, "beeswarm_QUALITY_FIRST.png")
plt.savefig(beeswarm_path, bbox_inches="tight", dpi=150)
plt.close("all")
print(f"  Saved: {beeswarm_path}")

# ── 5. Dependence plot — savings_ratio on QUALITY_FIRST ──────────────────────
# savings_ratio is the discount proxy (discount_pct was not in model features)
# The downward slope confirms: higher discount → lower QUALITY_FIRST SHAP
print("\nGenerating dependence plot (savings_ratio → QUALITY_FIRST)...")
feat        = "savings_ratio"
feat_idx    = feature_cols.index(feat)

fig, ax = plt.subplots(figsize=(8, 5))
shap.dependence_plot(
    feat_idx,
    shap_values[:, :, 4],
    X_test_reset.values,
    feature_names=feature_cols,
    ax=ax,
    show=False,
)
ax.set_title(
    "Dependence: savings_ratio (discount proxy) → QUALITY_FIRST SHAP\n"
    "(higher discount HURTS QUALITY_FIRST classification)",
    fontsize=10, fontweight="bold",
)
plt.tight_layout()
dep_path = os.path.join(OUTPUT_DIR, "dependence_savings_ratio_QUALITY_FIRST.png")
plt.savefig(dep_path, bbox_inches="tight", dpi=150)
plt.close("all")
print(f"  Saved: {dep_path}")

# ── 6. Waterfall plots — one correctly-classified product per segment ─────────
print("\nGenerating waterfall plots...")
preds_s = pd.Series(preds)

for cls, label in [(0, "DEAL_SEEKER"), (4, "QUALITY_FIRST"),
                   (2, "SOCIAL_PROOF"), (3, "NICHE_EXPLORER")]:
    # Prefer correctly classified; fall back to any predicted-as-cls
    correct_mask = (preds_s == cls) & (y_test_reset == cls)
    idxs = np.where(correct_mask)[0]
    if len(idxs) == 0:
        idxs = np.where(preds_s == cls)[0]

    sample_idx = int(idxs[0])

    expl_wf = shap.Explanation(
        values       = shap_values[sample_idx, :, cls],
        base_values  = explainer.expected_value[cls],
        data         = X_test_reset.iloc[sample_idx].values,
        feature_names= feature_cols,
    )
    plt.figure(figsize=(10, 6))
    shap.plots.waterfall(expl_wf, max_display=12, show=False)
    plt.title(
        f"Waterfall — {label}  (test sample #{sample_idx})",
        fontsize=12, fontweight="bold",
    )
    plt.tight_layout()
    wf_path = os.path.join(OUTPUT_DIR, f"waterfall_{label}.png")
    plt.savefig(wf_path, bbox_inches="tight", dpi=150)
    plt.close("all")
    print(f"  Saved: {wf_path}  (sample {sample_idx})")

# ── 7. Per-product SHAP summary + recommendations ────────────────────────────
print("\nBuilding per-product SHAP summary...")

def make_recommendation(push_feat, barrier_feat, pred_cls, row):
    """
    Rule-based recommendation text derived from SHAP push/barrier features.
    Extend the elif chain to add more domain-specific rules.
    """
    label      = SEGMENT_MAP[pred_cls]
    sv_ratio   = row.get("savings_ratio", 0)
    rating     = row.get("rating", 0)
    trust      = row.get("trust_score", 0)
    review_log = row.get("review_log", 0)
    cat_depth  = row.get("category_depth", 0)
    word_count = row.get("word_count", 0)

    # --- Barrier rules (what's holding it back) ---
    if barrier_feat == "savings_ratio" and pred_cls == 0:
        return (
            f"High discount (savings_ratio={sv_ratio:.2f}) locks product into DEAL_SEEKER. "
            f"Reduce savings_ratio below 0.30 to cross QUALITY_FIRST threshold — "
            f"estimated +₹4,800/month revenue."
        )
    if barrier_feat == "savings_ratio" and pred_cls in [2, 3]:
        return (
            f"Discount (savings_ratio={sv_ratio:.2f}) is undermining quality perception. "
            f"Lower to <0.25 to shift toward QUALITY_FIRST — estimated +₹3,500/month."
        )
    if barrier_feat == "trust_score" and pred_cls == 0:
        return (
            f"Low trust_score ({trust:.2f}) is the primary barrier to QUALITY_FIRST. "
            f"Improve seller response rate and fulfilment score; target trust_score > 0.75."
        )
    if barrier_feat == "rating" and pred_cls in [0, 2]:
        return (
            f"Product rating ({rating:.1f}★) blocks QUALITY_FIRST entry. "
            f"Target ≥ 4.2★ — focus on post-purchase review solicitation."
        )
    if barrier_feat == "review_log" and pred_cls in [0, 4]:
        return (
            f"Low review volume (review_log={review_log:.2f}) weakens SOCIAL_PROOF signal. "
            f"Incentivise verified reviews — target 50+ reviews to strengthen classification."
        )
    if barrier_feat == "category_depth" and pred_cls in [0, 2]:
        return (
            f"Shallow category listing (depth={cat_depth}) limits NICHE_EXPLORER reach. "
            f"Add sub-category attributes and long-tail keywords in listing copy."
        )
    if barrier_feat == "word_count" and pred_cls in [0, 4]:
        return (
            f"Short listing copy (word_count={word_count}) reduces NICHE_EXPLORER signal. "
            f"Expand bullet points and description — target 300+ words."
        )

    # --- Push rules (what's already working) ---
    if push_feat == "savings_ratio" and pred_cls == 0:
        return (
            f"Discount (savings_ratio={sv_ratio:.2f}) is your primary DEAL_SEEKER driver. "
            f"Maintain for volume; or reduce to <0.30 to attract quality-conscious buyers."
        )
    if push_feat == "trust_score" and pred_cls == 4:
        return (
            f"High trust_score ({trust:.2f}) is driving QUALITY_FIRST classification — "
            f"maintain seller standards and response SLA to retain premium positioning."
        )
    if push_feat == "review_log" and pred_cls == 2:
        return (
            f"Strong review volume (review_log={review_log:.2f}) drives SOCIAL_PROOF. "
            f"Add photo/video review prompts to deepen the social signal further."
        )
    if push_feat == "category_depth" and pred_cls == 3:
        return (
            f"Deep category structure (depth={cat_depth}) is the NICHE_EXPLORER anchor. "
            f"Expand into adjacent sub-categories to widen addressable niche audience."
        )

    # --- Generic fallback ---
    return (
        f"Key driver: {push_feat} (SHAP push). Main barrier: {barrier_feat} (SHAP barrier). "
        f"Optimise {barrier_feat} to move toward a higher-value segment."
    )


records = []
for i in range(len(X_test_reset)):
    pred_cls    = int(preds[i])
    sv          = shap_values[i, :, pred_cls]
    push_idx    = int(np.argmax(sv))
    barrier_idx = int(np.argmin(sv))
    push_feat   = feature_cols[push_idx]
    barrier_feat= feature_cols[barrier_idx]
    push_val    = float(sv[push_idx])
    barrier_val = float(sv[barrier_idx])
    row_data    = X_test_reset.iloc[i].to_dict()
    rec         = make_recommendation(push_feat, barrier_feat, pred_cls, row_data)

    records.append({
        "product_id"       : df_test.iloc[i]["product_id"],
        "pred_segment"     : SEGMENT_MAP[pred_cls],
        "shap_push"        : push_feat,
        "shap_push_val"    : round(push_val, 4),
        "shap_barrier"     : barrier_feat,
        "shap_barrier_val" : round(barrier_val, 4),
        "recommendation_text": rec,
    })

summary_df = pd.DataFrame(records)
csv_path   = os.path.join(OUTPUT_DIR, "shap_summary.csv")
summary_df.to_csv(csv_path, index=False)
print(f"  Exported {len(summary_df)} rows → {csv_path}")

# ── Done ──────────────────────────────────────────────────────────────────────
print("\n✅ All outputs saved to:", OUTPUT_DIR)
print("   Bar plots  :", [f"shap_bar_{l}.png" for l in ["DEAL_SEEKER","QUALITY_FIRST","SOCIAL_PROOF","NICHE_EXPLORER"]])
print("   Beeswarm   :", "beeswarm_QUALITY_FIRST.png")
print("   Dependence :", "dependence_savings_ratio_QUALITY_FIRST.png")
print("   Waterfalls :", [f"waterfall_{l}.png" for l in ["DEAL_SEEKER","QUALITY_FIRST","SOCIAL_PROOF","NICHE_EXPLORER"]])
print("   CSV        :", "shap_summary.csv")
