# Amazon Product Customer Intent Segmentation
## Rule Definitions & Buyer Psychology

---

## Overview

Each product row is scored against four mutually-exclusive intent segments using weighted boolean rules. When multiple segments fire simultaneously, the **highest weighted score wins** — resolving ambiguity in favour of the segment whose defining trait is most commercially meaningful. Products matching none of the rules are labelled **UNMATCHED**, which itself signals a potential gap in catalogue strategy.

---

## Segment Rules

### 1. 🏷️ DEAL_SEEKER  *(weight = 1.2)*

```
discount_pct > 45  AND  rating >= 3.8
```

**What it captures:** Products with aggressive (>45%) discounts that still maintain a respectable floor rating. The rating floor of 3.8 filters out damaged goods being cleared at a loss — a DEAL_SEEKER expects a bargain, not a defective product.

**Buyer psychology:** Price-motivated shoppers are primarily driven by *loss aversion* — they fear paying full price more than they desire product quality. Research in behavioural economics (Thaler's mental accounting) shows that a salient discount activates a "deal utility" separate from the product's acquisition utility. The 1.2 weight reflects that discount behaviour is common but not the highest-value signal; these customers are loyal to price, not brand.

**Business implication:** High sensitivity to promotions; likely to churn without continued discounting. Useful for volume-clearing and customer acquisition campaigns.

---

### 2. ⭐ QUALITY_FIRST  *(weight = 1.4 — highest)*

```
rating >= 4.3  AND  log1p(rating_count) >= log1p(500)  AND  discount_pct < 35
```

**What it captures:** Highly-rated products (top ~15% of the scale) with a statistically meaningful review base (≥500 reviews — enough to trust the signal) **and** low discount pressure. The `discount_pct < 35` guard is critical: it ensures we're not conflating a quality product that happens to be discounted with a genuine quality-seeker who pays near full price.

**Buyer psychology:** These buyers exhibit *quality heuristics* — they use rating and review volume as proxies for objective quality in the absence of physical inspection (a classic problem in e-commerce). The willingness to pay at low discount levels signals *prestige pricing sensitivity* and lower price elasticity. The highest weight (1.4) reflects that this segment is the most commercially valuable: high margin, low return rates, and strong brand affinity.

**Business implication:** Target with "Premium Pick" or "Top Rated" badges. Avoid unnecessary discounting — it can *reduce* purchase intent by signalling quality doubt (cf. Gneezy et al., 2014 on price–quality inference).

---

### 3. 👥 SOCIAL_PROOF  *(weight = 1.1)*

```
rating_count > q75_reviews (within top_cat)  AND  rating >= 4.0
```

**What it captures:** Products in the top quartile of review volume *within their own category* (not globally), combined with a solid rating. Using a **category-relative quantile** rather than an absolute threshold is deliberate — 10,000 reviews is ordinary for USB cables but exceptional for musical instruments.

**Buyer psychology:** Rooted in Cialdini's *social proof* principle — humans look to the behaviour of others under uncertainty. High review counts signal that many people have taken a purchase risk before you, reducing perceived risk. The 4.0 rating floor ensures the crowd signal is positive. Weight of 1.1 (lowest non-niche) reflects that social proof is a secondary, reinforcing signal rather than a primary purchase driver.

**Business implication:** Effective in retargeting and comparison pages. "Best Seller" and "Most Reviewed" labels activate this segment. Review acquisition campaigns have outsized ROI here.

---

### 4. 🔍 NICHE_EXPLORER  *(weight = 1.0)*

```
rating >= 4.2  AND  rating_count < 200  AND  category_depth >= 2
```

**What it captures:** High-quality products with very few reviews, sitting deep in the category tree. The `category_depth >= 2` condition ensures the product occupies a *specific* sub-niche (not a top-level generic). The `rating_count < 200` means the signal is early-stage — these are hidden gems not yet discovered by the mainstream.

**Buyer psychology:** Appeals to *exploratory* and *variety-seeking* buyers who derive utility from discovering underrated products before they go mainstream. This maps to *novelty-seeking* in personality psychology and the "underdog brand" effect (Paharia et al., 2011). Also attracts expert buyers who trust their own evaluation over crowd opinion. Weight of 1.0 is lowest — the segment is rare and the business case requires careful cultivation.

**Business implication:** Ideal for "Hidden Gem" editorial placements, early-adopter influencer seeding, and catalogue diversification. Low current revenue, but high long-term potential if reviews scale.

---

## Conflict Resolution Logic

When a product satisfies multiple segment conditions simultaneously (e.g., high rating AND big discount), the **weighted argmax** resolves the tie:

| Conflict Example | Winner |
|---|---|
| DEAL_SEEKER (1.2) vs QUALITY_FIRST (1.4) | QUALITY_FIRST |
| SOCIAL_PROOF (1.1) vs DEAL_SEEKER (1.2) | DEAL_SEEKER |
| NICHE_EXPLORER (1.0) vs any other | Any other |

The weights encode a deliberate **commercial priority hierarchy**: quality retention > deal-driven acquisition > social momentum > niche discovery.

---

## Segment Summary Statistics

| Segment | Count | Mean Price (₹) | Mean Rating | Mean Discount | Mean Reviews |
|---|---|---|---|---|---|
| DEAL_SEEKER | 730 | 1,507 | 4.15 | 62.96% | 20,535 |
| UNMATCHED | 454 | 4,301 | 3.89 | 37.66% | 6,241 |
| QUALITY_FIRST | 147 | 6,141 | 4.38 | 18.61% | 14,716 |
| SOCIAL_PROOF | 124 | 4,915 | 4.17 | 29.53% | 54,667 |
| NICHE_EXPLORER | 8 | 1,657 | 4.36 | 32.00% | 78 |

**Key observations:**
- DEAL_SEEKER is the dominant segment (49.9% of catalogue), driven by Amazon India's heavy promotional culture.
- QUALITY_FIRST commands the highest average price (₹6,141) with the lowest discount — exactly as expected for premium buyers.
- SOCIAL_PROOF has by far the highest mean review count (54,667) — the category-relative threshold correctly isolated genuinely viral products.
- NICHE_EXPLORER is rare (n=8) — a healthy sign that the rule is tight, not catching noise.
- UNMATCHED (31%) warrants attention: these products have average ratings (~3.89) and moderate discounts, suggesting they may benefit from quality improvement or repositioning before targeted campaigns.
