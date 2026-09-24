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
  `place_option_strategy_instruction`, etc.). **As of 2026-09-24,
  `live_trading_enabled` below is `true` — real orders can be placed by the
  Execution Agent for trades Head of Trading has APPROVED and that fit
  inside every limit at the moment of execution.** This is a live account
  with live money. Every safety check below still applies in full; going
  live removed nothing, it only allowed the final step to actually fire.
- Net liquidation value as of 2026-09-24: **$1,309.60** (100% cash, 0 open
  positions). Portfolio Risk Monitor keeps this section's numbers fresh in
  the shared memory `positions` collection — this file's account context is
  a snapshot, never the number to trade against; always read
  `positions/latest` for current real balance and holdings.

---

## Hard limits (set by the account owner on 2026-09-24, instrument scope and trade-count cap updated same day)

| Field | Value | Meaning |
|---|---|---|
| `max_position_size_usd` | **200** | Max USD notional committed to any single trade (per proposed_trades entry), whether paper or live. For options this is the max net premium/debit for the whole position (contract price × 100 × contracts, or net debit for a spread) — see "Options-only sizing constraint" below. |
| `max_daily_loss_usd` | **45** | If realized + unrealized P&L for the current trading day drops by this much, Portfolio Risk Monitor sets `trading_halted` and Head of Trading must deny every new trade for the rest of that day. |
| `max_open_positions` | **10** | Max simultaneous open positions (paper or live) at any one time. A new trade that would exceed this is denied regardless of size or conviction. |
| `max_trades_per_day` | **2** | Max new trade *approvals* per calendar trading day (paper or live) — a rate limit, separate from `max_open_positions`. The 3rd otherwise-qualifying proposal on a given day is DENIED for this reason alone, however good it looks. |
| `allowed_instruments` | **options** | Options only. Stocks, crypto, and futures are out of scope — Portfolio Manager drafts nothing else, and Head of Trading DENIES any proposal with `instrument != "option"` on sight. |
| `live_trading_enabled` | **true** | Set by the account owner on 2026-09-24, via explicit chat confirmation after being told plainly this is the real-money step. See below. |

### Options-only sizing constraint (practical, not a loophole)

Options trade in 100-share contract lots, so `max_position_size_usd: 200`
means a single-leg long option position is only affordable at or below
**~$2.00/contract premium** (1 contract × 100 × $2.00 = $200). This
materially narrows the strategy space versus stocks: expect the desk to
gravitate toward further-OTM strikes, shorter-dated contracts, or
defined-risk spreads (where `size_usd` is the net debit, which can fit
$200 at a wider range of strikes than a single long call/put). Portfolio
Manager must size to the *real* quoted premium from Webull, not round down
or approximate — if nothing in the real chain fits under the cap with a
thesis that still makes sense, the correct output is no trade, not a
distorted one to force a fit.

### Changing these values

Only the account owner (Hetil) changes this file. If an agent believes a
limit should change, it writes that recommendation to the `decisions`
collection with reasoning — it never edits this file itself, and it never
proceeds as though a proposed change is already in effect. This includes
`live_trading_enabled` itself: no agent ever flips this flag in either
direction; only the account owner does, directly in this file.

---

## `live_trading_enabled` — what each state means operationally

**While `false` (the default, and this desk's state from its creation on
2026-09-24 until the owner flipped it later the same day):**
1. Every agent operates in **analysis/paper mode only**.
2. Head of Trading's APPROVE clears a trade for **paper logging only**.
3. No agent ever calls a real order-placement tool, for any reason.
4. Paper trades are still scored against real market data, always labeled
   `is_paper: true`, never presented as real account activity.

**While `true` (current state, set 2026-09-24):**
1. Everything above still happens exactly the same way — full six-lens
   Research, Portfolio Manager sizing, Head of Trading's independent limit
   checks — right up through a decision.
2. **Important correction to how this actually works, discovered
   2026-09-24 after going live:** the Webull connector's order-placement
   tools (`place_stock_instruction`, `place_option_single_instruction`,
   `place_option_strategy_instruction`, etc.) do not place real orders
   directly, for any instrument, ever. Each one creates a **pending
   instruction** that only becomes a real order once **you personally
   confirm it in the Webull App or Desktop.** This is a property of the
   connector itself, independent of anything in this repo — it is a real,
   unbypassable human-in-the-loop step on top of everything else in this
   file. Head of Trading's APPROVE and Execution Agent's precondition
   checks control whether an *instruction gets created and put in front of
   you*; they cannot and do not control whether it becomes a real order —
   only your own tap in the app does that.
3. **No agent ever calls a real order-placement tool** unless: this flag
   reads `true` at the moment of the call (re-read fresh, not cached),
   `trading_halted/current.halted` is `false`, the specific trade has a
   `decisions` doc with `verdict == "APPROVE"` and
   `resulting_action == "cleared_for_execution"`, and the trade still fits
   every limit against freshly re-pulled real account state. Any one of
   those failing means no instruction is even created, no exceptions.
4. When an instruction is created, Execution Agent surfaces the tool's
   confirmation `message` (which contains the real confirmation link) to
   you immediately — every time, no exceptions — and never describes
   instruction creation itself as "executed." It later reconciles the
   outcome (`get_processed_instruction`: `APPROVED`/`REJECTED`/`EXPIRED`)
   and, only for an `APPROVED` instruction, confirms the real fill (price,
   quantity, order id) from Webull's own order data before logging
   anything as an actual executed trade.
5. Read-only Webull tools remain in use every cycle regardless of this
   flag — Portfolio Risk Monitor's job doesn't change.

### To turn live trading back off

The account owner changes `live_trading_enabled` back to `false` in this
file at any time. That immediately stops all *new* real orders (checked
fresh on every Execution Agent call) — it does not, by itself, close any
position already open; closing a real position is a decision like any
other, routed through the normal approve/execute flow (or done manually by
the owner directly in Webull).

### To turn live trading on (for reference — already done 2026-09-24)

The account owner filled in final reviewed values for all four limit
fields above and changed `live_trading_enabled` to `true` directly in this
file, after explicit confirmation in chat that this authorizes real order
placement on a real account. That is the only path that has ever turned
this on, and the only path that ever will.

**Current status: `live_trading_enabled: true`. Execution Agent CAN create
real order instructions for APPROVED trades that fit every limit at the
moment of execution — but every one of those instructions still requires
YOUR manual confirmation in the Webull App or Desktop before it becomes a
real order. Nothing trades without you personally tapping confirm. This is
not a drill, but it is also not fully autonomous execution — treat every
confirmation prompt this system sends you as a real decision point.**

---

## Enforcement chain

- **Portfolio Manager crew** must not draft a `proposed_trades` entry whose
  `size_usd` exceeds `max_position_size_usd`, whose instrument isn't in
  `allowed_instruments` (options only), or that isn't accompanied by a
  stated invalidation point. As a courtesy check (not the authoritative
  one), it should also query today's `decisions` for existing `APPROVE`
  verdicts and skip drafting a 3rd proposal for the day — but Head of
  Trading enforces this for real regardless.
- **Head of Trading** re-checks all of the above independently (never trusts
  Portfolio Manager's math), plus `max_open_positions`, `max_trades_per_day`
  (count today's `decisions` with `verdict == "APPROVE"` — the 3rd approval
  in one day is a DENY on that basis alone), and `max_daily_loss_usd` /
  `trading_halted` against the live shared-memory state, before writing a
  `decisions` entry. Head of Trading also DENIES anything the Risk Factor
  Scout flagged that wasn't adequately answered in the proposal, and DENIES
  on sight any proposal whose `instrument` isn't `"option"`.
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
  positions changed) — no exceptions, no "just this once." Even when it
  does call the tool, that only creates a pending instruction — the owner's
  own manual confirmation in the Webull App/Desktop is the real last step,
  and no agent anywhere in this system can perform it or substitute for it.
