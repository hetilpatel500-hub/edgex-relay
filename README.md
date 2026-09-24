# Edgex Capital

An AI-agent-run trading research and execution desk for a real Webull
account, built the same way as the studio this pattern is borrowed from:
named agent roles as `.md` files, spawned as parallel clones via the
`Agent` tool when work needs to happen at once, a durable shared memory,
and a Routine that keeps the desk working without anyone needing to be
present.

## Start here

- **`TRADING-DESK.md`** — the hard-limit gate. Every trade this system
  will ever propose is checked against this file. Read it first; it is the
  actual safety boundary, not decoration.
- **`MEMORY.md`** — the shared-memory schema and the dashboard/database
  URL. Everything any agent learns or decides is written here — nothing
  lives only in one agent's own output.
- **`ROUTINE.md`** — the exact hourly cycle: what runs, in what order, and
  what each step is allowed to do.
- **`agents/`** — one `.md` file per role. Each is a complete, standalone
  brief: mandate, inputs, process, exact output schema, and boundaries.

## Current state (updated 2026-09-24)

- **`live_trading_enabled: true`**, set by the account owner directly in
  `TRADING-DESK.md` after explicit chat confirmation. Execution Agent can
  now create real order instructions on this real Webull account for
  trades Head of Trading has APPROVED and that independently re-check
  clean against every limit at the moment of execution.
- **Important: this is not fully autonomous execution.** Every Webull
  order-placement tool (stocks, options, crypto, futures — all of them)
  creates a *pending instruction*, never a real order directly. Nothing
  trades until the account owner personally confirms it in the Webull App
  or Desktop. This system's job is to get a well-reasoned, limit-checked
  confirmation prompt in front of the owner; only the owner's own tap ever
  makes it real. See `TRADING-DESK.md` for the full detail and how to turn
  live trading back off (owner-only, any time).
- **Instrument scope: options only** (changed 2026-09-24; stocks are no
  longer proposed). Options trade in 100-share lots, so the $200
  per-trade cap effectively limits single-leg positions to contracts
  priced under ~$2.00, or a defined-risk spread sized to that net debit —
  see `TRADING-DESK.md`'s sizing-constraint note.
- **Max 2 new trade approvals per calendar day** (`max_trades_per_day`,
  added 2026-09-24) — separate from the 10-position concurrent cap.
- The Webull connector for this account (`5JM94223`, Individual Cash) is
  authorized for real trading. Every safety check — Head of Trading's
  independent limit re-derivation, Risk Factor Scout's objections,
  Portfolio Risk Monitor's halt authority, Execution Agent's fresh
  precondition re-check — still applies in full, on top of the owner's own
  manual confirmation step.
- Real account snapshot at setup: $1,309.60 net liquidation value, 100%
  cash, 0 open positions.
- Limits: max $200 per trade, max $45 daily loss (halts new trades for the
  rest of the day), max 10 open positions, max 2 new trades/day, options
  only.
- Cadence: every 5 minutes during US market hours (weekdays, ~14:00–21:00
  UTC), instead of hourly — see `ROUTINE.md`. Research is deduped per
  ticker (skipped if covered within the last 4 hours), so the dense
  cadence mainly buys faster Risk Monitor checks, faster proposal/approval
  turnaround, and faster instruction reconciliation, not six-agent
  research spinning up every 5 minutes.

## The org

**Research & Intelligence crew** (six independent lenses, spawned in
parallel every cycle): Technical Analyst, Fundamentals/Earnings Analyst,
News & Catalyst Scout, Options Flow / Sentiment, Macro/Sector Analyst, Risk
Factor Scout. Every finding is written to the shared `research` collection
with real sourcing — no invented data, no fabricated backtests, no claiming
statistical significance without showing the basis.

**Portfolio Manager crew** synthesizes Research's findings into sized,
correlation-checked, fully-specified trade proposals with an explicit
invalidation point — and refuses to draft anything Risk Factor Scout
flagged and wasn't adequately answered.

**Head of Trading** is the finalizer: re-derives every limit check
independently against `TRADING-DESK.md` and either APPROVES (paper-logged,
fully reasoned) or DENIES. An approval only ever clears a trade for paper
logging unless `live_trading_enabled` is `true` and the trade fits inside
every hard limit — no exceptions.

**Execution Agent** is the only role ever allowed to touch a real Webull
order-placement tool, and only for an already-approved trade with the live
flag on and every precondition re-verified in the moment. Calling that
tool creates a pending instruction, not a real order — Execution Agent
surfaces the confirmation link to the owner immediately, then reconciles
the outcome each cycle (approved+filled, rejected, or expired) once the
owner has acted in the Webull app. It never assumes a submitted order
filled — it confirms the real fill from Webull's own order data.

**Portfolio Risk Monitor** runs every cycle regardless of anything else:
pulls real balance/positions, flags anything approaching the daily-loss or
open-position limits, and is the only role that can set a halt. It can stop
trading; it can never start it.

**Post-Trade Review** logs real, honest P&L on every closed position
(paper or live) and retros what the thesis got right or wrong, feeding
lessons back to Research.

## Memory

An `ArtifactData`-backed shared database (see `MEMORY.md` for the URL and
full schema): `research`, `proposed_trades`, `decisions`, `positions`,
`trading_halted`, `performance_log`, `config`. The same URL is a live
dashboard for the account owner — gate status, real account state,
proposed trades, decisions, research feed, and performance, all rendered
from the same documents the agents read and write.

## The loop

A recurring Routine (`create_trigger`, fresh session per firing) runs
`ROUTINE.md`'s cycle every 5 minutes during market hours: Risk Monitor
refreshes real state -> Research crew finds/updates ideas -> Portfolio
Manager sizes and drafts (options only) -> Head of Trading approves/denies
(max 2/day) -> Execution Agent creates a real confirmation instruction for
any approval and reconciles previously-created ones -> Post-Trade Review
closes out resolved positions -> Risk Monitor closes out the cycle. It
stays honest at every step about what's real (an actual Webull balance,
position, confirmed fill) versus what's paper, and about the difference
between "an instruction was created" and "the owner confirmed it and it
actually traded" — never blurring any of it.
