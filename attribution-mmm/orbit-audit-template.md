# Orbit Marketing Audit — 7-Check Framework

**Purpose:** 30-minute paid media audit for any brand. Shows what their dashboards are hiding.
**Output:** One-page report with findings + estimated cost of each blind spot.
**Use case:** Lead gen for Orbit, content series ("The Real Numbers"), Extern Episode 1.

---

## The 7 Checks

### CHECK 1 — Conversion Tracking Health
**Orbit call:** `get_conversion_actions(customer_id)`
**What to find:**
- Conversions with `included_in_conversions = false` (exist but not counting)
- `purchase` events not in primary conversions (campaigns optimizing toward wrong goal)
- Duplicate conversion actions inflating reported numbers
- `always_use_default_value = true` on revenue (means $0 revenue attributed)

**The reveal:** "Your Google campaigns think a conversion is worth $1. Your actual AOV is $X."

---

### CHECK 2 — The Attribution Black Hole (GA4 Unassigned)
**Orbit call:** `get_ga4_traffic_sources(property_id)`
**What to find:**
- % of conversions + revenue landing in "Unassigned" channel
- If Unassigned > 10% of revenue → UTMs are being stripped somewhere
- Common culprit: Stripe/payment redirect, email links, affiliate traffic

**The reveal:** "X% of your revenue has no source. You're making budget decisions blind on $Xk/mo."

---

### CHECK 3 — Reported ROAS vs. Estimated True ROAS Gap
**Orbit calls:** `get_campaign_performance()` + `get_ga4_conversions()`
**What to find:**
- Platform-reported conversions vs. GA4 conversions per channel
- If Meta says 4x ROAS but GA4 shows half the conversions → double-counting
- Branded search iROAS proxy: if branded spend > 15% of total Google spend, likely 0.7x true iROAS

**The reveal:** "Meta is reporting 4.2x ROAS. Based on GA4 cross-reference, estimated true ROAS is ~2.1x. You may be overspending by $X/mo."

---

### CHECK 4 — Budget Waste Scan (Campaigns Above CPA Threshold)
**Orbit call:** `get_campaign_performance(date_range="LAST_30_DAYS")`
**What to find:**
- Campaigns with spend > $500 and 0 conversions
- Campaigns with CPA > 3x target CPA
- Paused campaigns still showing in active budget planning
- YouTube/Demand Gen with < 0.5x ROAS (almost always waste for DTC)

**The reveal:** "$X is being spent on [campaign] with zero measurable return in 30 days."

---

### CHECK 5 — Search Term Pollution
**Orbit call:** `get_search_terms(customer_id, date_range="LAST_30_DAYS")`
**What to find:**
- Non-buyer intent terms spending > $50 (e.g. "how to", "free", "DIY")
- Competitor brand terms without a matching landing page
- Geographic irrelevant terms if geo-targeting is misconfigured
- Foreign language terms (Spanish, etc.) showing up in US campaigns

**The reveal:** "X search terms are eating $X/mo that will never convert. Here's the negative keyword list."

---

### CHECK 6 — Channel Saturation Proxy
**Orbit calls:** `get_spend_by_day()` + `get_campaign_performance()`
**What to find:**
- Channels where spend increased >20% but conversions flat or declining (diminishing returns)
- Channels underspending relative to conversion rate (room to scale)
- Day-of-week patterns showing budget exhausting early (impression share lost)

**The reveal:** "Meta is likely at or near saturation based on spend-to-conversion curve. Google has headroom. Recommend shifting $X/week."

---

### CHECK 7 — The MMM Proxy (Quick Version)
**Logic:** Without running a full Bayesian MMM, we can proxy it:
- Branded Google Search → almost always overstated (people were going to buy anyway)
- Non-branded Google Search → usually undervalued
- Meta Prospecting → depends heavily on creative refresh rate
- Email/organic → almost always undervalued in attribution

**The reveal:** "Based on channel mix benchmarks and your specific data patterns, we estimate [channel] is over-credited by ~X% and [channel] is under-credited. A proper incrementality test would confirm this in 3 weeks."

---

## Report Format

```
ORBIT MARKETING AUDIT — [BRAND NAME]
Pulled: [date] | Analyzed by: Orbit MCP

HEADLINE FINDING:
"[Brand] is spending $X/mo on paid media with an estimated $Y in 
preventable waste and $Z in untapped opportunity."

THE 7 CHECKS:
✅ Check 1 — Conversion Tracking: [finding]
🔴 Check 2 — Attribution Holes: [finding + $ impact]  
🟡 Check 3 — ROAS Gap: [finding + estimated gap]
🔴 Check 4 — Budget Waste: [finding + $ amount]
🟡 Check 5 — Search Pollution: [finding + $ amount]
✅ Check 6 — Channel Saturation: [finding]
🟡 Check 7 — MMM Proxy: [recommendation]

PRIORITY ACTIONS:
1. [Most impactful fix, estimated $ impact, time to implement]
2. [Second fix]
3. [Third fix]

WHAT A PROPER MEASUREMENT PROGRAM WOULD SHOW:
Run incrementality test on [top channel] → know true iROAS in 3 weeks.
Set up MMM → know how to allocate budget across all channels monthly.

[Orbit contact / CTA]
```

---

## Extern Episode 1 — Data Pull Checklist
- [ ] Google Ads: `customer_id` for Extern account (pull from Orbit MCP)
- [ ] GA4: `property_id` for Extern
- [ ] Meta: Extern ad account ID
- [ ] Run all 7 checks
- [ ] Generate report PDF
- [ ] Record walkthrough (founder-cam style, show the actual numbers)
- [ ] Hook: "This brand spends $X/mo on ads. Here's what their dashboard is hiding."
