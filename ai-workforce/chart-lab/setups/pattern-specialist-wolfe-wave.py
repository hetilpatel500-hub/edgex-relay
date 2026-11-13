"""Wolfe wave: point 5 overshoots the 1-3 line, first close back inside.
Added 2026-10-15 by pattern-specialist via Bill Wolfe's published rules (point 3 beyond point 1, point 4
inside the 1-2 / 3 channel, point 5 pokes through the 1-3 line); no Wolfe wave detector is in the lab yet.
Parameters fixed BEFORE any P&L was seen: 2-bar pivots, point 3 at least 0.3 ATR beyond point 1, point 4
between points 1 and 2, wave height (2 to 3) at least 1 ATR, point 5 at least 0.1 ATR through the 1-3 line.
The lab tests it with and against.
"""


def wolfe(s):
    """Alternating 5-minute pivots (2 bars each side, known 2 bars later). Bullish: 1 low, 2 high, 3 low
    below 1 by 0.3 ATR or more, 4 high below 2 and above 1, 5 low that sits at least 0.1 ATR under the line
    through 1 and 3 extended to its bar; the first close back above that line, within 6 bars of point 5's
    confirmation, is the signal (long). Bearish mirrors it. 10:00 to 14:30 ET, one per side per session."""
    b = s.bars
    n = len(b)
    pv = []                              # (index, price, +1 high / -1 low), alternating
    done = set()
    for i in range(2, n):
        k = i - 2
        if k >= 2:
            ish = b[k].h > max(x.h for x in b[k - 2:k]) and b[k].h > max(x.h for x in b[k + 1:k + 3])
            isl = b[k].l < min(x.l for x in b[k - 2:k]) and b[k].l < min(x.l for x in b[k + 1:k + 3])
            if ish != isl:
                t = 1 if ish else -1
                p = b[k].h if ish else b[k].l
                if pv and pv[-1][2] == t:
                    if (t == 1 and p > pv[-1][1]) or (t == -1 and p < pv[-1][1]):
                        pv[-1] = (k, p, t)
                else:
                    pv.append((k, p, t))
        a = s.atr[i]
        if not a or b[i].m < 600 or b[i].m > 870 or len(pv) < 5:
            continue
        k1, p1, t1 = pv[-5]
        k2, p2, _ = pv[-4]
        k3, p3, _ = pv[-3]
        k4, p4, _ = pv[-2]
        k5, p5, _ = pv[-1]
        d = -t1                          # first point a low (t1 -1) -> long
        if d in done or i - k5 > 2 + 6:
            continue
        if d == 1:
            ok = p1 - p3 >= 0.3 * a and p1 < p4 < p2 and p2 - p3 >= a
        else:
            ok = p3 - p1 >= 0.3 * a and p2 < p4 < p1 and p3 - p2 >= a
        if not ok or k3 == k1:
            continue
        slope = (p3 - p1) / (k3 - k1)
        line5 = p1 + slope * (k5 - k1)
        linei = p1 + slope * (i - k1)
        if d == 1:
            ok = p5 <= line5 - 0.1 * a and b[i].c > linei and b[i - 1].c <= p1 + slope * (i - 1 - k1)
        else:
            ok = p5 >= line5 + 0.1 * a and b[i].c < linei and b[i - 1].c >= p1 + slope * (i - 1 - k1)
        if ok:
            done.add(d)
            yield i, d


SETUPS = [
    dict(id='wolfe_wave', name='Wolfe wave: point 5 through the 1-3 line, close back inside', family='pattern',
         detect=wolfe,
         rules="Five alternating 5-minute pivots; for a bullish wave: 1 low, 2 high, 3 low at least 0.3 ATR below "
               "1, 4 high between 1 and 2, wave height 2 to 3 at least 1 ATR, point 5 low at least 0.1 ATR under "
               "the 1-3 line projected to its bar. The first close back above that line within 6 bars of point 5's "
               "confirmation is the signal; the bearish wave mirrors it. 10:00 to 14:30 ET, one per side per "
               "session. Tested with and against."),
]
