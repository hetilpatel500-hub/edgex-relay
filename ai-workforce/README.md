# AI Workforce — Deal Desk

**120 studio agents across 23 departments** (plus the owner's 20-analyst Chart
Desk), in three divisions, with the 10-agent **Legal Desk** (added 2026-09-26)
checking everything that goes out (`LEGAL-DESK.md`):

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
  **Video Last Touch** gate.
- **The Dispatch (20 agents, added 2026-09-24)** — keeps every one of
  the other 90 agents working (finds an idle agent, assigns the correct
  next task) and, the instant it has nothing to dispatch, hunts new
  money-making opportunities and organizes the team to build them. Read
  **`DISPATCH.md`** first. Physically sits in the real gap between the
  other two divisions' buildings — see `office/index.html` and the note
  below.

The office is no longer one zero-gap building end to end: there's now a
real, visible gap between the original 40's building and Edgex Clips'
wing, with The Dispatch's own building sitting in that gap — three
distinct structures, not one sprawling complex.

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

The office page is the owner's live view of the studio, read straight
from the office database as the shifts write to it:

- **Badges** over each agent show its real state: working now, asked by
  the owner, blocked, worked in the last 2 hours, earlier, or no work
  yet. A strip under the title shows last activity, when the next shift
  starts, how many agents worked in the last 2 hours, what's waiting on
  the owner, the request queue, money-map progress and money earned.
- **Live** is a newest-first feed of agent updates, decisions, requests,
  outbox changes and applied repo changes, with a box for telling the
  studio what to do next (it writes a `requests` doc with
  `source: "studio-floor"` that the next shift handles first). A toast
  pops up when a shift writes something new.
- **Waiting on you** lists the `owner_actions` docs. Some have one-click
  choices (for example the held outreach): a choice writes a request
  tagged with `owner_action` and `choice` and marks the action done.
- **Money** tracks every real deal end to end (outreach sent, deal
  agreed, Last Touch cleared, delivered, paid), the opportunities by
  status, and the 100-item money map. No deal exists there until it's
  real.
- Clicking an agent (or a row in **All agents**) lets the owner assign it
  a task: that writes a request with the agent's id and sets the agent
  to "asked by you" until a shift picks it up.
- **Office life.** Each agent's pose and monitor show its real state:
  typing with code on screen (working), hand raised (asked by you), hands
  on head with a red sticky note (blocked), leaning back with a check on
  screen (done in the last 2 hours). When a live update marks work done,
  that agent walks it over to whoever reviews it (Last Touch, Video Last
  Touch, or the boardroom for reviewers), and a speech bubble shows what
  changed. Coffee runs, desk chats, meetings and window breaks are
  ambient scenery; people route around walls and desks on a walkable
  grid built from the scene, and only agents who aren't heads-down take
  breaks. Lighting and the view out the windows follow the viewer's
  local time; a wall clock and a live studio board (earned, waiting on
  you, working now, next shift, latest update) hang on the north wall.
  **Chart Desk** opens a 20-analyst room that reads a chart screenshot
  and calls the next direction and price, a **Live tape** tab (liquidity
  heatmap from level 2, footprint from tick trades, big prints, VWAP,
  POC/value area, initial balance, initial volume bar, protected level),
  and a **Lab** tab with the backtested playbook (see `CHART-DESK.md` and
  `chart-lab/README.md`).
  **Tour** flies the camera through the rooms with the freshest real work;
  **Sound** adds room tone and typing that scales with how many agents are
  working.

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
   Then the **Legal Desk** (10 counsel, `LEGAL-DESK.md`) checks the law on it:
   advertising, anti-spam, privacy, copyright, trademark, financial content,
   platform rules, kids and COPPA, and contracts. It needs a `cleared` verdict.
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

## The Dispatch — the other 20

A third division, physically sitting between the original 40's building
and Edgex Clips' wing (with a real gap on both sides — see
`office/index.html`), keeps the other 90 agents working and hunts new
revenue in its own idle time. Full detail in `DISPATCH.md`; the short
version:

- **4 departments, 20 agents**: Task Dispatch (finds an idle agent,
  assigns the correct next task), Capacity & Queue (maintains a real
  backlog so the match is actually right), Opportunity Discovery
  (always-on opportunity-hunting, the instant Dispatch has nothing to
  dispatch), and Venture Coordination (turns a validated idea into a
  real cross-team build).
- **No new approval gate**: anything a venture produces still clears
  the relevant division's own Last Touch or Video Last Touch, then
  Chief of Staff, then the weekly budget process for any real spend —
  Launch Readiness Agent's whole job is routing to the gate that
  already exists, never a shortcut around it.
- **Chief of Staff still sets priorities and approves/denies**; Task
  Dispatch now handles the moment-to-moment mechanics of who works on
  what next, escalating only genuine judgment calls (see
  `chief-of-staff.md`).
