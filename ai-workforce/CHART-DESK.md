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
- **Not part of the business shifts.** The desk's agents have no docs in
  the `agents` collection; the hourly shifts never assign them work and
  never read or write `chart_analyses`. The Edgex Capital trading system
  stays separate.
