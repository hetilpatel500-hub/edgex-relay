# Chart Desk

A 20-agent department built only to read the owner's chart screenshots,
for **intraday options** trading. It lives in its own room on the Studio
Floor (north-east corner, door on the west side) and opens from the
**Chart Desk** button.

## How a run works

1. The owner drops, pastes or picks up to 5 screenshots, usually the same
   ticker on 1m, 5m, 15m and 1h (any timeframe works, even a phone photo of
   a screen), and types the ticker plus a question in the note, e.g. "SPY:
   calls or puts for the next 30 min?".
2. **Live Webull data.** Once the ticker is known (from the note, or read
   off the chart), the page pulls from the owner's Webull connector,
   read-only: a snapshot (last, bid/ask, pre-close, 52-week range, session),
   1m/5m/15m/1h/daily bars, the top of the order book, the next earnings
   date, and SPY/QQQ (or QQQ/IWM) for market context. From real bars it
   computes EMA 9/20/50/200, SMA 20/50/200, RSI(14), MACD(12,26,9),
   Stochastic(14,3), ATR(14), Bollinger(20,2), relative volume and swing
   points per timeframe, plus session VWAP, today's open/high/low,
   premarket high/low, 5/15/30-minute opening ranges, prior-day
   high/low/close, classic pivots, daily ATR and how much of it is used,
   and minutes to the close. Every analyst is told these numbers are exact
   and beat anything read off the picture.
   On top of that the page adds a **quant layer** that no model writes:
   - **Scorecard:** per timeframe (1m/5m/15m/1h), a signed score from
     price vs EMA20, EMA20 slope, EMA9 vs EMA20, MACD histogram sign and
     direction, and RSI zone, plus price vs VWAP and the 30-minute opening
     range; then how many timeframes agree.
   - **Similar setups:** the last ~15 regular sessions of 5-minute bars
     for this ticker, each bar tagged by the state the market is in now
     (vs VWAP, vs EMA20, EMA20 slope, RSI zone, time of day). The matches
     are followed 15/30/60 minutes forward inside the same session: % that
     went up, median change, typical run-up and drawdown, next to the
     same-time-of-day baseline so the edge is visible. If fewer than 15
     matches exist, time of day and then RSI zone are dropped from the
     match.
   - **Relative strength** vs SPY (or QQQ for SPY) today.
   - **Track record:** once 5+ calls are scored, the Head of Desk gets the
     desk's hit rate, this ticker's hit rate, and how often each
     analyst's bias matched what price actually did.
   Every analyst treats the similar setups as the base rate; the Head of
   Desk anchors the odds to it and sizes targets to what similar setups
   actually ran.
3. **Full desk** (about 4-6 minutes, ~21 Claude calls with the images):
   - **Chart Reader** reads every screenshot (timeframe, drawings,
     indicators shown, swings, recent candles).
   - Seventeen analysts run in parallel, each on one checklist: price
     structure; trend & moving averages; support & resistance;
     supply/demand & smart money; chart patterns; candlesticks; momentum
     oscillators; MACD & divergences; volume & VWAP; Fibonacci &
     harmonics; Elliott waves; volatility & expected move; session, time
     & gaps; Wyckoff phase; strategy playbook; risk; and the **Options
     Strategist**, who turns the read into calls / puts / no trade with
     expiry, strike, entry trigger, stops and a time stop.
   - **Devil's Advocate** checks every quoted price against the data and
     images, and flags options red flags (chop, time of day, earnings, a
     move too small to beat decay).
   - **Head of Desk** makes the call.
4. **Fast read** (about 1 minute): the Head of Desk alone, same data, same
   checklist in one pass.

The call gives: direction with odds and confidence; the next 15-60
minutes and into the close; expected move; price now (Webull's exact
print), targets and the price that proves it wrong; the **options play**
(buy calls / buy puts / no trade, 0DTE / 1DTE / weekly, strike guidance,
entry trigger, stop and targets on the underlying, a time stop, when to
skip it); the plan on the underlying; reasons, risks, key levels, the
devil's advocate's notes, each analyst's checklist, the live data used,
and a follow-up box.

## Data mode (when a view can't send pictures)

Some Claude views don't let a page show images to Claude (the call
rejects `images_unavailable`, or `sample.limits()` reports no images).
Then the desk runs on live Webull data alone: the owner types the ticker
in the Ticker box, and every analyst gets the recent 1m/5m/15m/1h/daily
candles as [time, open, high, low, close, volume] arrays alongside the
computed indicators, levels, scorecard and similar setups. Screenshots
become optional and are only saved with the call; a candle chart drawn
from the 5-minute data stands in on the wall and in History. If a view
claims image support but refuses mid-run, the desk switches to data mode
and reruns by itself when it knows the ticker.

Every call is also checked against Webull's live price: a target or
"wrong at" level more than 8% away is flagged as a probable misread.

## Rules

- **Runs on the owner's own accounts**, from the page: Claude through the
  artifact's `sample` capability, Webull through its `mcp` capability
  declared with four read-only tools (`get_stock_snapshot`,
  `get_stock_bars`, `get_stock_quotes`, `get_stock_earnings_calendar`).
  The page's manifest holds **no order tools**, so it cannot trade.
  Capital-flow data was left out.
- **No option-chain data.** Webull's connector offers no option quotes,
  so the desk never quotes premiums, IV or greeks. It plans on the
  underlying's price and says so.
- **Honest reads.** An indicator that is neither in the data nor on the
  chart is "not shown". Confidence is calibrated; "no trade" is a valid
  call.
- **Track record.** Every call is saved to `chart_analyses` with
  thumbnails and the live data used. **Check outcomes with Webull** (in
  History) walks the regular-hours bars after each call and records
  whether target 1 or the "wrong at" level came first; both in one bar
  counts as wrong. The owner can also mark calls by hand. The hit rate
  means little before 20+ scored calls.
- **Not part of the business shifts.** The hourly business shifts never
  assign the desk work and never read or write its collections. Between
  the owner's charts the desk works in the **Chart Desk lab** (below); its
  20 `agents` docs are written only by lab runs. The Edgex Capital trading
  system stays separate.

## Live tape (Studio Floor, Chart Desk → Live tape)

While the market is open the tab follows one symbol (default SPY) every 5
seconds from the owner's Webull connector, read-only:

- **Liquidity heatmap**: every level 2 snapshot (`get_stock_quotes`, depth
  50, or 10 if the account's data plan refuses 50) becomes a column; resting
  bids green, asks red, brighter = more size. 5-minute candles, the tick
  price path and big prints (bubbles) sit on top, with VWAP ±2σ, developing
  POC/VAH/VAL, yesterday's POC/high/low, IB high/low, the initial volume bar
  and the protected level drawn as lines.
- **Footprint**: Webull's own footprint feed is a paid add-on
  (`MARKET_DATA_NOT_SUBSCRIBED`), so the page rebuilds it from
  `get_stock_tick`: volume bought at the ask vs sold at the bid per price
  bucket (2 bps), delta, and 3:1 diagonal imbalances outlined.
- **Big prints** ("deep trades"): the top 1% of trade sizes, at least 5,000
  shares, with side.
- **Session levels** and **playbook signals today** (from the lab's hourly
  market-hours run, `chart_live/<SYM>`).

When the owner runs Analyze on the symbol being followed, the desk gets this
same read (`live_tape` in the market data), plus the lab playbook
(`lab_playbook`); otherwise Analyze pulls 1,000 ticks and a 10-level book
once for the ticker. Level 2 was untested at build time (the book is empty
outside market hours); if the page reports an empty book during market hours,
the owner's Webull account likely has level 1 data only.

## Chart Desk lab

`chart-lab/` backtests the desk's knowledge on Webull bars and keeps it
honest: 5-minute bars for 12 symbols (SPY QQQ IWM DIA AAPL MSFT NVDA AMZN
GOOGL META TSLA AMD) and 4.7 years of daily bars, costs included, tuned on
the first 70% of dates and judged on the last 30%, then frozen and forward
tested on every new day. Results go to `chart_playbook` (one doc per setup,
shown on the Lab tab and fed into every analyst's prompt), the log to
`chart_research`, the hourly live read to `chart_live`, and state to
`chart_lab_state`. Three Routines drive it:

- **Edgex Chart Desk lab** (hourly, fresh session): one new researched
  setup per run, coded, backtested and published.
- **Edgex Chart Desk live tape** (weekdays, hourly 9:38-15:38 ET, the
  owner's connected session with read-only Webull): the live read for all
  12 symbols to `chart_live`, and the order-flow rows kept for future
  order-flow backtests.
- **Edgex Chart Desk data refresh** (weekdays 16:21 ET, the owner's
  connected session): stores the day's bars and tape rows in the repo,
  re-runs every forward test, commits and pushes.

Runbook, method and research queue: `chart-lab/README.md`. Current
results: `chart-lab/PLAYBOOK.md`.
