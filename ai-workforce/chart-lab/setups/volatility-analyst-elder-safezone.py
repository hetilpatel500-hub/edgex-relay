"""Elder SafeZone stop flip on 5-minute bars.
Added 2026-10-15 by volatility-analyst via WebSearch (Alexander Elder's SafeZone stops, "Come Into My Trading Room" 2002, as
described in StockCharts/TradingView write-ups: the stop sits a multiple of the average "noise penetration" beyond the prior
bar's extreme, ratchets with the trend, and a close through it flags that the trend has flipped; sources give no intraday test).
Parameters fixed BEFORE any P&L was seen: lookback 10 bars, coefficient 2.0. Downside penetration of a bar = prior low - low when
the low is below the prior low (upside: high - prior high); average over the penetrating bars of the last 10 bars (0 if none).
Long-side stop = prior low - 2.0 * avg downside penetration, ratcheted upward only; short-side stop mirrored and ratcheted down
only; the series restarts each session. Trend flips down at the first close below the ratcheted long stop (signal short at that
close) and up at the first close above the ratcheted short stop (signal long). Signals between 10:00 and 14:30 ET, one per side
per session. No VWAP or volume filter.
"""

N, COEF = 10, 2.0


def elder_safezone(s):
    b = s.bars
    n = len(b)
    long_stop = short_stop = None
    done = {1: False, -1: False}
    for i in range(N, n - 1):
        dn = [b[k - 1].l - b[k].l for k in range(i - N + 1, i + 1) if b[k].l < b[k - 1].l]
        up = [b[k].h - b[k - 1].h for k in range(i - N + 1, i + 1) if b[k].h > b[k - 1].h]
        ad = sum(dn) / len(dn) if dn else 0.0
        au = sum(up) / len(up) if up else 0.0
        ls = b[i - 1].l - COEF * ad
        ss = b[i - 1].h + COEF * au
        prev_ls, prev_ss = long_stop, short_stop
        long_stop = ls if prev_ls is None else max(prev_ls, ls)
        short_stop = ss if prev_ss is None else min(prev_ss, ss)
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        if prev_ls is not None and not done[-1] and b[i].c < prev_ls:
            done[-1] = True; yield i, -1
            long_stop = ls
        elif prev_ss is not None and not done[1] and b[i].c > prev_ss:
            done[1] = True; yield i, 1
            short_stop = ss


SETUPS = [
    dict(id='elder_safezone_flip', name='Elder SafeZone stop flip', family='volatility',
         detect=elder_safezone,
         rules="Elder's SafeZone puts a stop two average 'noise penetrations' beyond the prior bar's low (for longs) or "
               "high (for shorts) and only lets it ratchet with the trend. Between 10:00 and 14:30 the first 5-minute "
               "close through the ratcheted long stop leans short, the first close through the ratcheted short stop "
               "leans long; one signal per side per session, tested with and against."),
]
