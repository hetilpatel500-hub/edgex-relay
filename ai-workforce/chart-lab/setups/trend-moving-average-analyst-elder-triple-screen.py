"""Elder Triple Screen on 5-minute bars.
Added 2026-10-05 by trend-moving-average-analyst: the research queue had no open
non-tape lines, so this tests Alexander Elder's Triple Screen (Trading for a
Living, 1993): screen 1 the slower-timeframe trend, screen 2 a Force Index(2)
counter-trend dip, screen 3 a breakout of the prior bar in the trend direction.
Parameters (EMA 5 of prior daily closes, Force Index EMA 2, 10:00-14:30) were
fixed before any P&L was seen. The book's 13-day EMA needs 26 chained sessions and the stored
bars chain at most 19, so the first run produced zero signals; the EMA was shortened to 5 days
(10 chained sessions) with no P&L having been seen.
"""


def _daily_ema_slope(s, n=5):
    """+1 / -1 / 0: slope of the EMA(5) of chained prior-session closes (last
    value vs the one before it). 0 when fewer than 2n sessions are chained."""
    closes, p = [], s.prior
    while p is not None and len(closes) < 2 * n:
        closes.append(p.close)
        p = p.prior
    if len(closes) < 2 * n:
        return 0
    closes.reverse()
    k = 2 / (n + 1)
    e = sum(closes[:n]) / n
    prev = e
    for c in closes[n:]:
        prev = e
        e = c * k + e * (1 - k)
    return 1 if e > prev else (-1 if e < prev else 0)


def elder_triple_screen(s):
    """Screen 1: daily EMA(5) slope up (down). Screen 2: the 2-bar EMA of Force
    Index (close change x volume) was below (above) zero on the prior bar.
    Screen 3: this bar closes above the prior bar's high (below its low). One
    signal per session, 10:00 to 14:30."""
    d = _daily_ema_slope(s)
    if d == 0:
        return
    b = s.bars
    k = 2 / 3
    fi = None
    fis = [0.0]
    for i in range(1, len(b)):
        raw = (b[i].c - b[i - 1].c) * b[i].v
        fi = raw if fi is None else raw * k + fi * (1 - k)
        fis.append(fi)
    for i in range(7, len(b)):
        if b[i].m >= 870:
            break
        if b[i].m < 600:
            continue
        if d == 1 and fis[i - 1] < 0 and b[i].c > b[i - 1].h:
            yield i, 1
            return
        if d == -1 and fis[i - 1] > 0 and b[i].c < b[i - 1].l:
            yield i, -1
            return


SETUPS = [
    dict(id='elder_triple_screen', name='Elder Triple Screen (daily trend, Force Index dip, bar break)', family='trend',
         detect=elder_triple_screen,
         rules="When the 5-day EMA of prior daily closes slopes up (down), wait for the 2-bar Force Index to be "
               "negative (positive) on the prior bar, then lean with the daily trend on the first bar that closes "
               "above the prior bar's high (below its low). One signal per session, 10:00 to 14:30."),
]
