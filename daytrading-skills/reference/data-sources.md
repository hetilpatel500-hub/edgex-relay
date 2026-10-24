# Market data for the day-trading skills

Every script accepts the same data flags. `--source auto` (the default) picks, in order:

1. `--csv FILE` / `--csv-dir DIR` if given
2. Alpaca, if `ALPACA_API_KEY_ID` and `ALPACA_API_SECRET_KEY` are set (free account, IEX feed, years of 1-minute bars)
3. Yahoo Finance via `yfinance`, if installed (free; 1m bars for ~30 days, 2m/5m for 60 days, daily for years)

Other sources:

| flag | what it is |
|------|------------|
| `--source relay` | The edgex-relay service in this repo (`RELAY_URL`, `RELAY_API_KEY`): live 1-minute futures bars from Databento, last ~500 bars. Good for entry-signal watching; too short for the time machine's history. |
| `--source demo` | Synthetic bars. Only for trying a skill out. Never present demo output as real market analysis. |

## Bars from a connector or the user

If the session has a market-data or brokerage connector (for example a broker MCP server with a "get bars" tool), or the user pastes or uploads bars:

1. Fetch the bars with that tool (intraday: 1m or 5m, as many days as it allows; daily: a year).
2. Save them as CSV with a header: `timestamp,open,high,low,close,volume`. Timestamps without a zone are read as exchange time (New York); ISO strings with an offset and epoch seconds/ms/ns also work. JSON lists of bar objects work too.
3. Pass `--csv path/to/bars.csv` (or `--csv-dir DIR` with one `<SYMBOL>.csv` per ticker for the scanner).

Column names are matched loosely (`t/o/h/l/c/v`, `Date`, `Close`, `ts_event` all work). Bars are treated as start-of-bar timestamps.

## Install

From the plugin folder (the one holding `requirements.txt`, two levels above each skill):

```bash
python3 -m pip install -r requirements.txt
```

Scripts exit with code 3 and print the exact command, with the full path, when numpy/pandas are missing. Exit code 2 is a usage or data problem; the message says what to change.

## Futures

Use Yahoo symbols like `MES=F`, `ES=F`, `NQ=F`, or a CSV/relay feed. Sessions default to US equity hours (09:30-16:00 New York); pass `--session` to change. Sessions must start and end on the same calendar day, so overnight futures sessions are not modelled.

## Network notes

Yahoo, SEC EDGAR and press-wire feeds are plain HTTPS. If a sandbox blocks them, scripts say so; fall back to a CSV from a connector, or (for news) to web search.
