---
name: trade-plan
description: Runs every skill on one trade idea in a single report covering market context, event flags, the entry checklist, the time machine (clock-time and the setup's own history), the exit plan and position size, optionally logged as a paper trade. Use when the user wants a complete pre-trade check of a specific idea.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# Trade plan

`STORE` is `${CLAUDE_PLUGIN_DATA}/market-data` unless the user names another folder. If it lacks recent bars for the symbols, fetch and ingest them first: read `${CLAUDE_PLUGIN_ROOT}/docs/DATA.md`. Ingest fresh 5-minute bars for the symbol and SPY/QQQ first. Optionally save an event-calendar result (`events.json`) and order-flow responses.

## Run

```
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE plan --symbol TSLA --side long --stop-atr 1 --target-r 2 --account 50000 --risk-pct 0.5 --setup round_number_bounce --results backtest.json --events events.json
```
- Also accepts `--entry`, `--stop`/`--target` prices, `--level --trigger` for a level-based entry, `--ticks --book --flow`, `--date --time` for a past moment, and `--journal FILE` to log it as a paper trade.

## How to present

- Start with the engine's summary lines, in order, then the details a trader acts on: entry, stop and target prices, size, and the odds with their coin-flip comparison and ranges.
- Keep the engine's last line: it is a summary of the evidence, not a recommendation. The user decides, and places any trade themselves.

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
