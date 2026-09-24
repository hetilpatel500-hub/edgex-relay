# ROUTINE.md — the Edgex Capital desk cycle

This is the standalone instruction the Routine (a scheduled trigger,
`create_trigger` in Claude Code Remote) sends into a **fresh session** on
every firing. Because the session has no memory of any prior cycle, this
document — plus `TRADING-DESK.md`, `MEMORY.md`, and the role files in
`agents/` — must be everything a cold-start session needs to run one
complete, correct cycle.

**Cadence (updated 2026-09-24): every 5 minutes during US market hours
(weekdays, cron `*/5 14-20 * * 1-5`, UTC), not hourly.** The dedup rule in
step 2 keeps this cheap — Research crew mostly no-ops between its own
4-hour-old checks, so the dense cadence buys faster Risk Monitor checks,
faster approve/deny turnaround, and faster real-fill confirmation, not six
agents re-researching every 5 minutes. Outside market hours the Routine
doesn't fire at all — no autonomous action happens while markets are
closed.

Repo: `hetilpatel500-hub/edgex-relay`, branch `claude/practical-einstein-wl1pbm`.
Shared memory / dashboard: see `MEMORY.md` for the current URL.

## The literal trigger prompt

The Routine's stored prompt is:

> Run one Edgex Capital trading-desk cycle now. Read ROUTINE.md,
> TRADING-DESK.md, MEMORY.md, and the role files in agents/ from the
> edgex-relay repo (branch claude/practical-einstein-wl1pbm, or its default
> branch if that branch has since merged) and follow ROUTINE.md exactly.
> If mcp__Webull__* tools are not available in this session, say so
> clearly rather than silently skipping real-data steps. Never call a real
> Webull order-placement tool unless live_trading_enabled reads true in
> TRADING-DESK.md AND every precondition in agents/execution-agent.md is
> independently verified in the moment — and remember that tool only
> creates a pending instruction requiring the owner's manual confirmation
> in the Webull app, never a real order by itself. If Execution Agent
> creates a new instruction this cycle, ALWAYS report back immediately
> with the confirmation message/link verbatim. If a previously-pending
> instruction's status changed (approved+filled, rejected, or expired),
> ALWAYS report that too. Otherwise, stay quiet on an uneventful cycle;
> only report back if trading_halted just became true, a denial is worth
> flagging to the owner, a step errored, or the Webull connector was
> unavailable.

## Cycle steps, in order

### 0. Orient
Read `TRADING-DESK.md` (the authoritative gate — never trust a cached
value), `MEMORY.md` (schema + shared-memory URL), and skim `agents/*.md`.
Confirm `ArtifactData` is loaded (`ToolSearch`, `select:ArtifactData` if
needed) and the Webull MCP tools are available (`ToolSearch`,
`select:mcp__Webull__...` for whichever you need this cycle).

### 1. Portfolio Risk Monitor — first pass (always runs)
Spawn one `Agent` call using the `agents/portfolio-risk-monitor.md`
instructions as its brief (paste the file's content into the prompt along
with the shared-memory URL and the account_id from `TRADING-DESK.md`). It
refreshes `positions/latest` from real Webull data and updates
`trading_halted/current`. **This step runs even if every later step will be
skipped.** Read its result: note whether `halted` is now `true`.

### 2. Build this cycle's ticker candidate list (cap: 5 tickers)
Before spawning Research, assemble candidates yourself (no agent needed for
this bookkeeping step):
1. Every symbol in the account owner's Webull watchlists
   (`get_watchlists` then `get_watchlist_instruments` per list).
2. Any symbol with a real open position (`positions/latest.positions`) —
   keep researching names actually held.
3. Top 2 gainers and top 2 losers today (`get_gainers_losers`,
   `category: "US_STOCK"`, `rank_type: "DAY_1"`) to catch real, current
   opportunities the owner isn't already watching.
Dedupe against existing research: for each candidate, `get` the
`research/<TICKER>__<today>` doc — if it already has all six sections and
was last updated under 4 hours ago, drop it from this cycle's list (no need
to re-research something just covered). Cap the final list at 5 tickers,
prioritizing held positions and watchlist names over gainers/losers when
trimming.

If the candidate list is empty after dedup, skip straight to step 6
(Post-Trade Review) and step 7 (Risk Monitor closeout) — there's nothing
new to research this cycle, which is a normal, healthy outcome, not a
failure.

### 3. Research crew — six parallel agents
Spawn six `Agent` calls **in the same message** (true parallelism), one per
role file: `technical-analyst.md`, `fundamentals-analyst.md`,
`news-catalyst-scout.md`, `options-flow-sentiment.md`,
`macro-sector-analyst.md`, `risk-factor-scout.md`. Each agent's prompt
must include: the full text of its role file, the shared-memory URL, the
`ArtifactData` write pattern from `MEMORY.md`, and this cycle's ticker
candidate list. Each agent researches every ticker in the list within its
own lens and writes its section to each ticker's `research` document —
they work independently and must not simply restate what another lens
would find. Risk Factor Scout should be told explicitly to read the other
five sections is not required (it can run concurrently) but must actively
hunt for real counter-evidence per its own file, not just note the absence
of other findings.

Wait for all six to complete before moving on — Portfolio Manager needs
complete research.

### 4. Portfolio Manager crew
Spawn one `Agent` call (or two in parallel if the ticker list is large
enough to split sensibly — otherwise one is enough) using
`portfolio-manager.md` as the brief, with the shared-memory URL and this
cycle's ticker list. It reads the fresh research, decides which (if any)
tickers warrant a proposal, and writes `proposed_trades` entries. Most
cycles will produce zero or one proposal — that's expected; don't treat an
empty result as an error.

### 5. Head of Trading, then Execution Agent (always runs, every cycle)
Spawn one `Agent` call using `head-of-trading.md` as the brief. It
processes every `proposed_trades` doc with `status == "pending"`, writes a
`decisions` entry for each (including the `max_trades_per_day` check), and
updates each proposal's `status`.

Then spawn one `Agent` call using `execution-agent.md` as the brief,
**every cycle, regardless of whether there's a new approval** — it has two
jobs: (a) for any `status == "approved"`, `resulting_action ==
"cleared_for_execution"` decision from this cycle, independently re-check
every precondition and, if they hold, create the instruction; (b)
reconcile any previously-created instructions still sitting
`pending_user_confirmation` or `approved_pending_fill` against
`get_processed_instruction`/order data.

**`live_trading_enabled` is currently `true`.** Creating an instruction is
not executing a trade — it puts a real confirmation prompt in front of the
owner in the Webull app, and nothing trades until they act on it
themselves. The reporting rule in step 8 means the owner is always told
immediately both when a new instruction is created and when a pending
one's status changes. If any precondition fails before instruction
creation (halt is set, real positions moved since approval, the flag
somehow reads false on re-check), Execution Agent logs why and stops — no
exceptions either direction.

### 6. Post-Trade Review
Spawn one `Agent` call using `post-trade-review.md` as the brief. It checks
every open (`approved`, not yet `closed`) proposed trade — including ones
from previous cycles, so it must query `proposed_trades` for
`status == "approved"` broadly, not just this cycle's — against real
current quotes for a stop/target/invalidation hit, and logs
`performance_log` entries for anything that resolved.

### 7. Portfolio Risk Monitor — closeout pass (always runs)
Spawn `portfolio-risk-monitor.md` again for a final refresh: real balance/
positions may have moved during the cycle (market prices change even
though this desk isn't placing real orders yet), and this pass also does
the housekeeping prune described in `MEMORY.md`.

### 8. Report only if it matters
Per the trigger prompt: stay quiet on an uneventful cycle (the dashboard is
the record). Do report back (a message to the account owner) when:
- **A new instruction was created — always, every time, no exceptions.**
  Include the confirmation `message`/link verbatim, the ticker, and the
  proposal's thesis in one line — the owner needs to know a real
  confirmation prompt is now sitting in their Webull app.
- **A previously-pending instruction's status changed** —
  `approved_and_filled` (include real order id, fill price, quantity),
  `rejected`, or `expired` — always, every time.
- `trading_halted/current.halted` just became `true`.
- Head of Trading denied a proposal for a reason the owner should probably
  know about even though the system worked correctly (e.g. a genuinely
  promising idea was denied only because it would have exceeded
  `max_open_positions` — that's useful signal, not noise).
- Any step errored in a way that means the cycle didn't complete as
  designed (a tool failure, an unreachable data source) — say what broke
  and what still ran.

## Cost/scope discipline

- Cap candidate tickers at 5 per cycle. This bounds Research crew's search
  volume and keeps the shared-memory document count growing slowly (see
  `MEMORY.md` housekeeping).
- Six Research agents run once per cycle regardless of ticker count (each
  covers the whole candidate list itself) — never spawn one agent per
  ticker per role; that fans out too fast at a 5-minute cadence.
- If `trading_halted/current.halted` is already `true` at step 1, Research
  may still run (keeps the desk's analysis current for when the halt
  clears), but treat it as lower urgency — it's fine to skip straight to
  step 6/7 on a halted cycle if you want to conserve effort, since no new
  proposal can be approved while halted anyway.

## The one thing every step must never do

No agent spawned in any step of this cycle calls a real Webull
order-placement tool unless it is the Execution Agent, `TRADING-DESK.md`'s
`live_trading_enabled` reads exactly `true` (re-read fresh, that moment —
never cached from earlier in the cycle or from a prior cycle), and every
precondition in `agents/execution-agent.md` is independently re-verified
in that moment. Even then, that call only creates a pending instruction —
**no agent, and no amount of approval logic in this system, can make a
trade real. Only the owner's own manual confirmation in the Webull App or
Desktop can.** Every trade that isn't cleared this way stays paper,
honestly labeled `is_paper: true` everywhere it's logged. Every instruction
that is created, and every change in a pending instruction's status, is
reported to the owner immediately per step 8, never left for them to
discover on the dashboard or in the Webull app with no warning.
