# AI Workforce — Deal Desk Starter Kit

This is the buildable starting slice of the 35-agent studio described in the
[playbook doc](../..). It's the ~8 agents needed to run one service line
end-to-end: find a prospect, pitch them, draft the deal, deliver the work —
with a hard rule that **no email sends and no deal is final without you
explicitly approving it first.**

## What's here

- `agents/` — one Claude Code subagent definition per role. Drop the ones
  you want into a project's `.claude/agents/` folder (or point Claude Code
  at this folder) and invoke them with the `Agent` tool, e.g.
  `Agent(subagent_type: "outreach-agent", ...)`.
- `DEAL-DESK.md` — the approval workflow: exactly what gets shown to you
  before anything is sent or agreed to.

## The approval rule (read this before running anything)

Two agents touch the outside world: `outreach-agent` (drafts/sends emails)
and `account-manager` (finalizes deal terms). Both are written so that:

1. They only ever **draft**. They never call a send/finalize tool
   without pasting the exact email or deal terms into the conversation
   first and waiting for you to say "send it" / "approved" / equivalent.
2. Claude Code's own permission system backs this up: sending an email
   through a connector is a visible, hard-to-reverse action, so the
   harness itself will prompt you for confirmation before the send tool
   actually fires — even if a prompt tried to skip that step.

So "press agree" is real: you'll see the actual email or deal card, then
one confirmation is all it takes to send.

## Setup

1. **Connect Gmail** (or Outlook): claude.ai → Settings → Connectors →
   add the Gmail connector, then start a **new** Claude Code session
   (connectors only load at session start).
2. Copy the `agents/` you want into your project's `.claude/agents/`
   directory, or reference this folder directly.
3. Once Gmail is connected, check what the connector's tool is actually
   called in your session (e.g. `mcp__gmail__send_email`) and update the
   `tools:` line in `outreach-agent.md` and `account-manager.md` to match
   — placeholder names are marked `TODO` below.
4. Start with `opportunity-scout` → `lead-researcher` → `outreach-agent`
   for your first prospect batch. Full flow is in `DEAL-DESK.md`.

## Why only 8 agents, not all 35

The playbook's rollout plan (Section 13) is explicit: build the ~5-8
agents needed for one service line, land a paying client, then expand.
This kit is that starting slice — copywriter + dev + QA cover a
landing-page/content service; swap in other specialists from the full
roster once this loop is proven.
