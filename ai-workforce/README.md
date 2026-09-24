# AI Workforce — Deal Desk

All 35 agents from the studio playbook are built as real Claude Code
subagents in `agents/`. The studio's contact address is
`ai--edgex@edgex--ai.com` — every client-facing draft signs off from it.
Hard rule, unchanged from day one: **no email sends and no deal is final
without you explicitly approving it first.**

An autonomous shift also runs on its own (set up via a recurring cron in
the session that built this): every few hours it rotates through
whichever agents have gone longest without fresh work, gives each a real
self-directed task, and writes results to the live status board on
[the office artifact](https://claude.ai/artifact/NzBSM8bbGtbqhariCBzfoH) —
no manual task assignment needed. That job is session-bound (dies if the
session ends, hard-expires after 7 days) — recreate it in a fresh session
if you want it to keep running past that.

## What's here

- `agents/` — one Claude Code subagent definition per role. Drop the ones
  you want into a project's `.claude/agents/` folder (or point Claude Code
  at this folder) and invoke them with the `Agent` tool, e.g.
  `Agent(subagent_type: "outreach-agent", ...)`.
- `DEAL-DESK.md` — the approval workflow: exactly what gets shown to you
  before anything is sent or agreed to.
- `office/index.html` — a 3D floor plan of the studio: one room per
  department, click (or tap) a room to walk in and see its 5 agents and
  what each one does. Open the file in any browser, or serve it as a
  static page — no build step, no server required.

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

1. **Connect email for `ai--edgex@edgex--ai.com`**: claude.ai → Settings
   → Connectors → add whichever connector matches that address's actual
   mailbox provider (Gmail/Google Workspace, Outlook/Microsoft 365,
   etc.), then start a **new** Claude Code session (connectors only load
   at session start). Which provider hosts this domain's mail isn't
   confirmed yet — check before connecting.
2. Copy the `agents/` you want into your project's `.claude/agents/`
   directory, or reference this folder directly.
3. Once the connector is live, check what its send tool is actually
   called in your session (e.g. `mcp__gmail__send_email`) and add it to
   the `tools:` line in `outreach-agent.md` and `account-manager.md` —
   every other client-facing agent stays draft-only by design.
4. Start with `opportunity-scout` → `lead-researcher` → `outreach-agent`
   for your first prospect batch. Full flow is in `DEAL-DESK.md`.

## All 35, and how they stay busy

Every department in the playbook (Section 3-9) now has real agents here,
not just descriptions. The client-facing ones (`outreach-agent`,
`account-manager`, `onboarding-agent`, `support-help-desk-agent`,
`partnerships-agent`, `email-marketing-agent`, `community-engagement-agent`,
`paid-ads-agent`, `devops-deployment-agent`) all carry the same rule:
draft in full, get explicit confirmation, only then act — nothing sends,
posts, deploys, or spends money on its own. Everyone else (research,
content, technical, ops, growth-analysis roles) works freely since their
output is internal until a client-facing agent or the user moves it
forward.
