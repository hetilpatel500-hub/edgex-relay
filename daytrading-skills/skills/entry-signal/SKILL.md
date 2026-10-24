---
name: entry-signal
description: Watches a stock intraday for a defined entry trigger - opening range breakout/breakdown, VWAP reclaim or rejection, trend pullback to the 9 EMA, high/low-of-day break from a tight base, red-to-green and green-to-red - and reports each signal's status (triggered, armed, invalidated), exact trigger price, structural stop and a 0-100 quality score with reasons. Can keep polling and alert on new triggers. Use when the user asks "is there an entry on X", "watch X for a breakout", "tell me when it reclaims VWAP", "did the ORB trigger", "where do I get in", or wants an entry signal.
---

# Entry signal

Defined triggers with a stop attached. No trigger, no trade.

## One check

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/entry_signal.py" --symbol AMD
python3 "${CLAUDE_SKILL_DIR}/scripts/entry_signal.py" --symbol AMD --side long --only orb,vwap --regime trend-up
```

Signal families for `--only`: `orb` (opening range, `--orb 5|15|30`), `vwap` (reclaim / rejection), `pullback` (trend pullback to the 9 EMA), `range` (HOD/LOD break from a base), `r2g` (red-to-green / green-to-red). `--regime` takes the market-regime label. `--min-quality 60` hides weak setups. Uses 1-minute bars for the last 7 days by default (`--interval 5m` for slower charts).

## Keep watching

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/entry_signal.py" --symbol AMD --watch 60 --until 11:30
```

Prints a line each time a new trigger fires and stops at `--until` (default: the close). Run it in the background and tell the user what you are watching for. For live futures bars, use the relay: `--source relay --symbol MESZ6 --watch 30`. Data help: `${CLAUDE_SKILL_DIR}/../../reference/data-sources.md`.

## Statuses

- **triggered**: fired recently and still valid. If it fired more than 3 bars ago the score drops; chasing a late trigger is a worse trade.
- **armed**: conditions are in place; the trigger price is where it would fire.
- **forming**: the opening range is still building.
- **invalidated**: fired, then failed (e.g. back inside the opening range).

Quality starts at 50 and moves with trigger-bar volume, the day's relative volume, VWAP side, EMA alignment, regime, stop width versus daily ATR, extension beyond the 2σ VWAP band and time of day (lunch and the last hour cost points). Reasons and warnings are listed under each signal.

## Present it

Lead with the best actionable signal: name, side, trigger, stop, risk per share, quality and its top reasons. Mention warnings plainly. Then offer the next steps: position-sizer for size, exit-planner for targets, time-machine for the historical odds, risk-guard before entering.

## Guardrails

This skill alerts; it never places orders, even if a brokerage connector is available. A signal is a condition being met, not a recommendation.
