---
name: exit-planner
description: Plans the exits for a day trade before entry - picks a stop from structure or volatility (or checks the user's stop), sets profit targets at real levels or R multiples, lays out scale-outs, breakeven and trailing rules, a time stop and a flat-by time, and flags targets beyond a normal day's range. Saves the plan for the time-machine skill to simulate. Use when the user asks "where should I take profit", "where do I put my stop", "exit plan", "when should I sell", "how do I manage this trade", or "cut losses or hold".
---

# Exit planner

Decide every exit while you are still calm, then simulate it.

## Run it

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/exit_planner.py" --symbol AAPL --side long --entry 187.50
python3 "${CLAUDE_SKILL_DIR}/scripts/exit_planner.py" --symbol AAPL --side long --entry 187.50 --stop 186.20 --shares 200
python3 "${CLAUDE_SKILL_DIR}/scripts/exit_planner.py" --symbol TSLA --side short --style single --first-r 2.5 --emit-plan plan.json
```

| option | use |
|--------|-----|
| `--stop` | the user's stop; omit it to have one chosen |
| `--style` | `scale` (50% at T1, 25% at T2, 25% runner), `thirds`, `single` (all at one target, 2R), `runner` (50% at T1, 50% trails) |
| `--first-r` | R multiple for the first target (default 1, or 2 for `single`) |
| `--trail-r` | runner trailing distance in R (default 1) |
| `--time-stop 45` | minutes allowed to reach +0.5R before bailing (0 = off) |
| `--flat-by 15:55` | hard exit time |
| `--emit-plan plan.json` | write the plan for `time_machine.py --plan plan.json` |

How the stop is chosen: the nearest real support (for longs) of 2+ stars, just beyond it, if that is between 0.08 and 0.5 daily ATRs away; otherwise 2x the intraday bar ATR; then a quarter daily ATR; then 1%. Targets snap to a real level when one sits near the R target (and never closer than 1R for T1). Data help: `${CLAUDE_SKILL_DIR}/../../reference/data-sources.md`.

## Present it

1. Stop and why, risk per share (and dollars with `--shares`)
2. Each target: price, R, size, why (level or R)
3. The management rules, numbered (breakeven after T1, time stop, flat-by, never widen the stop)
4. Notes: range already used today, stretch targets, wide stops

Then offer to run the time-machine skill on the saved plan to see how often it would have paid off.

## Guardrails

Plans, not orders. Never place or modify orders, even with a brokerage connector available.
