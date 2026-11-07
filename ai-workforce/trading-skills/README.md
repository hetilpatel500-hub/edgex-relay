# Edgex Trading Skills

Twelve free, read-only day-trading research skills for Claude Code. They scan charts,
check news and events, read the market, plan entries and exits, size positions, keep
a paper-trade journal, and run a **time machine** that replays the rest of the trading
day thousands of times on historical bars, so you can see the historical odds of a
trade before any money is at risk.

**Analysis only.** No skill places, stages or cancels an order. While the plugin is
enabled, a hook blocks every broker order tool Claude might have, from any connector.
You make every decision and place any trade yourself, outside Claude.

> Educational only. Not financial advice. Historical odds describe the past, not the future.

## The skills

| Skill | What it does |
|---|---|
| `chart-scanner` | Scans the latest 5-minute and daily bars across the store (or a watchlist built from today's top movers) for setups, ranked by each setup's tested evidence on **your** data |
| `news-watch` | Groups headlines into stories; a story counts as confirmed only when 2+ independent outlets carry it; shows how far the stock moved since it broke |
| `event-calendar` | Earnings dates and high-impact releases (CPI, PCE, jobs, GDP, Fed) with New York times |
| `market-context` | The regime from SPY/QQQ/IWM/DIA: day change, VWAP side, trend, 200-day trend, volatility percentile, breadth, sectors |
| `entry-watch` | Has the trigger fired (a tested setup, or a break/reclaim/bounce of a level)? Then a checklist: VWAP, volume, trend, market, trade tape, order book, time left, stop distance, event risk |
| `exit-planner` | Tests a grid of stops and targets (ATR/R multiples and the session's own levels) through the time machine and ranks them by expected result after costs |
| `time-machine` | Replays the rest of the day thousands of times: how often the target was hit first, the stop was hit first, or neither by the close, next to a coin-flip baseline |
| `backtester` | In-sample/out-of-sample backtests with filters, ATR exits, a luck check against random entries, an equity shuffle and forward tests |
| `risk-sizer` | Shares from account size, risk % and stop, with position caps, R prices, a daily loss limit and pattern-day-trader warnings |
| `trade-journal` | Logs plans with their odds, settles paper trades on the bars, and checks whether the recorded odds came true |
| `daily-review` | After the close: market recap, what the scanner's hits actually did, journal results, setup changes |
| `trade-plan` | Every skill on one idea, in one report |

## What we did differently

The idea "test your trade 10,000 times" is easy to oversell, so the skills are built to keep it honest:

- **A coin-flip baseline next to every result.** With a 1-ATR stop and a 2-ATR target, even a coin flip reaches the target first about a third of the time. The time machine shows the same simulation with direction removed, so the edge (the gap) is visible.
- **Real-day counts and 90% ranges, not just 10,000 paths.** The paths are rebuilt from a few hundred real days; the ranges come from re-drawing those days, and the plain count on the real days is shown beside them.
- **Setup mode.** When a trade comes from a tested setup, the time machine replays that setup's own past signals. In our tests that is where an edge, if any, shows up.
- **Calibration you can re-run.** `ts.py calibrate` checks walk-forward whether the odds came true. Our results are in [docs/CALIBRATION.md](docs/CALIBRATION.md) and summarised below, including where the tool did *not* beat the coin flip.
- **No look-ahead.** A trade on a given date only learns from days before it.
- **Luck checks on backtests.** Each result is compared with random entries using the same exit and trade count, and the number of variants tried is reported.
- **An exit planner that can say no.** It smooths the grid so one lucky cell can't win, gives a range for the best plan, and reports plainly when no exit is positive after costs.
- **A journal that grades the odds.** Paper trades settle on the bars, and the journal tracks whether the recorded odds came true (Brier score against the coin flip).
- **No dependencies.** Python 3.9+ standard library only. Works with a Webull connector, or with any CSV of 1- or 5-minute bars.

## What the calibration found (our data)

Store: 12 US symbols (SPY, QQQ, IWM, DIA, AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA, AMD),
107 sessions from 2026-05-15 to 2026-10-23. Trade tested: 1 ATR stop, 2R target, flat by the close.

- **Clock-time mode on 600 random walk-forward trades:** predicted 33.0% target-first on average; actual 31.2% (90% range 28.1–34.4%). Calibrated on average, but **no better than the coin flip trade by trade** (Brier 0.2173 vs 0.2154). It knows the time of day and volatility, not direction.
- **Setup mode on 332 out-of-sample signals from 6 setups:** better than the coin flip on 4 of 6 setups, worse on 2. Pooled Brier 0.2434 vs 0.2460 (skill +0.011): a small, real improvement, not a crystal ball.

The full table and method are in [docs/CALIBRATION.md](docs/CALIBRATION.md). Re-run it on your own data with
`python3 engine/tools/calibration_report.py --data STORE --out CALIBRATION.md`.

## Install

From a clone of this repository, add it as a marketplace and install the plugin:

```
/plugin marketplace add ./path/to/trading-skills
/plugin install edgex-trading-skills@edgex-skills
```

Or try it for one session with `claude --plugin-dir ./path/to/trading-skills`.

## Quick start

```
# 1. Get bars into a store (Webull responses saved as JSON, or any CSV)
python3 engine/ts.py --data market-data ingest spy_m5.json nvda_m5.json spy_d.json

# 2. Test the built-in setups on your data, then scan
python3 engine/ts.py --data market-data --save backtest.json backtest
python3 engine/ts.py --data market-data scan --results backtest.json

# 3. The time machine: NVDA long now, 1-ATR stop, 2R target
python3 engine/ts.py --data market-data time-machine --symbol NVDA --side long --stop-atr 1 --target-r 2

# 4. The same with a setup's own history, then the full plan
python3 engine/ts.py --data market-data time-machine --symbol NVDA --side long --stop-atr 1 --target-r 2 --setup round_number_bounce --results backtest.json
python3 engine/ts.py --data market-data plan --symbol NVDA --side long --stop-atr 1 --target-r 2 --account 25000 --risk-pct 0.5
```

Inside Claude Code you just ask ("what are the odds on an NVDA long here with a 1-ATR stop?"),
and the skills run these commands. [docs/DATA.md](docs/DATA.md) lists the read-only tools and arguments for fetching data.

## How the time machine works

1. **Memory:** every full past session in the store, strictly before the trade's date, pooled across symbols (each in its own ATR units).
2. **Paths:** each path stitches 30-minute blocks taken from random past days at the same clock times. This keeps the time-of-day pattern of volatility and short-term momentum. Each block is rescaled from its own day's ATR to today's.
3. **Walk:** each path is walked bar by bar against the stop and target. The stop counts first if one bar touches both, gaps fill at the open, and the position is flat at the close. Round-trip costs come off.
4. **Report:**
   - odds and expected R, with 90% ranges from re-drawing the days;
   - the plain count on the real days;
   - the coin-flip baseline: the same paths with block directions randomised;
   - when the day is already complete, what actually happened.
5. **Setup mode** (`--setup ID`): the memory is that setup's own past signals (with the side and filter its backtest chose), each replayed from its signal bar, oriented to your trade and rescaled to today's ATR.

## Limits to keep in mind

- **Survivor bias in the built-in setups:** the 7 included setups are the ones that passed testing on our data, out of 333 tried. Expect their future results to be weaker. Re-test on your own data; the scanner ranks by **your** backtest.
- **Short history:** five months of 5-minute bars on 12 large, liquid US symbols. Small caps, other regimes, and premarket or after-hours trading are not covered.
- **Fills are idealised:** 5-minute bars hide the order of prices inside a bar (the stop is assumed first), and costs are a fixed 2–3 bps round trip. Real fills, slippage on fast moves, and halts can be worse.
- **Stocks and ETFs only:** no options, futures or crypto.
- **News and events are labels, not causes:** the tools never claim a headline moved a stock.

## Safety, data and legal

- `hooks/block_orders.py` runs before every MCP tool call and blocks any tool whose name places, changes or cancels orders or closes positions. Read-only tools pass. Disable the plugin to remove the hook.
- Market data usually comes with terms that forbid redistribution. Keep your store local and private. This repository ships code only, and the calibration report contains aggregate statistics only.
- Read [DISCLAIMER.md](DISCLAIMER.md). Nothing here is investment advice, and past results don't guarantee future results.

## Tests

```
cd engine/tests && python3 test_engine.py
```

The tests use synthetic random-walk data. They also check that the time machine recovers the textbook coin-flip odds on a pure random walk, and that the safety hook blocks order tools.

## License

MIT. See [LICENSE](LICENSE).
