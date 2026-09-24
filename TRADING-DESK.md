# TRADING-DESK.md — Edgex Capital hard-limit gate

This file is the single source of truth for every risk limit on this desk. Every
agent in the Edgex Capital system — Research crew, Portfolio Manager crew, Head
of Trading, Execution Agent, Portfolio Risk Monitor, Post-Trade Review — reads
this file (or its mirror in the shared memory `config/limits` document) before
acting. No agent may hardcode a limit that duplicates what's here; if a number
is needed, it comes from this file.

**This is a hard-coded permission boundary, not a suggestion.** The same way
"never spend real client money" was a boundary in the other studio, this file
is the boundary here. An agent that is unsure whether an action is allowed
must treat it as not allowed and escalate (log a denial / halt) rather than
proceed.

---

## Account context (real, read-only, refreshed by Portfolio Risk Monitor)

- Broker: Webull
- Account: Individual Cash, account number `5JM94223`
  (`account_id: 83JSBJO42S9IC2SPHDG2J4BBUB`)
- Connector authorization category: **Trading** — the Webull MCP connector
  installed in this environment is technically capable of placing real orders
  (`place_stock_instruction`, `place_option_single_instruction`,
  `place_option_strategy_instruction`, etc.). **The only thing preventing a
  real order is `live_trading_enabled: false` below and the Execution Agent's
  refusal to call any order-placement tool while it is false.** Treat this as
  a live weapon that is currently on safety, not as a toy account.
- Net liquidation value as of 2026-09-24: **$1,309.60** (100% cash, 0 open
  positions). Portfolio Risk Monitor keeps this section's numbers fresh in
  the shared memory `positions` collection — this file's account context is
  a snapshot, never the number to trade against; always read
  `positions/latest` for current real balance and holdings.

---

## Hard limits (set by the account owner on 2026-09-24)

| Field | Value | Meaning |
|---|---|---|
| `max_position_size_usd` | **200** | Max USD notional committed to any single trade (per proposed_trades entry), whether paper or (if ever enabled) live. |
| `max_daily_loss_usd` | **45** | If realized + unrealized P&L for the current trading day drops by this much, Portfolio Risk Monitor sets `trading_halted` and Head of Trading must deny every new trade for the rest of that day. |
| `max_open_positions` | **10** | Max simultaneous open positions (paper or live) at any one time. A new trade that would exceed this is denied regardless of size or conviction. |
| `allowed_instruments` | **stocks, options** | Research, Portfolio Manager, and Execution may only work these two instrument classes. Crypto and futures are out of scope until the owner adds them here explicitly. |
| `live_trading_enabled` | **false** | Hard default. See below. |

### Changing these values

Only the account owner (Hetil) changes this file. If an agent believes a
limit should change, it writes that recommendation to the `decisions`
collection with reasoning — it never edits this file itself, and it never
proceeds as though a proposed change is already in effect.

---

## `live_trading_enabled: false` — what this means operationally

While this flag is `false` (the current and default state):

1. Every agent in the system operates in **analysis/paper mode only**.
2. Research, debate, sizing, and a fully-specified trade recommendation
   (ticker, direction, size, entry, stop, target, thesis, confidence) may be
   logged to `proposed_trades`.
3. Head of Trading may APPROVE or DENY a proposed trade against the limits
   above. An APPROVE while `live_trading_enabled` is false clears the trade
   for **paper logging only** — it is not, and must never be described as,
   an executed trade.
4. **No agent ever calls `mcp__Webull__place_stock_instruction`,
   `place_option_single_instruction`, `place_option_strategy_instruction`,
   `place_crypto_instruction`, `place_futures_instruction`,
   `place_algo_instruction`, `place_event_instruction`, or any other
   real order-placement tool, for any reason, while this flag is false.**
   This includes "just to test," "small size," or "the approval already
   covers it." There are no exceptions.
5. Paper trades are tracked in `proposed_trades` / `performance_log` using
   real market data (real fills are simulated against real quotes) so that
   performance numbers are honest, but they are always labeled `is_paper:
   true` and never presented as real account activity.
6. Read-only Webull tools (`get_account_balance`, `get_account_positions`,
   `get_stock_quotes`, `get_open_orders`, etc.) remain in use every cycle —
   the Portfolio Risk Monitor's job is to know the real account state at all
   times, independent of whether trading is live.

### To turn live trading on

The account owner must, in this file:
1. Fill in final reviewed values for all four limit fields above (confirming
   or changing the current values), and
2. Change `live_trading_enabled` to `true`.

Only then may the Execution Agent call a real order-placement tool — and
even then, only for a trade that Head of Trading already APPROVED against
these exact limits, never retroactively for a trade approved before the
flag flipped.

**Current status: `live_trading_enabled: false`. No real orders. Paper only.**

---

## Enforcement chain

- **Portfolio Manager crew** must not draft a `proposed_trades` entry whose
  `size_usd` exceeds `max_position_size_usd`, whose instrument isn't in
  `allowed_instruments`, or that isn't accompanied by a stated invalidation
  point.
- **Head of Trading** re-checks all of the above independently (never trusts
  Portfolio Manager's math), plus `max_open_positions` and
  `max_daily_loss_usd` / `trading_halted` against the live shared-memory
  state, before writing a `decisions` entry. Head of Trading also DENIES
  anything the Risk Factor Scout flagged that wasn't adequately answered in
  the proposal.
- **Portfolio Risk Monitor** runs every cycle regardless of what else
  happened, reads real Webull balance/positions, and is the only role that
  may set `trading_halted: true`. It can stop trading; it can never start it
  or clear its own halt without the halt condition genuinely no longer
  applying (e.g., a new trading day has started).
- **Execution Agent** is the only role ever allowed to touch a real
  order-placement tool, and refuses to do so whenever
  `live_trading_enabled` is false, a trade wasn't APPROVED, the halt flag is
  set, or the trade doesn't fit inside every limit above at the moment of
  execution (limits can tighten between approval and execution if real
  positions changed) — no exceptions, no "just this once."
