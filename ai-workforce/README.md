# AI Workforce — Deal Desk

**90 agents across 18 departments**, in two connected divisions:

- **The original 40** — the studio playbook's 35 plus **Last Touch**
  (5 agents: grammar, visual/formatting, tone/sensitivity, brand
  consistency, final release) — client services, built as real Claude
  Code subagents in `agents/`. Identity, tone, pricing philosophy,
  payment processor, and compliance rules are centralized in
  **`BRAND.md`** — read it first, every client-facing agent points back
  to it.
- **Edgex Clips (50 agents, added 2026-09-24)** — owned video/social
  media, not client services: the studio makes and posts its own
  commentary/original video content on YouTube, Instagram, Facebook,
  and TikTok, aiming for real ad-revenue/creator-fund payouts. Read
  **`VIDEO-DESK.md`** first — it has this division's one hard rule
  (commentary/original only, never a raw repost) and its own 5-agent
  **Video Last Touch** gate. Connected to the original 40's building via
  Last Touch's second door — see `office/index.html`.

**Updated 2026-09-24, per the owner's direct instruction:** agents no
longer wait for the owner's personal sign-off before sending an email,
posting publicly, finalizing deal terms, or deploying a client build.
**Chief of Staff** approves or denies those on the owner's behalf, and
every decision — approved or denied, with the reason and the revenue
case — is logged and rolled into **one digest email a day** to
`hetilpatel500@gmail.com`. The **one thing that never moves**: spending
real money still needs the owner, via the weekly budget process.

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

An autonomous shift also runs on its own — a Routine (`trig_01BXBEAoHuB48YDR3xKzUbXG`,
**hourly**), not a session-bound cron job: it's owned by the
environment, spawns a fresh session on each firing, and survives this
session ending or the container restarting. Each firing rotates through
whichever agents have gone longest without fresh work, gives each a real
self-directed task, and writes results to the live status board on
[the office artifact](https://claude.ai/artifact/NzBSM8bbGtbqhariCBzfoH) —
no manual task assignment needed. Manage it from any session with
`list_triggers` / `delete_trigger`, or via the claude.ai Routines UI.

A **separate daily Routine** (`trig_01FmybD21HpqpiY3ymP1qK8Q`) wakes the
owner's own connected chat session once a day to actually send anything
Chief of Staff approved and email the daily digest — see the mechanical-
limit note in `DEAL-DESK.md` for why sending needs a connected session
specifically, not the hourly shift Routine.

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

Full detail in `DEAL-DESK.md`; the short version:

1. Every client-facing agent still **drafts first** — nothing is
   improvised live.
2. The draft clears **Last Touch** (5-agent quality gate — grammar,
   formatting, tone, brand consistency, final release).
3. **Chief of Staff** reviews the cleared draft and approves or denies
   it — checking it against `BRAND.md`, the studio's catalog, and plain
   judgment. This replaced the owner's personal review.
4. Only once approved, the agent that owns it actually sends, posts, or
   deploys — for real, no further confirmation from anyone.
5. Every decision (approved or denied, why, and the revenue case) is
   logged to the `decisions` collection and rolled into **one digest
   email a day**, sent to `hetilpatel500@gmail.com`.

**The one exception:** anything that spends the studio's own money (ad
budget, a paid tool, a new number or hosting plan) is never Chief of
Staff's to approve — that still goes through the owner via the weekly
budget process in `OPERATIONS.md`.

## Setup

1. **Email for `ai--edgex@edgex--ai.com`**: confirmed via this domain's
   live MX records — it's **Google Workspace**. The **Gmail** connector
   is connected and granted to the client-facing agents and to the
   autonomous shift Routine, so sends are real once Chief of Staff
   approves them.
2. Copy the `agents/` you want into your project's `.claude/agents/`
   directory, or reference this folder directly.
3. Start with `opportunity-scout` → `lead-researcher` → `outreach-agent`
   for your first prospect batch. Full flow is in `DEAL-DESK.md`.

## All 40, and how they stay busy

Every department in the playbook (Section 3-9) plus Last Touch now has
real agents here, not just descriptions. The client-facing ones
(`outreach-agent`, `account-manager`, `onboarding-agent`,
`support-help-desk-agent`, `partnerships-agent`, `email-marketing-agent`,
`community-engagement-agent`, `devops-deployment-agent`) draft, clear
Last Touch, get Chief of Staff's approval, then act for real — no owner
confirmation needed. `community-engagement-agent` is the one exception
to "acts for real": it has no posting tool connected yet, so an approved
post still needs a human to actually publish it. `paid-ads-agent` is the
one exception to the approval flow itself: ad spend is real money, so it
stays draft-only for the owner, same as the weekly budget process.
Everyone else (research, content, technical, ops, growth-analysis
roles) works freely since their output is internal until it clears Last
Touch and a client-facing agent moves it forward.

## Edgex Clips — the other 50

A second division, connected through Last Touch's second door, makes and
posts the studio's own video content instead of serving clients. Full
detail in `VIDEO-DESK.md`; the short version:

- **10 departments, 50 agents**: Trend Intelligence, Clip Sourcing &
  Rights, Commentary & Scripting, Production & Editing, Thumbnails &
  Titles, then one operations department per platform (YouTube, TikTok,
  Instagram & Facebook), Growth & Community (Video), and **Video Last
  Touch** (5 agents: copyright, platform policy, defamation/harassment,
  brand/tone, publish coordination).
- **The one hard rule**: commentary and reaction with real original
  work, never a raw repost of someone else's clip. "Non-copyrighted
  streamer clip" isn't a real legal category — Copyright Compliance
  Reviewer blocks anything that's just a re-upload.
- **Same approval model as the rest of the studio**: draft → Video Last
  Touch clears it → Chief of Staff approves or denies → the right
  platform agent queues it to post. `meta-ads-boost-agent` is this
  division's `paid-ads-agent` — spend still goes through the owner via
  the weekly budget process, same exception as everywhere else.
- **Monetization is reported honestly**, never assumed: each platform
  agent tracks the platform's actual payout eligibility (YouTube
  Partner Program, TikTok Creativity Program, Meta bonuses) rather than
  rounding up "views" into "money."
