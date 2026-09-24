# MEMORY.md — Edgex Capital shared memory

The desk's durable shared memory is an `ArtifactData`-backed database attached
to a published dashboard Artifact:

**Dashboard / DB URL: https://claude.ai/artifact/GPxqy83tSRQCxTRB3KbnKt**

Every agent role reads and writes this store with the `ArtifactData` tool
(load its schema via `ToolSearch` with `select:ArtifactData` if it isn't
already loaded), passing `url` = the URL above. The dashboard page itself
renders the same collections live for the human owner — it is not a separate
copy of the truth, it's a window onto it.

Nothing lives only in one agent's own output or context window. If another
role needs a fact, it must be written to one of these collections — an
agent's chat transcript or subagent return value is not memory.

## Collections and document shape

### `config/limits` (single document)
Mirror of `TRADING-DESK.md`, kept in sync by whichever role reads the gate
file each cycle (Head of Trading, at minimum, on every cycle).
```
{
  max_position_size_usd: number,
  max_daily_loss_usd: number,
  max_open_positions: number,
  allowed_instruments: string[],   // e.g. ["stocks", "options"]
  live_trading_enabled: boolean,
  source: "TRADING-DESK.md",
  synced_at: ISO8601 string
}
```
If this document and `TRADING-DESK.md` in the repo ever disagree, the repo
file wins — always re-read `TRADING-DESK.md` before trusting this mirror for
anything consequential (an approval or an execution check).

### `trading_halted/current` (single document)
The only document Portfolio Risk Monitor may set `halted: true` on. Every
other role must check `halted === false` before proposing, approving, or
executing anything new.
```
{
  halted: boolean,
  reason: string | null,
  halted_at: ISO8601 | null,
  cleared_at: ISO8601 | null,
  daily_pnl_usd: number,          // running total for trading_day, paper+live combined but labeled
  trading_day: "YYYY-MM-DD"
}
```

### `positions/latest` (single document)
Real account state, pulled fresh from Webull read-only tools every cycle by
Portfolio Risk Monitor. Never estimated, never blended with paper positions.
```
{
  account_id: string,
  account_number: string,
  account_label: string,
  net_liquidation_value: number,
  cash_balance: number,
  buying_power: number,
  total_unrealized_pl: number,
  total_day_pl: number,
  positions: [
    { symbol, instrument_type, quantity, avg_cost, market_value, unrealized_pl }
  ],
  pulled_at: ISO8601 string,
  source: "webull_live_read"
}
```

### `research/{doc_id}` collection
One document per ticker per calendar day, **merged** (via `update`) by
whichever Research crew member adds a section — not one document per
agent-hour. `doc_id` convention: `<TICKER>__<YYYY-MM-DD>` (e.g.
`NVDA__2026-09-24`). Housekeeping: prune documents older than 14 days each
cycle (see Portfolio Risk Monitor role) to stay well under the artifact's
5,000-document cap.
```
{
  id: string,               // same as doc_id
  ticker: string,
  timestamp: ISO8601,        // last update
  sections: {
    technical?: { summary, data, sources: [{title,url}], confidence, timestamp },
    fundamentals?: { ... same shape ... },
    news_catalyst?: { ... },
    options_flow?: { ... },
    macro_sector?: { ... },
    risk_factor?: { summary, kill_reasons: string[], data, sources, timestamp }
  }
}
```
Every `sources` entry must be a real URL from a real WebSearch/fetch or a
real Webull data call — never invented. If an agent has no real source for a
claim, it either omits the claim or explicitly labels it as its own
inference, never presents it as sourced fact.

### `proposed_trades/{doc_id}` collection
One document per candidate trade, written by the Portfolio Manager crew.
`doc_id` convention: `<TICKER>__<YYYY-MM-DDTHH-MM>`.
```
{
  id: string,
  ticker: string,
  instrument: "stock" | "option",
  option_details: { type: "call"|"put", strike: number, expiry: "YYYY-MM-DD" } | null,
  direction: "long" | "short",
  size_usd: number,           // must be <= config/limits.max_position_size_usd
  entry: number,
  stop: number,
  target: number,
  thesis: string,
  invalidation_point: string, // what would prove this idea wrong
  confidence: "low" | "medium" | "high",
  research_refs: string[],    // research doc_ids this drew on
  correlation_note: string,   // how this relates to current open positions
  risk_factor_response: string, // how the proposal answers Risk Factor Scout's objections
  status: "pending" | "approved" | "denied" | "expired",
  created_at: ISO8601,
  created_by: "portfolio_manager",
  is_paper: true              // always true unless live_trading_enabled flips; Execution Agent may later add executed_* fields, never flips this retroactively for past paper trades
}
```

### `decisions/{doc_id}` collection
One document per Head of Trading verdict, 1:1 with a `proposed_trades`
document. `doc_id` = same id as the proposed trade it decides.
```
{
  id: string,
  proposed_trade_id: string,
  ticker: string,
  verdict: "APPROVE" | "DENY",
  reasoning: string,
  limits_checked: {           // snapshot of the numbers actually compared, for audit
    max_position_size_usd, max_daily_loss_usd, max_open_positions,
    current_open_positions, current_daily_pnl_usd, live_trading_enabled
  },
  resulting_action: "logged_paper" | "denied" | "would_execute_live_blocked_by_gate",
  decided_by: "head_of_trading",
  timestamp: ISO8601
}
```

### `performance_log/{doc_id}` collection
One document per closed position (paper or live), written by Post-Trade
Review Agent. `doc_id` = the originating `proposed_trades` id.
```
{
  id: string,
  trade_id: string,
  ticker: string,
  is_paper: boolean,
  thesis_recap: string,
  what_happened: string,
  pnl_usd: number,
  pnl_pct: number,
  opened_at: ISO8601,
  closed_at: ISO8601,
  lessons: string,            // feeds back to Research crew
  timestamp: ISO8601
}
```

## Housekeeping (document-count discipline)

The store caps out at 5,000 documents total. `research`, `proposed_trades`,
and `decisions` are the only collections that grow unbounded over time.
Each cycle, Portfolio Risk Monitor:
1. Queries `research` for documents with `timestamp` older than 14 days and
   deletes them.
2. Queries `proposed_trades` with `status in ["denied","expired"]` and
   `created_at` older than 30 days, and deletes them (and their matching
   `decisions` doc) — approved/paper-logged trades are kept until
   Post-Trade Review has logged a `performance_log` entry, then may be
   pruned the same way.
This keeps the store well under quota indefinitely without losing anything
the desk still needs.

## Real vs. paper — the one rule that must never blur

Every document that represents a fill, a position, or a balance carries an
explicit `source` or `is_paper` field. `source: "webull_live_read"` means it
came from a real, live Webull read-only call this cycle. `is_paper: true`
means it is a simulated outcome the desk logged for its own honesty and
learning, scored against real market data but never sent to the broker. No
document is ever written that could be misread as a real fill unless it
actually is one (which requires `live_trading_enabled: true` AND a real
Webull order-placement response with a real order id, confirmed by
Execution Agent).
