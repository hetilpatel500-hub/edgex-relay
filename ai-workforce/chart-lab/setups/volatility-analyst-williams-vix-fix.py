"""Williams VIX Fix capitulation spike on 5-minute bars.
Added 2026-10-11 by volatility-analyst via WebSearch (LuxAlgo "Williams VIX Fix", ProRealCode and the widely reused
ChrisMoody TradingView script). Larry Williams' formula: WVF = (highest close of 22 bars - current low) / highest
close * 100; a bottom is flagged when WVF is above its own Bollinger upper band (20 bars, 2 sd) or above 85% of its
highest value over the last 50 bars. The sources only discuss daily bars; the top-flagging mirror
((current high - lowest close of 22 bars) / lowest close) is a community inversion. Untested intraday adaptation.
Parameters fixed BEFORE any P&L was seen: the classic 22 / 20 / 2.0 / 50 / 0.85, computed inside the session only,
so the first signal is possible after about 13:00 ET (42 bars of warm-up). One signal per side per session.
"""


def _spikes(wvf):
    n = len(wvf)
    out = [False] * n
    for i in range(41, n):
        seg = wvf[i - 19:i + 1]
        m = sum(seg) / 20
        sd = (sum((x - m) ** 2 for x in seg) / 20) ** 0.5
        top50 = max(wvf[max(0, i - 49):i + 1])
        out[i] = wvf[i] >= m + 2 * sd or wvf[i] >= 0.85 * top50
        if wvf[i] <= 0:
            out[i] = False
    return out


def williams_vix_fix(s):
    b = s.bars
    n = len(b)
    if n < 43:
        return
    bot, top = [0.0] * n, [0.0] * n
    for i in range(21, n):
        hc = max(x.c for x in b[i - 21:i + 1])
        lc = min(x.c for x in b[i - 21:i + 1])
        bot[i] = (hc - b[i].l) / hc * 100 if hc else 0.0
        top[i] = (b[i].h - lc) / lc * 100 if lc else 0.0
    sb, st = _spikes(bot), _spikes(top)
    seen_long = seen_short = False
    for i in range(42, n - 1):
        if b[i].m >= 900:
            break
        if sb[i] and not seen_long:
            seen_long = True
            yield i, 1
        if st[i] and not seen_short:
            seen_short = True
            yield i, -1


SETUPS = [
    dict(id='williams_vix_fix', name='Williams VIX Fix capitulation spike', family='volatility',
         detect=williams_vix_fix,
         rules="Measure how far the 5-minute low has fallen below the highest close of the last 22 bars (Larry "
               "Williams' VIX Fix). When that drop jumps above its own Bollinger band (20 bars, 2 sd) or above 85% "
               "of its 50-bar high, the selling looks like a capitulation low: lean long; the mirror (high far above "
               "the lowest close of 22 bars) leans short. One signal per side per session, only after about 13:00 "
               "ET when enough bars exist; tested with and against."),
]
