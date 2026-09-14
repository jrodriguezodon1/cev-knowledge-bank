---
title: "Build vs Buy — AI Outreach (Artisan/$37M vs DIY in 17 min)"
date: 2026-09-12
tags: ["outreach", "ai-agents", "saas", "build-vs-buy", "influencer"]
category: paid-ads
source: "https://www.instagram.com/reel/DbEXteEtZ1z/"
layout: entry
---
# Build vs Buy — AI Outreach (Artisan/$37M vs DIY in 17 min)

**Source:** [Instagram Reel](https://www.instagram.com/reel/DbEXteEtZ1z/)
**Added:** 2026-09-12
**Tags:** outreach, ai-agents, saas, build-vs-buy, influencer

## The Thesis
Artisan raised $37M to be an "AI BDR" (Ava). A dev rebuilt the same thing in 17 minutes.

## DIY Architecture (the 17-min build)
1. Pick a cheap data source (Apollo, Clay, etc.) — same data as expensive tools
2. Store prospect data in a DB (Airtable, Notion, Supabase, Postgres)
3. Create a templates table — rows of outreach messages, actually written with a human brain
4. Build AI skills: given a contact's segment + stage → pick best template → rewrite for them → send
5. Log which template was used + track reply rate per template
6. Schedule skills to run async (cron)

## The Key Insight
The AI's job is NOT to write the email from scratch — it's to:
- Classify the contact (segment + stage)
- Select the right template
- Personalize it for that specific person
- Send + log

The human writes the templates. The AI scales the personalization.

## Why This Beats "Full AI" Outreach
Pure AI-generated emails = AI slop. Prospects can smell it. Reply rates tank.
Human-crafted templates + AI personalization = feels personal, scales infinitely.

## Application to CL Outbound Agent
This is exactly the architecture for CL's Outbound agent:
- Template table seeded with human-written outreach for different creator types
- Agent classifies creator (niche, follower tier, platform, prior brand deals)
- Selects + rewrites template for that creator specifically
- Tracks reply rates → surfaces best-performing templates
- Iterates copy based on data, not guesses
