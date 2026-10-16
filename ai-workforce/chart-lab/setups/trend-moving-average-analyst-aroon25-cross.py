"""Aroon(25) crossover on 5-minute bars (Chande's Aroon, documented intraday use at 25 periods).
Added 2026-10-02 by trend-moving-average-analyst: the research queue held only tape items, so this run took
Aroon-25 from public indicator-backtest write-ups (liberatedstocktrader.com, tradingsim.com). Rules fixed BEFORE
any P&L was seen: period 25 on 5-minute bars inside one session, Aroon Up crossing above Aroon Down is long,
the reverse is short, one signal per session. Distinct from the EMA crossover, supertrend and Donchian setups
(Aroon times the age of the extreme, not its price).
"""

PERIOD = 25


def aroon25_cross(s):
    """Aroon Up = 100*(25 - bars since the highest high of the last 26 bars)/25, Aroon Down likewise for lows.
    Between bar 26 (about 11:40) and 15:00, the first bar whose Aroon Up crosses above Aroon Down is long; whose
    Aroon Down crosses above Aroon Up is short. One signal per session."""
    b = s.bars
    prev = None
    for i in range(PERIOD, len(b)):
        if b[i].m >= 900:
            break
        w = b[i - PERIOD:i + 1]
        hi = max(x.h for x in w)
        lo = min(x.l for x in w)
        # most recent bar holding the extreme
        since_hi = next(PERIOD - k for k in range(PERIOD, -1, -1) if w[k].h == hi)
        since_lo = next(PERIOD - k for k in range(PERIOD, -1, -1) if w[k].l == lo)
        up = 100.0 * (PERIOD - since_hi) / PERIOD
        dn = 100.0 * (PERIOD - since_lo) / PERIOD
        osc = up - dn
        if prev is not None:
            if prev <= 0 < osc:
                yield i, 1
                return
            if prev >= 0 > osc:
                yield i, -1
                return
        prev = osc


SETUPS = [
    dict(id='aroon25_cross', name='Aroon(25) crossover', family='trend',
         detect=aroon25_cross,
         rules="On 5-minute bars, Aroon Up (how recently the highest high of the last 25 bars printed) crossing above "
               "Aroon Down (how recently the lowest low printed) is a long signal; the reverse is a short. "
               "Only counted from about 11:40 (25 bars into the session) to 15:00, once per session."),
]
