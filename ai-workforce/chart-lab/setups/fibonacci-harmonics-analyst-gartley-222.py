"""Gartley (222) harmonic completion on 5-minute bars.
Added 2026-10-14 by fibonacci-harmonics-analyst via WebSearch (tradejini.com and luxalgo.com primers on the Gartley 222
pattern; H.M. Gartley 1935, ratios from later harmonic-pattern authors, so the ratios here are one common reading, not
canon). Not yet tested here; distinct from abcd_completion (equal legs only, no XA anchor) and fib618_opening_drive.
Parameters fixed BEFORE any P&L was seen: 2-bar fractal pivots confirmed two bars later (same as core structure); four
alternating pivots X, A, B, C; XA at least 1.5 ATR(5-min); B retraces 0.568-0.668 of XA (0.618 +/- 0.05); C retraces
0.382-0.886 of AB; D is the 0.786 retracement of XA. Signal at the close of the first bar whose range reaches D while
no bar since C has traded beyond X, leaning against the CD leg, before 15:00, one per side per session. Only pivots
confirmed by the signal bar are used.
"""


def gartley(s):
    b = s.bars
    n = len(b)
    piv = []
    fired = {1: False, -1: False}
    for i in range(4, n):
        if b[i].m >= 900:
            return
        k = i - 2
        if k >= 2:
            if all(b[k].h > b[j].h for j in (k - 2, k - 1, k + 1, k + 2)):
                piv.append((k, b[k].h, 'H'))
            if all(b[k].l < b[j].l for j in (k - 2, k - 1, k + 1, k + 2)):
                piv.append((k, b[k].l, 'L'))
        piv.sort()
        if len(piv) < 4 or not s.atr[i]:
            continue
        (kx, x, tx), (ka, a, ta), (kb, bb, tb), (kc, c, tc) = piv[-4:]
        if not (tx == tb and ta == tc and tx != ta):
            continue
        xa = abs(a - x)
        if xa < 1.5 * s.atr[i]:
            continue
        ab = abs(a - bb)
        bc = abs(c - bb)
        if not (0.568 * xa <= ab <= 0.668 * xa) or not (0.382 * ab <= bc <= 0.886 * ab):
            continue
        rest = b[kc + 1:i]
        if tx == 'L':              # bullish: X low, A high, B low, C high, D = A - 0.786 XA
            if c >= a or bb <= x:
                continue
            d_px = a - 0.786 * xa
            if not fired[1] and rest and b[i].l <= d_px and min(y.l for y in rest) > d_px and b[i].l > x:
                fired[1] = True
                yield i, 1
        else:                      # bearish: X high, A low, B high, C low, D = A + 0.786 XA
            if c <= a or bb >= x:
                continue
            d_px = a + 0.786 * xa
            if not fired[-1] and rest and b[i].h >= d_px and max(y.h for y in rest) < d_px and b[i].h < x:
                fired[-1] = True
                yield i, -1


SETUPS = [
    dict(id='gartley_222', name='Gartley 222 completion at 0.786 of XA', family='fibonacci',
         detect=gartley,
         rules="Four alternating swing pivots X, A, B, C with XA at least 1.5 ATR, B retracing 0.618 of XA (within 0.05) "
               "and C retracing 38.2-88.6% of AB. Point D is the 0.786 retracement of XA. At the close of the first "
               "bar to reach D without trading beyond X, lean against the CD leg (long at a bullish D, short at a "
               "bearish D), before 15:00. One per side per session."),
]
