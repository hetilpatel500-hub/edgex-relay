"""Symmetrical triangle breakout on 5-minute bars.
Added 2026-10-05 by pattern-specialist: classic triangles, from the pattern
family of the research queue (WebSearch: a symmetrical triangle is two
converging trendlines each touching at least two highs and lows, and the
break counts on a close, ideally with volume expansion). Two lower swing
highs and two higher swing lows (2-bar swings, confirmed two bars late)
inside the last 36 bars, the lines at least 8 bars wide apart at the first
swing and converging. A close beyond the projected line by 0.1 ATR on a bar
whose volume is at least 1.5x the average of the previous 10 bars leans with
the break, once per session, before 15:00.
"""


def _line(p1, p2, x):
    (x1, y1), (x2, y2) = p1, p2
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)


def triangle_break(s):
    b = s.bars
    n = len(b)
    sh, sl = [], []
    for i in range(12, n):
        if b[i].m >= 900:
            return
        k = i - 2
        if all(b[k].h > b[j].h for j in (k - 2, k - 1, k + 1, k + 2)):
            sh.append((k, b[k].h))
        if all(b[k].l < b[j].l for j in (k - 2, k - 1, k + 1, k + 2)):
            sl.append((k, b[k].l))
        atr = s.atr[i]
        if len(sh) < 2 or len(sl) < 2 or not atr or i < 10:
            continue
        h1, h2 = sh[-2], sh[-1]
        l1, l2 = sl[-2], sl[-1]
        if i - min(h1[0], l1[0]) > 36 or h2[1] >= h1[1] or l2[1] <= l1[1]:
            continue
        if h2[0] == h1[0] or l2[0] == l1[0]:
            continue
        first = min(h1[0], l1[0])
        up0, lo0 = _line(h1, h2, first), _line(l1, l2, first)
        up_i, lo_i = _line(h1, h2, i), _line(l1, l2, i)
        if up0 - lo0 < 0.5 * atr or up_i - lo_i >= up0 - lo0 or up_i <= lo_i:
            continue
        vavg = sum(x.v for x in b[i - 10:i]) / 10.0
        if vavg <= 0 or b[i].v < 1.5 * vavg:
            continue
        if b[i].c > up_i + 0.1 * atr:
            yield i, 1
            return
        if b[i].c < lo_i - 0.1 * atr:
            yield i, -1
            return


SETUPS = [
    dict(id='symmetrical_triangle_break', name='Symmetrical triangle breakout on volume', family='pattern',
         detect=triangle_break,
         rules="Two lower swing highs and two higher swing lows (converging lines, at least 0.5 ATR wide at the "
               "first swing, within the last 36 bars) form a symmetrical triangle. The first close beyond the "
               "projected line by 0.1 ATR on a bar with at least 1.5x the previous 10 bars' average volume leans "
               "with the break, once per session, before 15:00."),
]
