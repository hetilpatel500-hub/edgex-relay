# Edgex — Operating Rules for the Autonomous Studio

Added 2026-09-24 per the owner's direct instructions. Governs how shifts
pick work, how agents collaborate, and how the studio's small discretionary
budget is decided. Read alongside `BRAND.md` (identity/tone/compliance) and
`DEAL-DESK.md` (the approval gate).

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

## Agents take ideas from each other

A lightweight **`suggestions`** collection lets any agent leave a note for
another: `{to_agent, from_agent, note, status}`. If Competitor Analysis
finds something SEO Agent should reposition around, or Trend Scout spots a
signal that changes what Proposal Writer should price, they log a
suggestion instead of letting it die in their own `result` field. Each
shift, agents with an open suggestion addressed to them get picked first,
and their task incorporates the suggestion — marking it `addressed` when
done.

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
