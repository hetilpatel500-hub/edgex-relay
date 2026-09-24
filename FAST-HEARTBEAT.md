# FAST-HEARTBEAT.md — session-local fast monitoring loop

This is a **second, separate** automation from `ROUTINE.md`'s hourly desk
cycle. It exists because the account owner asked for faster-than-hourly
reaction during market hours, and the durable hourly Routine (`create_trigger`)
has a hard platform floor of 1 hour — confirmed by an actual rejected API
call, not a guess. This heartbeat is the real alternative: a session-local
cron job (`CronCreate`), the fastest mechanism actually available, running
**once per minute** (cron has no finer granularity than a minute — "every
30 seconds" isn't expressible at all, in this or any standard cron).

## Hard limitations — read before assuming this is equivalent to ROUTINE.md

1. **Session-only.** This job lives only inside the specific Claude Code
   session that created it. Nothing is written to disk for it, and it is
   gone the moment that session ends (container reclaim, the owner closing
   the session, etc.) — unlike `ROUTINE.md`'s Routine, which is durable and
   fires into a fresh session regardless of whether any chat is open.
2. **Auto-expires after 7 days** even if the session somehow stays alive
   that long (a platform limit on `CronCreate`, not a choice here).
3. **Not a substitute for the hourly cycle.** This heartbeat does *not* run
   Research, Portfolio Manager, or Head of Trading — it does one narrow,
   cheap job (below) so it can actually sustain a 1-minute cadence without
   either falling behind or burning the account's tool-call budget on
   redundant six-agent research every 60 seconds.
4. **Cannot make a real trade happen any faster.** Every Webull
   order-placement tool creates a pending instruction requiring the
   owner's manual confirmation in the app (see `TRADING-DESK.md`). This
   heartbeat's only edge is *detecting and alerting* fast — it has no
   more power to execute than anything else in this system.

## Schedule
`* 14-20 * * 1-5` (every minute, ~market hours, weekdays, UTC) — scoped to
market hours in the cron expression itself so it doesn't spend a tick
overnight or on weekends when nothing real is moving.

## What each tick actually does
1. If `ArtifactData`/Webull tools aren't loaded this tick, `ToolSearch` for
   them (`select:ArtifactData`, `select:mcp__Webull__get_account_balance,
   mcp__Webull__get_account_positions,mcp__Webull__get_stock_quotes`).
2. Read `TRADING-DESK.md` for `max_daily_loss_usd` and the account_id (the
   authoritative source, not a cached value).
3. **Daily-loss fast check (the highest-value part of this heartbeat):**
   pull real `get_account_balance`. If today's real day P&L, combined with
   `trading_halted/current.daily_pnl_usd`, has now crossed
   `-max_daily_loss_usd` and `trading_halted/current.halted` isn't already
   `true`: immediately `update` `trading_halted/current` with
   `halted: true` and a reason, and message the owner right away — don't
   wait for the top-of-hour Risk Monitor pass to catch this.
4. **Open-position fast check:** `query` `proposed_trades` for
   `status == "approved"` and not yet closed. If any exist, pull real
   current quotes for those tickers and compare against `stop`, `target`,
   and `invalidation_point`. If one is breached: message the owner
   immediately with the real price and which level was hit, and `update`
   that `proposed_trades` doc with `fast_check_alert: {hit: "stop"|
   "target"|"invalidation", price, at: ISO8601}` — **do not** write a
   `performance_log` entry or mark it `closed` here; that formal
   close-out stays Post-Trade Review's job on the next hourly cycle
   (reading `fast_check_alert` if present), so there's exactly one place
   that ever writes the authoritative performance record.
5. If neither check found anything: end the tick with no message and no
   writes. A quiet tick is the expected, healthy default — there are
   currently 0 open positions, so most ticks will be step 3 only (one
   real Webull balance call) with nothing to alert on.

## Boundaries
- Never calls a Webull order-placement tool — same rule as everywhere else
  in this system. This heartbeat only reads and alerts.
- Never duplicates `ROUTINE.md`'s research/approval work. If something
  needs a new decision (not just detecting a breach of an existing
  approved trade), that's the hourly cycle's job, not this one's.
- Stops the moment this session ends — the owner should not treat "I set
  up the heartbeat" as "the desk is now watched 24/7 no matter what." It
  is watched fast *while this session is open*, and watched hourly
  *always* (that part is durable).
