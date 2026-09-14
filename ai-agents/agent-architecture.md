# Autonomous Agent Architecture — How It Actually Works

**Source:** Orbit Agent Platform master plan + CL agentic campaign build (Sep 2026)
**Added:** 2026-09-10
**Tags:** agents, architecture, mcp, orbit, creatorlookup, autonomy

## What Makes an Agent Actually Autonomous
Most "agent" products are just LLM calls with a wrapper. Real autonomous agents:
- Run on **cron**, not user prompts
- Maintain **state in DB** between runs
- Take **real actions** (send emails, update records, call APIs)
- **Escalate to humans** only when genuinely blocked
- **Learn** from outcomes (reply rates, engagement, conversion)

## Core Execution Pattern
1. Cron triggers agent (not user)
2. Agent reads current state from DB
3. LLM decides what action to take given state + instructions
4. Execute action via tool calls (email, API, DB write)
5. Write outcome back to DB + activity feed
6. If blocked → notify via iMessage with approval link
7. Human approves → agent continues

## Inter-Agent Coordination
Agents share state via DB, never direct calls. Fully decoupled. Each agent is stateless — state lives in DB.
Monitor reads DB → sees Pipeline stalled → writes directive to agent_configs → Pipeline reads it next run.

## iMessage as Control Plane
Sendblue webhook pattern:
- Agent hits decision point → generates approval token
- Texts user: "[@creator] asking about exclusivity — reply YES/NO or tap link"
- User replies from iMessage → webhook hits API → token resolves → agent executes

## MCP Connection
MCP (Model Context Protocol) = the USB-C of AI integrations. Orbit exposes all ad platforms behind one MCP server. Any MCP-compatible AI can use Orbit's tools without rebuilding integrations. This is the distribution moat.

## LLM Council Method
Before building something, pressure-test with multi-model council (Claude + GPT + Gemini + Grok). Each gives a steelman argument for/against. Surfaces fatal flaws early. Used on: scraper.creatorlookup.com/agents (verdict: conditional no — GDPR Article 6 risk), creatorlookup.com/agents (verdict: build MCP first, validate demand).
