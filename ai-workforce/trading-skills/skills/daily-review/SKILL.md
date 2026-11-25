---
name: daily-review
description: After the close, measures the day: market recap, how each of the scanner's hits actually played out with its tested exit, journal results (paper trades settled on the bars), setups whose status or forward test changed, and the running odds check. Use when the user asks how today went, or for an end-of-day review.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# Daily review

`STORE` is `${CLAUDE_PLUGIN_DATA}/market-data` unless the user names another folder. If it lacks recent bars for the symbols, fetch and ingest them first: read `${CLAUDE_PLUGIN_ROOT}/docs/DATA.md`. Ingest the full day's 5-minute bars after 16:00 New York time first.

## Run

```
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE --save backtest-new.json backtest --frozen ${CLAUDE_PLUGIN_DATA}/frozen.json
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE review --journal ${CLAUDE_PLUGIN_DATA}/trade-journal.jsonl --scans scan-1.json scan-2.json --results backtest-new.json --previous backtest.json
```
- `--scans` are scanner outputs saved with `--save` during the day. `--previous` is yesterday's backtest results, to list status changes. `--date` reviews another day.

## How to present

- Market first, then the scanner's tested hits (filter met) with what each actually did and their average R. Untested hits and hits that missed the filter go separately.
- Then the journal, setup changes (new validations, retirements, forward-test verdicts), and the odds check.
- Measured facts only. No narrative about why the market moved unless a cited source says so.

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
