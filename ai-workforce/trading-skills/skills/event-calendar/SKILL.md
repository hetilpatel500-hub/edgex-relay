---
name: event-calendar
description: Flags earnings dates and high-impact economic releases (CPI, PCE, jobs, GDP, retail sales, ISM, Fed decisions and speakers) that can gap or spike a stock, with New York times, plus the last earnings surprise. Use before planning a trade, or when the user asks about earnings or economic events today or this week.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# Event calendar

## Steps

1. Fetch with read-only tools: `get_stock_earnings_calendar` for each symbol (category `US_STOCK`; the response does not name the symbol, so keep one file per symbol), and `get_macroeconomic_calendar` for today through the next few days. Save each response as JSON.
2. Run:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --save events.json events --earnings AAPL=aapl.json NVDA=nvda.json --macro macro.json --days 5
   ```
   Pass `--today YYYY-MM-DD` to check another day.
3. `events.json` can be handed to entry-watch (`--events`) and trade-plan so their checklists include event risk.

## How to present

- High flags first: earnings today or tomorrow, and high-impact releases today with their ET time. Prices often jump in the minutes around a release.
- The feed does not say whether earnings come before the open or after the close. Say so; don't guess.
- Then the coming days, and the last earnings surprise (actual vs estimate).

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
