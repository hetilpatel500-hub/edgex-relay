# Edgex Capital

An AI-agent-run trading research and execution desk for a real Webull
account, built the same way as the studio this pattern is borrowed from:
named agent roles as `.md` files, spawned as parallel clones via the
`Agent` tool when work needs to happen at once, a durable shared memory,
and an hourly Routine that keeps the desk working without anyone needing to
be present.

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

## Current state (set 2026-09-24)

- `live_trading_enabled: false`. **No real order has ever been placed by
  this system, and none will be until the account owner edits
  `TRADING-DESK.md` and flips that flag.**
- The Webull connector for this account (`5JM94223`, Individual Cash) is
  authorized for real trading — it is technically capable of placing real
  orders. The gate file and the Execution Agent's precondition checks are
  the only thing preventing that, which is why they're written as hard
  rules with no exceptions rather than defaults an agent could reason its
  way around.
- Real account snapshot at setup: $1,309.60 net liquidation value, 100%
  cash, 0 open positions.
- Limits: max $200 per trade, max $45 daily loss (halts new trades for the
  rest of the day), max 10 open positions, stocks and options only.

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
flag on and every precondition re-verified in the moment. It never assumes
a submitted order filled — it confirms the real fill from Webull's own
response before logging anything as executed.

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

## The hourly loop

A recurring Routine (`create_trigger`, fresh session per firing) runs
`ROUTINE.md`'s cycle every hour: Risk Monitor refreshes real state ->
Research crew finds/updates ideas -> Portfolio Manager sizes and drafts ->
Head of Trading approves/denies -> Execution Agent (paper-only until the
gate opens) -> Post-Trade Review closes out resolved positions -> Risk
Monitor closes out the cycle. It stays honest at every step about what's
real (an actual Webull balance, position, or fill) versus what's paper —
never blurring the two.
