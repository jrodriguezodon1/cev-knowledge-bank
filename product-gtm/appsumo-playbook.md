# AppSumo Launch Playbook — CreatorLookup

**Source:** Internal planning (Sep 2026)
**Added:** 2026-09-10
**Tags:** appsumo, creatorlookup, gtm, launch, ltda

## Why AppSumo for CL
- Eliminates "is $149/mo worth it for something I use 6x/year" friction — LTD pays once
- Instant brutally honest feedback loop
- Sets up the agentic ops beta announcement play
- Cohort of engaged users to validate next direction

## The Week-In Play
Email all LTD buyers ~7 days in:
> "Because of all your feedback, we're launching beta of our autonomous campaign tool. We've been using this internally for our agency. All you pay for is usage beyond what's included — generous packages."

Why it works: true (BYOB runs it), makes them feel like insiders, usage-based is right model for agentic layer.

## Technical Integration Needed
- Webhook endpoint for license events (activate/upgrade/refund)
- OAuth redirect for SSO (AppSumo → CL account)
- `license_key` storage in DB + tier → credit limit mapping
- Docs: https://docs.licensing.appsumo.com

## Status
Webhook integration in progress (as of Sep 2026). VSL recorded in Screen.Studio.
