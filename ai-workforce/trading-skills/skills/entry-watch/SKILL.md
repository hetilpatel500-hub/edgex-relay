---
name: entry-watch
description: Checks whether a planned entry's trigger has fired (a tested setup, or a break, reclaim or bounce of a price level) and runs a checklist covering VWAP side, volume, trend, the market, the trade tape and order book, time left, stop distance and event risk. Returns READY, CAUTION, WAIT or INVALID. Use when the user asks whether it is time to get in, or wants a trigger watched.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# Entry watch

`STORE` is `${CLAUDE_PLUGIN_DATA}/market-data` unless the user names another folder. If it lacks recent bars for the symbols, fetch and ingest them first: read `${CLAUDE_PLUGIN_ROOT}/docs/DATA.md`. Ingest the latest 5-minute bars right before checking; a stale store gives a stale answer.

## Run

Setup trigger (the setup must fire in your direction once its tested side is applied, with its filter met):
```
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE entry --symbol TSLA --side long --setup round_number_bounce --results backtest.json --stop 368.0
```
Level trigger:
```
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE entry --symbol SPY --side long --level 762 --trigger reclaim --stop 760.5
```
- `break` = first close beyond the level today; `reclaim` = back on your side after closing on the wrong side; `bounce` = tagged the level and closed at least 0.1 ATR away.
- Optional order flow from saved read-only responses: `--ticks` (get_stock_tick), `--book` (get_stock_quotes), `--flow` (get_stock_capital_flow). Optional `--events events.json` from event-calendar.
- A past moment: `--date YYYY-MM-DD --time HH:MM`.

## How to present

- State the status first, then each check with its detail. The trigger is required; the rest are evidence for or against.
- READY means the conditions asked for are present, not that the trade will work. INVALID means price is already through the stop.
- For watching over time, re-ingest bars and re-run on each new 5-minute close. Don't loop faster than the bars change.

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
