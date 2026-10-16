"""Three white soldiers / three black crows on 5-minute bars.
Added 2026-10-06 by candlestick-specialist: classic Nison three-candle continuation pattern; the README
queue is fully coded, so this took a documented pattern the lab had not tested. Rules fixed BEFORE any P&L
was seen: three consecutive same-colour 5-minute bodies each at least 60% of the bar's range, each close
beyond the previous close and in the outer 25% of its bar, each open inside the previous body. Signal at
the third bar's close between 10:00 and 15:00 ET. One signal per session.
"""


def three_soldiers_crows(s):
    """Three strong same-direction 5-minute candles in a row, each opening inside the prior body and
    closing near its extreme; signals in the pattern's direction at the third close (10:00-15:00 ET)."""
    b = s.bars
    for i in range(2, len(b)):
        if not (600 <= b[i].m < 900):
            continue
        for d in (1, -1):
            ok = True
            for k in (i - 2, i - 1, i):
                x = b[k]
                rng = x.h - x.l
                if rng <= 0 or d * (x.c - x.o) < 0.6 * rng:
                    ok = False; break
                near = (x.c - x.l) / rng if d == 1 else (x.h - x.c) / rng
                if near < 0.75:
                    ok = False; break
            if not ok:
                continue
            for k in (i - 1, i):
                p, x = b[k - 1], b[k]
                lo, hi = min(p.o, p.c), max(p.o, p.c)
                if not (lo <= x.o <= hi) or d * (x.c - p.c) <= 0:
                    ok = False; break
            if ok:
                yield i, d
                return


SETUPS = [
    dict(id='three_soldiers_crows', name='Three white soldiers / three black crows (5-min)', family='candlestick',
         detect=three_soldiers_crows,
         rules="Three consecutive 5-minute candles of the same colour, each with a body of at least 60% of its range, "
               "each closing in the outer 25% of its range and beyond the previous close, and each opening inside the "
               "previous body. Signals in the pattern's direction at the third close, 10:00-15:00 ET. One per session."),
]
