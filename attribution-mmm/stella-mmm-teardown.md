# Stella — MMM + Incrementality Platform Teardown

**Source:** Instagram Reel — https://www.instagram.com/reel/Dc6V_w3PpTB/ + stellaheystella.com
**Date logged:** 2026-09-03
**Category:** attribution-mmm
**Founder:** Brenden DelaRua

---

## What They Do
Causal marketing measurement for mid-market e-commerce ($10M-$50M brands).
Core question: "Would this sale have happened WITHOUT the ad?"

Three methodologies running simultaneously:
1. **Holdout tests** — geo-based blackout experiments, turn off ads in test markets, measure revenue delta
2. **MMM (Media Mix Model)** — Bayesian regression, predicts revenue as spend shifts across channels
3. **Attribution** — standard click-based, treated as ONE signal among three (not the answer)

Weights all three by recency + confidence → one recommendation: "Scale TikTok. Hold Meta."

---

## Key Stats
- 98% prediction accuracy on one custom client (predict next month revenue within 98%)
- 250+ incrementality experiments/year on platform
- $400M+ ad spend measured
- Median iROAS across clients: 2.31x (vs platform-reported ~4x — massive gap)
- Branded Google Search iROAS: 0.70x (most brands are overpaying for branded)

---

## Pricing
- Free (basic holdout)
- $750/mo
- $3,000/mo (full platform — incrementality + MMM + always-on)
- $6,000/mo
- Managed engagements: custom

vs. Measured/Haus: $50K-$150K/year. Stella is 10-20x cheaper.

**Pricing trap they fell into:** Intentionally priced cheap for accessibility → enterprise brands assumed they couldn't be legit at that price. $100K brands didn't reach out for 6 months. Lesson: price signals quality.

---

## Tech Infrastructure (what's under the hood)
- Bayesian MMM (likely PyMC or Stan)
- Geo-based holdout experiment design (requires blocking by market in each ad platform)
- 90-120 days pre-period data for location selection/matching
- R² > 0.7, MAPE < 20% validation thresholds
- Python-generated charts for model outputs
- Budget optimizer + revenue optimizer (input target revenue → get channel allocation)
- Always-on incrementality monitoring between formal tests

---

## What to Steal for Orbit

**1. "One answer from multiple signals" UI**
Instead of separate dashboards per channel, synthesize into one verdict:
"Scale Google. Pause TikTok. Meta is at ceiling." — with confidence level.

**2. Confidence scoring on recommendations**
Every Orbit recommendation should show: Strong / Moderate / Low confidence + why.
Clients stop second-guessing. Becomes a trust layer.

**3. The free audit as acquisition**
Stella: "Run a real holdout free, no credit card."
Orbit equivalent: "Free marketing measurement audit — we pull your Google/Meta/GA4 and show you where you're blind."

**4. Always-on calibration**
Their MMM recalibrates every time a holdout completes. Not quarterly — continuous.
CreatorLookup: creator performance scores should recalibrate every time a campaign closes.

---

## The Audit Opportunity (Orbit)
Stella proves the market wants this. Orbit can do a 30-min version:
- Pull Google Ads → find misattributed conversions
- Pull Meta → show reported ROAS vs estimated true ROAS gap
- Pull GA4 → show Unassigned bucket (tracking holes)
- Quick MMM proxy → which channels are over/undervalued

Output: one-page report with findings + what it's costing them.
Use Extern as Episode 1 of public audit series.
