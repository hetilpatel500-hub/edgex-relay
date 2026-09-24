# ROUTINE.md — the hourly Edgex Capital desk cycle

This is the standalone instruction the hourly Routine (a scheduled trigger,
`create_trigger` in Claude Code Remote) sends into a **fresh session** every
hour. Because the session has no memory of any prior cycle, this document —
plus `TRADING-DESK.md`, `MEMORY.md`, and the role files in `agents/` — must
be everything a cold-start session needs to run one complete, correct cycle.

Repo: `hetilpatel500-hub/edgex-relay`, branch `claude/practical-einstein-wl1pbm`.
Shared memory / dashboard: see `MEMORY.md` for the current URL.

## The literal trigger prompt

The Routine's stored prompt is:

> Run one Edgex Capital trading-desk cycle now. Read ROUTINE.md,
> TRADING-DESK.md, MEMORY.md, and the role files in agents/ from the
> edgex-relay repo (branch claude/practical-einstein-wl1pbm) and follow
> ROUTINE.md exactly. Report back only if something needs the account
> owner's attention (a halt, a denial worth flagging, an error) — otherwise
> a quiet, successful cycle needs no reply.

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

### 5. Head of Trading
Spawn one `Agent` call using `head-of-trading.md` as the brief. It
processes every `proposed_trades` doc with `status == "pending"`, writes a
`decisions` entry for each, and updates each proposal's `status`. Then, for
any `status == "approved"` decision, spawn one `Agent` call using
`execution-agent.md` as the brief — it will independently re-check every
precondition and, since `live_trading_enabled` is currently `false`, will
correctly do nothing beyond logging why it didn't execute. This is not
wasted work: it's the same code path that will run once live trading is
ever turned on, and it needs to be exercised every cycle so it's trustworthy
when it matters.

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
  ticker per role; that fans out too fast for an hourly cadence.
- If `trading_halted/current.halted` is already `true` at step 1, Research
  may still run (keeps the desk's analysis current for when the halt
  clears), but treat it as lower urgency — it's fine to skip straight to
  step 6/7 on a halted cycle if you want to conserve effort, since no new
  proposal can be approved while halted anyway.

## The one thing every step must never do

No agent spawned in any step of this cycle calls a real Webull
order-placement tool unless it is the Execution Agent, `TRADING-DESK.md`'s
`live_trading_enabled` reads exactly `true`, and every precondition in
`agents/execution-agent.md` is independently re-verified in that moment.
Today, and until the account owner explicitly changes the gate file, that
condition is never met — every cycle is paper-only, honestly labeled as
such everywhere it's logged.
