# Getting data into the store

Every skill reads bars from a **store**: a folder of `SYMBOL_M5.csv.gz` (5-minute
bars) and `SYMBOL_D.csv.gz` (daily bars). Use one store for everything:

- default: `${CLAUDE_PLUGIN_DATA}/market-data` (kept across plugin updates);
- or a folder the user names (for example an existing chart-lab `data/` folder,
  which already uses this layout).

Pass it to every command as `--data STORE`.

## With a read-only market-data connector (Webull shown)

Only ever call **read-only** tools. Never call a tool that places, changes or
cancels orders or reads/changes an account; this plugin's hook blocks them.

| Need | Tool and arguments |
|---|---|
| 5-minute bars | `get_stock_bars` symbols (up to 20), category `US_STOCK` (or `US_ETF` for ETFs), timespan `M5`, count up to 1200 (~15 sessions), trading_sessions `RTH`, real_time_required `false` |
| daily bars | same with timespan `D`, count up to 1200 (~4.7 years) |
| trades / book / money flow (entry-watch) | `get_stock_tick` count `1000`, trading_sessions `RTH`; `get_stock_quotes` depth `50` (fall back to `10`); `get_stock_capital_flow` count 5 (stocks only) |
| news | `get_stock_news` symbol; `search_news` keyword |
| calendars | `get_stock_earnings_calendar` symbol, category `US_STOCK`; `get_macroeconomic_calendar` start_date / end_date |
| watchlist candidates | `get_gainers_losers` rank_type `DAY_1` (or `MIN_5`), sort_by `CHANGE_RATIO`; `get_most_active` rank_type `VOLUME` or `RELATIVE_VOLUME_10D` |
| sectors | `get_market_sectors` category `US_STOCK`, period `D1` |

Save each response **exactly as returned** to a JSON file (when a result is too
large and the tool saves it to a file, use that file), then:

```
python3 ${CLAUDE_PLUGIN_ROOT}/engine/ts.py --data STORE ingest saved1.json saved2.json
```

Mixed symbols in one response are fine. ETFs and stocks need separate calls
(different category).

## Without a connector

Any CSV with a header naming time (or date + time), open, high, low, close and
volume works; name the file after the symbol (`AAPL_5m.csv`) or pass
`--symbol AAPL`. 1-minute bars are rolled up into 5-minute bars; 15-minute and
hourly bars are refused. Times without an offset are read as New York time.

## How much history

- time machine and backtests: 40+ full sessions to start, 100+ to trust;
- daily setups: 200+ days (they use a 200-day average);
- the more symbols in the store, the more past days the time machine can learn from.

## News confirmation from the web

For `news-watch`, run a web search for the story and save the results you
actually read as a JSON list: `[{"title": ..., "url": ..., "date": "YYYY-MM-DDTHH:MM:SSZ"}]`.
Only list results that appeared in the search; never fabricate an entry.

## Keep vendor data private

Market data usually comes with terms that forbid redistribution. Keep the store
local; don't commit it to a public repository or paste it into public pages.
