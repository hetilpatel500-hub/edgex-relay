---
name: chart-scanner
description: Scans the latest 5-minute and daily bars of every symbol in the store, or a fresh watchlist built from today's top movers, for chart setups, ranked by each setup's tested evidence on the user's own data. Use when the user asks what is setting up, wants trade ideas, or wants many charts scanned at once.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# Chart scanner

`STORE` is `${CLAUDE_PLUGIN_DATA}/market-data` unless the user names another folder. If it lacks recent bars for the symbols, fetch and ingest them first: read `${CLAUDE_PLUGIN_ROOT}/docs/DATA.md`.

## Build a watchlist (optional, for scanning beyond the store)

1. Fetch rankings with read-only tools (see DATA.md): `get_gainers_losers` and `get_most_active`. Save each response as JSON.
2. `python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE universe gainers.json active.json --min-price 5 --min-volume 1000000 --max 40`
3. Fetch 5-minute bars for the listed symbols (up to 20 per `get_stock_bars` call), plus daily bars if daily setups matter, and ingest them.

## Scan

```
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE --save backtest.json backtest
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE --save scan.json scan --results backtest.json --lookback 3
```

- The backtest step gives each setup its evidence on this store. Reuse `backtest.json` all day; re-run it after the close.
- `--lookback N` = how many of the latest 5-minute bars count as fresh. `--symbols A B C` limits the scan. `--setups-dir DIR` (before the command) adds more setup files.

## How to present hits

- Group by status: validated, promising, then the rest. Only validated or promising setups **with the filter met** have tested evidence behind them. Everything else is a pattern that printed, not a signal.
- For each tested hit, give: symbol, setup, time, the traded direction (a "fade" setup is traded against its lean), the out-of-sample trades and average R, and the implied stop/target from its tested exit.
- Offer the next step: time-machine with `--setup` on the best hits, then entry-watch.
- The built-in setups survived testing on Edgex's own data (7 of 333). That survivor bias means their future results are likely weaker than shown. The user's own backtest is what counts.

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
