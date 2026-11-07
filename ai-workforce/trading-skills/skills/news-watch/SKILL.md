---
name: news-watch
description: Groups recent headlines about a stock into stories, marks a story confirmed only when two or more independent outlets carry it, tags catalysts, and measures how far the stock has moved since the story broke. Use when the user asks what news could move a stock, what is going on with a ticker, or whether news is already priced in.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py *)
license: MIT
---

# News watch

## Steps

1. Fetch the feed with read-only tools: `get_stock_news` (symbol) and, for a theme, `search_news` (keyword). Save each response as JSON.
2. Search the web for the main stories and save the results you actually read as `web.json`: `[{"title", "url", "date"}]`. Never add a result that did not appear.
3. Run:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE news --symbol NVDA --alias Nvidia --webull news.json --web web.json --days 14
   ```
   `--alias` adds company names to match in headlines. `--data STORE` lets it measure the move since each story first appeared (needs that symbol's 5-minute bars).

## How to present

- Lead with confirmed stories (2+ independent outlets inside 14 days): headline, when it first appeared, the outlets, the catalyst tags, and the move since.
- Single-source stories go in a separate, clearly labelled list. Several items from one outlet are still one source.
- Don't say a headline caused a move unless a cited source says so. Feed sentiment labels are the feed's, not yours.

## Always

- Analysis only. Use read-only market-data tools; never call a tool that places, changes or cancels orders or touches an account. The plugin's hook blocks them.
- Report only what the engine printed: numbers with their ranges and sample sizes. Never invent numbers, news, or reasons for a move.
- Never tell the user to buy or sell; describe the evidence and its limits.
- End every answer with: "Educational only. Not financial advice."
