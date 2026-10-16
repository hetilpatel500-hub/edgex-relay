"""Heikin Ashi trend candles on the VWAP side.
Added 2026-10-01 by trend-moving-average-analyst: the research queue's non-tape
lines are all coded, so this run used WebSearch (liberatedstocktrader.com VWAP
test, avatrade/quantifiedstrategies Heikin Ashi guides) for a documented,
untested idea: a Heikin Ashi "strong trend" candle (no wick on the trend side)
on the right side of VWAP. Rules fixed before any P&L was seen.
"""


def heikin_ashi_vwap(s):
    """Heikin Ashi bars are built inside the session (ha_close = OHLC/4,
    ha_open = midpoint of the prior HA bar). Two consecutive HA bars of the same
    colour, the latest with no wick on the trend side (green with ha_low == ha_open,
    red with ha_high == ha_open), and the close on the same side of VWAP, start a
    trend signal. One signal per side per session, 10:00 to 14:30 ET."""
    b = s.bars
    ho = hc = None
    ha = []
    for i, x in enumerate(b):
        c = (x.o + x.h + x.l + x.c) / 4
        o = (x.o + x.c) / 2 if ho is None else (ho + hc) / 2
        ha.append((o, max(x.h, o, c), min(x.l, o, c), c))
        ho, hc = o, c
    fired = set()
    for i in range(1, len(b)):
        if b[i].m < 600 or b[i].m >= 870:
            continue
        o, h, l, c = ha[i]
        po, _, _, pc = ha[i - 1]
        tol = 1e-9 * max(1.0, abs(o))
        if c > o and pc > po and abs(l - o) <= tol and b[i].c > s.vwap[i] and 1 not in fired:
            fired.add(1); yield i, 1
        elif c < o and pc < po and abs(h - o) <= tol and b[i].c < s.vwap[i] and -1 not in fired:
            fired.add(-1); yield i, -1


SETUPS = [
    dict(id='heikin_ashi_vwap', name='Heikin Ashi trend candle on the VWAP side', family='trend', detect=heikin_ashi_vwap,
         rules="Two Heikin Ashi 5-minute candles in a row of the same colour, the latest with no wick on the trend "
               "side (green with a flat bottom, red with a flat top), and price closing on the same side of VWAP: "
               "leans with the trend. From 10:00 to 14:30 ET, one signal per side per session."),
]
