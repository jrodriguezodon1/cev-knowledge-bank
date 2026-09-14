# Agentic Campaign Ops — The Vision

**Source:** Internal architecture sessions + CL product pivot (Sep 2026)
**Added:** 2026-09-12
**Tags:** creatorlookup, agents, campaigns, outreach, autonomy

## The Core Problem
Discovery without execution is a dead end. Users find creators, export a CSV, go back to spreadsheets and Gmail. Monthly SaaS for a campaign-trigger workflow is a mismatch.

## The Fix: 5-Agent Stack

| Agent | Role |
|---|---|
| **Scout** | Vets creators against brief. Not random lists — scores engagement, audience fit, competitor conflicts |
| **Outbound** | Personalized sequences via Smartlead/Instantly. A/B tests subject lines. Monitors reply rates |
| **Triage** | Classifies replies (negotiating/questions/interested/declined). Routes to playbook response |
| **Pipeline** | Stall detection. Follow-ups every 3 days. Escalates at day 21 |
| **Monitor** | Campaign health. Posts vs target. Tells other agents to push harder if behind |

## How Agents Communicate
Agents share state via DB, not direct calls. Monitor reads DB, sees Pipeline is stalled, writes directive to agent_configs. Pipeline reads it on next run. Fully decoupled.

## iMessage as Control Plane
Agents text you via Sendblue when they need a decision. You reply from iMessage. Webhook hits CL API. Agent continues. No app required.

Morning digest: "3 campaigns active. Scout found 6 new creators overnight. 2 replies need your attention."
Blocker alert: "@musclemindset asking about exclusivity — your call. Reply YES/NO."

## AppSumo Announcement Play
~7 days after LTD launch: email all buyers saying we've been running this internally for BYOB and opening it up as beta. Usage-based pricing beyond included credits. This is the retention loop that makes CL a daily-use product.

## Status (Sep 2026)
- DB schema: ✅ live (agent_campaigns, agent_contacts, agent_configs, agent_activity)
- API routes: ✅ built (/api/agents/campaigns/*)
- UI: ✅ built (/industry/campaigns/agents/)
- PR: https://github.com/Creator-Economy-Ventures/CreatorLookup/pull/49
- Smartlead/Instantly keys: ⏳ needed
