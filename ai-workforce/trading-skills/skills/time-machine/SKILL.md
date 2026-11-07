---
name: time-machine
description: Replays the rest of the trading session thousands of times from historical 5-minute bars to show how often a planned day trade hits its target first, its stop first, or neither by the close, next to a coin-flip baseline and a 90% range. Use when the user asks for the odds, probability or win rate of a specific trade, or wants to test a trade before risking money.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# Time machine

Answers: "if I take this trade now, how did the rest of the day go on past days like this?"

`STORE` is `${CLAUDE_PLUGIN_DATA}/market-data` unless the user names another folder. If it lacks recent bars for the symbols, fetch and ingest them first: read `${CLAUDE_PLUGIN_ROOT}/docs/DATA.md`.

## Run

```
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE time-machine --symbol NVDA --side long --stop-atr 1 --target-r 2
```

- Entry defaults to the last 5-minute close; pass `--entry PRICE`. Stop: `--stop PRICE` or `--stop-atr N` (5-minute ATRs). Target: `--target PRICE`, `--target-r N` or `--target-atr N`.
- To test a past moment: `--date YYYY-MM-DD --time HH:MM` (New York time; the result then also shows what really happened).
- If the trade comes from a tested setup, also run with `--setup ID` (ids from the chart-scanner or backtester). Setup mode replays that setup's own past signals, which is where an edge shows up. Clock-time mode only knows the time of day and volatility.
- Add `--json` for raw numbers and `--save FILE` to keep them for the journal.

## How to explain the result

1. Lead with the three odds (target first / stop first / neither) **and the coin-flip row**. With a 1-ATR stop and a 2-ATR target, a coin flip reaches the target first about a third of the time. The edge is the gap, not the raw percentage.
2. Give the 90% range and the number of real past days or signals behind it. 10,000 paths come from a few hundred real days: more paths make the numbers smoother, not truer.
3. Give the expected result in R after costs, the median time to target and to stop, and the R spread.
4. Pass on every note the engine printed, especially "no clear edge" and "part of this history was used to choose the setup's side and filter".
5. Never present the odds as a forecast or a promise. In walk-forward tests, clock-time odds matched reality on average but did not beat the coin flip trade by trade; setup mode did slightly better than the coin flip on 4 of 6 tested setups. Say which mode you used.

To check that the odds mean what they say on the user's own data:
`python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE calibrate` (clock-time mode) or `python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE calibrate --mode setup --setup ID`.

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
