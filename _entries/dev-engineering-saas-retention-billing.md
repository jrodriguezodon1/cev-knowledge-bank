---
title: "SaaS Retention & Billing Lessons — CreatorLookup"
date: 2026-09-10
tags: ["saas", "billing", "retention", "creatorlookup", "churn"]
category: dev-engineering
source: "CL metrics analysis (Sep 2026)"
layout: entry
---
# SaaS Retention & Billing Lessons — CreatorLookup

**Source:** CL metrics analysis (Sep 2026)
**Added:** 2026-09-10
**Tags:** saas, billing, retention, creatorlookup, churn

## The Numbers (Sep 2026)
- 280 signups/month
- 11 active paying subs → $1,829 MRR
- 5 past_due → $745 uncollected
- 2 cancel-flagged → $298 at risk
- 286 canceled total — 271 with no cancel_at_period_end flag (silent churn)

## Root Cause: Workflow Mismatch
4% signup-to-paid is the leak, not the ads ($150 CPA on $149/mo product is roughly break-even month 1).

Influencer discovery = campaign-trigger workflow, not daily use. Monthly SaaS billing is wrong for this use case.

## Billing Rules
- **Past-due recovery**: automate retry + dunning immediately — $745 is sitting there
- **Cancel-at-period-end**: intercept with win-back offer before period ends
- **Silent churn (271 users)**: never saw value, didn't even bother canceling — product failed them before value moment

## Paywall Placement
Paywall should sit over search RESULTS, not the platform entry. Show the count ("2,847 creators matching") but blur the names. Money at peak intent — they've already proven the data exists for their search.

## The Fix
Agentic ops layer creates daily/weekly touchpoints. Something always happening = product earns its keep every day instead of once every 6 weeks.
