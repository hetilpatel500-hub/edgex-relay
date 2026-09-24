# AI Workforce — Deal Desk

40 agents across 8 departments — the original 35 from the studio
playbook plus **Last Touch** (5 agents: grammar, visual/formatting,
tone/sensitivity, brand consistency, final release) — are built as real
Claude Code subagents in `agents/`. Identity, tone, pricing philosophy,
payment processor, and compliance rules are centralized in
**`BRAND.md`** — read it first, every client-facing agent points back to
it. Hard rule, unchanged from day one: **no email sends and no deal is
final without you explicitly approving it first.**

Last Touch is the mandatory quality gate every department's
client-facing output passes through before reaching your approval queue
— see `DEAL-DESK.md`. It catches grammar issues, broken formatting,
offensive/insensitive language, and anything that drifts from
`BRAND.md` — it doesn't replace your approval, it makes sure what you're
approving is already clean.

The office's **Command Center** (button top-left) tracks every real
deal end to end: outreach sent, deal agreed, Last Touch cleared,
delivered, paid — live, from the same `deals` collection the studio
writes to as things actually happen. No deal exists there until it's
real.

An autonomous shift also runs on its own — a Routine (`trig_01DXuq5GDu23xeztwjRDbjPr`,
**hourly**), not a session-bound cron job: it's owned by the
environment, spawns a fresh session on each firing, and survives this
session ending or the container restarting. Each firing rotates through
whichever agents have gone longest without fresh work, gives each a real
self-directed task, and writes results to the live status board on
[the office artifact](https://claude.ai/artifact/NzBSM8bbGtbqhariCBzfoH) —
no manual task assignment needed. Manage it from any session with
`list_triggers` / `delete_trigger`, or via the claude.ai Routines UI.

See **`OPERATIONS.md`** for the rules governing that shift: zero idle
agents, the `opportunities` collection (so a money-making idea can't
quietly vanish), the `suggestions` collection (agents leaving each other
notes instead of letting an insight die in one department), and the
$20/week discretionary budget — a separate weekly Routine
(`trig_013fBypAUMXwnKkmx69PF7gA`, Mondays) that tops up a tracked ledger
and logs one Chief-of-Staff recommendation a week; any actual spend still
needs the owner's approval, since no agent can move real money.

## What's here

- `agents/` — one Claude Code subagent definition per role. Drop the ones
  you want into a project's `.claude/agents/` folder (or point Claude Code
  at this folder) and invoke them with the `Agent` tool, e.g.
  `Agent(subagent_type: "outreach-agent", ...)`.
- `DEAL-DESK.md` — the approval workflow: exactly what gets shown to you
  before anything is sent or agreed to.
- `BRAND.md` — identity (business name, anonymity), voice, pricing
  philosophy, payment processor, and compliance rules every client-facing
  agent follows.
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

1. **Connect email for `ai--edgex@edgex--ai.com`**: confirmed via this
   domain's live MX records — it's **Google Workspace**
   (`aspmx.l.google.com`, SPF set for `_spf.google.com`). So: claude.ai
   → Settings → Connectors → add the **Gmail** connector, sign in as
   `ai--edgex@edgex--ai.com` specifically (not a personal Gmail), then
   start a **new** Claude Code session (connectors only load at session
   start).
2. Copy the `agents/` you want into your project's `.claude/agents/`
   directory, or reference this folder directly.
3. Once the connector is live, check what its send tool is actually
   called in your session (e.g. `mcp__gmail__send_email`) and add it to
   the `tools:` line in `outreach-agent.md` and `account-manager.md` —
   every other client-facing agent stays draft-only by design.
4. Start with `opportunity-scout` → `lead-researcher` → `outreach-agent`
   for your first prospect batch. Full flow is in `DEAL-DESK.md`.

## All 40, and how they stay busy

Every department in the playbook (Section 3-9) plus Last Touch now has
real agents here, not just descriptions. The client-facing ones
(`outreach-agent`, `account-manager`, `onboarding-agent`,
`support-help-desk-agent`, `partnerships-agent`, `email-marketing-agent`,
`community-engagement-agent`, `paid-ads-agent`, `devops-deployment-agent`)
all carry the same rule: draft in full, get explicit confirmation, only
then act — nothing sends, posts, deploys, or spends money on its own.
Everyone else (research, content, technical, ops, growth-analysis
roles) works freely since their output is internal until it clears Last
Touch and a client-facing agent or the user moves it forward.
