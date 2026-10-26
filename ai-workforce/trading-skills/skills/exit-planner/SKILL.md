---
name: exit-planner
description: Tests a grid of stop and profit-target choices (ATR and R multiples, plus the session's own levels such as VWAP, its bands, the opening range, the initial balance, the protected swing and yesterday's high, low and close) through the time machine, and ranks them by expected result after costs next to a coin-flip baseline. Use when the user asks where to put a stop, when to take profit, or how to plan an exit.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# Exit planner

`STORE` is `${CLAUDE_PLUGIN_DATA}/market-data` unless the user names another folder. If it lacks recent bars for the symbols, fetch and ingest them first: read `${CLAUDE_PLUGIN_ROOT}/docs/DATA.md`.

## Run

```
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE exits --symbol AAPL --side long
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE exits --symbol AAPL --side long --setup prior_range_tag --results backtest.json
```
- Entry defaults to the last close (`--entry PRICE` to change it). A past moment: `--date --time`. `--no-levels` keeps only the ATR/R grid.
- With `--setup`, every plan is judged on that setup's own past signals rather than all past days at this time.

## How to present

- Show the expected-R grid (stops down the side, targets across), then the top plans with target-first and stop-first odds and the coin-flip comparison.
- The best plan comes with a 90% range, and it is the best of many tried on the same history: expect less in the future. Prefer a region of good cells over a single cell.
- If the engine says no plan is positive after costs, say that plainly: the exit choice only trades win rate for payoff; it doesn't create an edge.
- Turn the chosen exit into prices and times the user can act on themselves.

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
