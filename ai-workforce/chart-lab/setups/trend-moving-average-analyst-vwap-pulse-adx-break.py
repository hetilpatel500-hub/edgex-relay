"""VWAP Pulse Breakout: VWAP cross confirmed by ADX and a 6-bar range break, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (TradingView idea "VWAP Pulse Breakout, a clean
intraday strategy using VWAP + ADX": long needs a close above VWAP with ADX above 20; the author gives no verified
backtest). The source also uses Stochastic RSI; that part is left out because stochrsi_trend_cross already covers it.
Parameters fixed BEFORE any P&L was seen: ADX(14, Wilder) restarted each session; the signal bar closes across
session VWAP (previous close on the other side), ADX >= 20 and rising versus the previous bar, and the close is
beyond the highest high (lowest low) of the prior 6 bars; 10:30-14:30 ET; one signal per session.
"""


def _adx(b, n=14):
    out = [None] * len(b)
    tr_s = pdm_s = ndm_s = 0.0
    dx = []
    for i in range(1, len(b)):
        up, dn = b[i].h - b[i - 1].h, b[i - 1].l - b[i].l
        pdm = up if up > dn and up > 0 else 0.0
        ndm = dn if dn > up and dn > 0 else 0.0
        tr = max(b[i].h - b[i].l, abs(b[i].h - b[i - 1].c), abs(b[i].l - b[i - 1].c))
        if i <= n:
            tr_s += tr; pdm_s += pdm; ndm_s += ndm
        else:
            tr_s = tr_s - tr_s / n + tr
            pdm_s = pdm_s - pdm_s / n + pdm
            ndm_s = ndm_s - ndm_s / n + ndm
        if i >= n and tr_s > 0:
            pdi, ndi = 100 * pdm_s / tr_s, 100 * ndm_s / tr_s
            dx.append(100 * abs(pdi - ndi) / (pdi + ndi) if pdi + ndi else 0.0)
            if len(dx) == n:
                out[i] = sum(dx) / n
            elif len(dx) > n:
                out[i] = (out[i - 1] * (n - 1) + dx[-1]) / n
    return out


def vwap_pulse_adx_break(s):
    b = s.bars
    adx = _adx(b)
    for i in range(30, len(b) - 1):
        x = b[i]
        if x.m < 630 or x.m > 870 or adx[i] is None or adx[i - 1] is None:
            continue
        if adx[i] < 20 or adx[i] <= adx[i - 1]:
            continue
        hh = max(y.h for y in b[i - 6:i])
        ll = min(y.l for y in b[i - 6:i])
        if b[i - 1].c <= s.vwap[i - 1] and x.c > s.vwap[i] and x.c > hh:
            yield i, 1
            return
        if b[i - 1].c >= s.vwap[i - 1] and x.c < s.vwap[i] and x.c < ll:
            yield i, -1
            return


SETUPS = [
    dict(id='vwap_pulse_adx_break', name='VWAP cross with ADX and a 6-bar range break', family='trend',
         detect=vwap_pulse_adx_break,
         rules="Between 10:30 and 14:30 ET, a 5-minute bar that closes across session VWAP (the bar before was on "
               "the other side), with ADX(14) at or above 20 and rising, and that closes beyond the highest high "
               "(long) or lowest low (short) of the prior 6 bars. One signal per session; tested with and against."),
]
