---
name: trade-journal
description: Records trade plans with the time machine's odds, closes them with real fills or settles paper trades on the bars, and reports win rate, R by setup and whether the recorded odds came true. Use when the user wants to log, review or paper-trade trades, or asks how their trading or the odds have done.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# Trade journal

Journal file: `${CLAUDE_PLUGIN_DATA}/trade-journal.jsonl` unless the user names one. Pass it as `--file`.

## Commands

```
J=${CLAUDE_PLUGIN_DATA}/trade-journal.jsonl
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE --save tm.json time-machine --symbol NVDA --side long --stop 210.9 --target 213
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE journal plan --file $J --symbol NVDA --side long --entry 211.6 --stop 210.9 --target 213 --setup round_number_bounce --time 11:05 --tm tm.json
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE journal close --file $J --id 2026-10-23-NVDA-1 --exit 212.40 --exit-time 12:10
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE journal settle --file $J
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE journal report --file $J
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE journal list --file $J
```
- `--mode paper` (default) plans are settled on the bars by `settle` once the session is complete, with costs. Use `--mode real` for the user's own trades; close those with the user's actual fill.
- Record odds with `--tm` only when the time machine used the same stop and target, or the odds check will skip the trade.

## How to present

- Overall and by-setup results (trades, win rate, average R, drawdown).
- The odds check: predicted target-first vs actual, with its 90% range, and Brier score vs the coin flip. With few trades, say it is too early to judge.

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
