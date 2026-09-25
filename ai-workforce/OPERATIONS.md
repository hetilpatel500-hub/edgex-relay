# Edgex — Operating Rules for the Autonomous Studio

Added 2026-09-24 per the owner's direct instructions. Governs how shifts
pick work, how agents collaborate, and how the studio's small discretionary
budget is decided. Read alongside `BRAND.md` (identity/tone/compliance) and
`DEAL-DESK.md` (the approval gate).

**Also as of 2026-09-24: this budget process is the *only* place the owner
still approves anything.** Every other client-facing decision now goes
through Chief of Staff instead — see `DEAL-DESK.md`. Nothing below changes
because of that; if anything it matters more now, since it's the one real
checkpoint left.

## Revenue priority over video content

Added 2026-09-24 per the owner's direct instruction ("make sure we are
making money, thats the goal, dont only focus on instagram"). The studio's
goal is real money, not content/audience growth for its own sake. Every
shift prioritizes work that advances actual revenue over Edgex Clips
video/social content specifically:

1. Advance every real deal already in motion toward signed/paid — a reply
   to follow up on, a deal card to finalize, an outreach cycle to run.
2. Actively source new leads and draft real deal cards across **all**
   validated opportunities, not just one niche.
3. Video content production (scripts/clips/voiceover/compose) does not
   consume a disproportionate share of a shift's real effort or vidIQ
   credit budget relative to what it can actually monetize right now —
   Instagram/YouTube have no real monetization eligibility yet, so treat
   video work as secondary to client-services revenue work, not equal
   priority, until the channel actually qualifies for real payouts.

This doesn't mean stop Edgex Clips entirely — keep it moving at a
sustainable pace — it means client-services revenue work comes first when
both are competing for the same shift's attention.

## Zero idle

No agent should sit at status="idle" for an extended stretch when there is
real work available — and with 40 agents and a growing opportunity list,
there almost always is. The autonomous shift runs **hourly** (not every 5
hours) specifically to keep rotation tight: a full pass through all 40
agents should take roughly 10 hours, not a full day.

"Idle" is not a failure state for an agent that's genuinely waiting on a
real external input (Client/Lead Researcher blocked on a target city was a
legitimate `blocked`, not `idle`). It *is* a problem when an agent sits
untouched simply because nobody re-assigned it.

## Shift mechanics — added 2026-09-25

Two rules every shift follows, because both broke silently before:

**Use the real clock.** Before writing any `updatedAt`, `timestamp`, or
`created` field, get the actual time with `date -u +%FT%TZ` in the shell
and use that. Never estimate or invent a time. Shifts were stamping
records with times hours in the future, which breaks "oldest first"
rotation and makes the office dashboard lie about what happened when.

**Hourly shifts cannot push to git — don't try.** The shift sessions
don't have this repo in their authorized sources, so every `git push`
fails (403), and any file edit made in a shift is lost when its container
ends. Past shifts wrote real content (compliance rules, pricing sign-offs)
that never reached the repo. Instead, when a shift needs a repo file
changed, it writes one doc per change to the `repo_changes` collection:

```
{ file: "ai-workforce/BRAND.md",
  op: "replace" | "append" | "create",
  old_str: "<exact existing text, for replace>",
  new_str: "<new text>",
  reason: "<one line>",
  decision_ref: "<decisions doc id, if any>",
  status: "pending",
  created: <real time> }
```

The daily check-in (it runs in the owner's connected session, which can
push) applies every `pending` change, commits, pushes, and marks each doc
`applied` (with the commit hash) or `rejected` (with why). Until a change
shows `applied`, treat the `decisions` doc as the operative record and
never describe the file as already updated.

## Opportunities never get lost

A dedicated **`opportunities`** collection (separate from any one agent's
`result` field) tracks every money-making idea the studio has ever found,
so an idea can't quietly vanish just because the agent who found it moved
on to something else. Each has a status:

- `scouting` — being actively investigated
- `validating` — has real signal, being sized/priced
- `active` — has a live client motion (leads, outreach, or a deal)
- `stalled` — identified but nobody's picked it up recently
- `archived` — explicitly ruled out, with why

Every shift, **at least one Research & Intelligence agent works on finding
or reviving an opportunity** — not just supporting the one already in
flight. If an idea sits at `stalled` for more than a couple of shifts, the
next shift assigns someone to either revive it or archive it with a real
reason. Nothing is allowed to just quietly die from neglect.

**Updated 2026-09-24 — this rule wasn't enough on its own.** The studio
ran its entire real pipeline on one single opportunity (missed-inquiry
automation for plumbers) for its whole existence, because "at least one
agent works on finding an opportunity" was satisfied by re-servicing the
same niche instead of genuinely diversifying. The stronger rule:
**the studio should have multiple distinct opportunities at `active` or
`validating` status at once, not one.** If the `opportunities` collection
has fewer than 3 non-archived entries, or the same single opportunity
has absorbed every outreach cycle for more than a few shifts running,
that's the top-priority gap for the next shift — Standing Opportunity
Scout (`DISPATCH.md`) and Opportunity Scout both exist specifically so
this doesn't happen, and a `scouting`-status opportunity that's sat
untouched with a clear documented next step (like a pricing tier needing
real research) is exactly what Venture Lead Agent should be picking up,
not leaving parked.

**Added 2026-09-25 — the idea pool.** `MONEY-MAP.md` lists 100 ways the
studio can make money with AI, each tracked in the `money_map` collection
(`status`: `unreviewed` → `promoted` / `hold` / `archived`, or `tracked`
if it already maps to an `opportunities` doc). Every shift, Opportunity
Discovery reviews ~10 `unreviewed` items with real research and writes
the result back to that item's doc — promote into `opportunities` at
`validating`, hold naming the specific `[SETUP]` blocker, or archive with
a reason. Keep 6–8 opportunities `active` at once, ranked by fastest real
path to a first dollar with tools that exist today; when one closes,
stalls, or archives, the next promoted item takes its slot. Never try to
work all 100 at once.

## Agents take ideas from each other

A lightweight **`suggestions`** collection lets any agent leave a note for
another: `{to_agent, from_agent, note, status}`. If Competitor Analysis
finds something SEO Agent should reposition around, or Trend Scout spots a
signal that changes what Proposal Writer should price, they log a
suggestion instead of letting it die in their own `result` field. Each
shift, agents with an open suggestion addressed to them get picked first,
and their task incorporates the suggestion — marking it `addressed` when
done.

## Chief of Staff's daily decision digest

Every client-facing decision Chief of Staff makes — approved or denied —
is logged to a **`decisions`** collection: `{agent, action, decision,
reason, revenue_case, timestamp}`. `decision` is `"approved"` or
`"denied"`; `revenue_case` is required on an approval (which deal or
opportunity this advances, and how) and optional on a denial.

A **separate daily Routine** ("Edgex daily decision digest",
`trig_01FmybD21HpqpiY3ymP1qK8Q`) wakes the owner's live chat session once
a day (Routines here can't hold a Gmail connector, only a connected chat
session can — see `DEAL-DESK.md`'s mechanical-limit note). It reads every
`decisions` entry from the last 24 hours, sends **one email** to
`hetilpatel500@gmail.com` covering what was decided, why, and the revenue
case for each approval, and also flushes anything Chief of Staff already
approved into `outbox` — those get actually sent for real at this point,
not before. This is a report, not a request; the owner doesn't need to
act on it for the studio to keep moving, but it's everything they'd need
to step back into any specific decision if they want to.

## The weekly budget meeting

A **separate weekly Routine** ("Edgex weekly budget meeting") runs once a
week. What it actually does:

1. Adds $20 to the studio's tracked balance (`budget/account` — a ledger,
   not a real bank balance; see below).
2. Chief of Staff reviews what every department flagged as actually
   needing money that week (a tool, a Twilio number, a small ad test,
   anything with a real cost) and what the current balance can cover.
3. Produces **one** consolidated recommendation — spend on X because Y, or
   save this week toward something bigger — logged to `budget_proposals`.
4. If it recommends spending, that's a **request for the owner's approval**,
   exactly like a deal card. Nothing is purchased automatically.

**The honest mechanical limit:** no agent, including Chief of Staff, has a
card, a checkout tool, or any way to actually move money. This ledger
tracks what's been authorized and what the team would do with it — an
actual purchase (registering a domain, buying a Twilio number, subscribing
to a tool) still means the owner does it themselves, or explicitly hands
over a payment method for a specific approved purchase. If real autonomous
spending is wanted later, that's a separate, bigger integration (a
virtual-card connector) — not something to wire in quietly alongside this.
