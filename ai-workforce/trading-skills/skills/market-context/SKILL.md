---
name: market-context
description: Summarises the market regime from SPY, QQQ, IWM and DIA (change on the day, side of VWAP, intraday trend, 200-day trend, realised-volatility percentile) plus breadth across the store and sector advancers and decliners. Use when the user asks how the market is doing, or before judging a single stock's setup.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# Market context

`STORE` is `${CLAUDE_PLUGIN_DATA}/market-data` unless the user names another folder. If it lacks recent bars for the symbols, fetch and ingest them first: read `${CLAUDE_PLUGIN_ROOT}/docs/DATA.md`. Include SPY, QQQ, IWM and DIA (category `US_ETF`), with daily bars too.

## Run

```
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE context --sectors sectors.json
```

- `--sectors` is optional: a saved `get_market_sectors` response (category `US_STOCK`, period `D1`).
- `--date YYYY-MM-DD` reviews a past session.

## How to present

- One line for the regime (trend up, trend down, mixed / range) and the volatility level, then the facts behind it: each index's change, VWAP side, trend, and 200-day position, then breadth and sectors.
- The label summarises those facts; it is not a forecast. Don't add reasons for the move that no source gave.

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
