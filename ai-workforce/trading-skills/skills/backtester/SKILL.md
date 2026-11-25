---
name: backtester
description: Backtests chart setups on the store's bars with one in-sample/out-of-sample split, a with-or-fade choice, filters and ATR exits, then adds a luck check against random entries and an equity shuffle for drawdowns. Use when the user wants to know whether a setup works, wants a new setup tested, or asks for a setup's track record.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# Backtester

`STORE` is `${CLAUDE_PLUGIN_DATA}/market-data` unless the user names another folder. If it lacks recent bars for the symbols, fetch and ingest them first: read `${CLAUDE_PLUGIN_ROOT}/docs/DATA.md`.

## Run

```
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE --save backtest.json backtest
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE backtest --only round_number_bounce gap_go_rvol
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE backtest --frozen frozen.json --out backtest.json
```
- `--frozen FILE` freezes the first validated or promising variant of each setup and forward-tests it on every later day, with no re-tuning.
- `--setups-dir DIR` (before the command) adds setup files. A new setup is a Python file with a `SETUPS` list; copy the format of `${CLAUDE_PLUGIN_ROOT}/engine/setups/round_number_bounce.py`. Write the rules **before** looking at any results, and never tune them to the out-of-sample period.

## How to present

- Status first: validated / promising / insufficient / rejected / retired, and what it rests on. Give out-of-sample trades, win rate, average R, profit factor, t-stat and symbols positive.
- Give the luck check: p = how often random entries with the same exit and trade count did as well. Many setups tested means some pass by luck. Say how many were tried.
- Give the equity-shuffle drawdown (p50 and p90) as the pain to expect with the same trades in a different order.
- Results are history on this store's symbols and dates only.

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
