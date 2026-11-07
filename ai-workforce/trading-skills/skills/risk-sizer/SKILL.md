---
name: risk-sizer
description: Works out how many shares to trade from account size, risk per trade and the stop, capped by maximum position size and buying power, with 1R/2R/3R prices, the reward at a target, a daily loss limit, and pattern-day-trader warnings. Use when the user asks how many shares to buy, how much to risk, or whether a position is too big.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# Risk sizer

The user supplies every number. This skill never reads or touches a brokerage account; don't use account tools to look the numbers up.

## Run

```
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py size --account 25000 --risk-pct 0.5 --entry 211.60 --stop 210.90 --target 213.00 --atr 0.72
```
- Caps: `--max-position-pct` (default 25) and `--buying-power`. Lots: `--lot`.
- Daily guard: `--realized-today -320 --daily-loss-limit-pct 2`.
- `--expected-r` (from the time machine) converts its expected result to dollars per trade.

## How to present

- Shares, dollars at risk and % of the account, position value, the R prices, and every warning the engine printed.
- If the daily loss limit is hit, say the plan calls for no more trades today.
- Ask for the account size and risk % if the user hasn't given them. Don't assume.

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
