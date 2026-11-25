"""Camarilla pivots H3/L3 reversal and H4/L4 breakout on 5-minute bars.
Added 2026-09-29 by support-resistance-mapper: the research queue's non-tape
lines are coded, so this run used WebSearch (Camarilla rules summarised by
onetradingmarkets.com, arongroups.co, litefinance.org). Levels come from
yesterday's high/low/close only: H3/L3 = close +/- 1.1 * range / 4, H4/L4 =
close +/- 1.1 * range / 2. Distinct from pivot_bounce (classic pivots).
"""


def _levels(s):
    p = s.prior
    if p is None:
        return None
    r = p.hi - p.lo
    if r <= 0:
        return None
    c = p.close
    return c + 1.1 * r / 4, c - 1.1 * r / 4, c + 1.1 * r / 2, c - 1.1 * r / 2


def camarilla_h3l3_fade(s):
    """A bar trades through H3 (or L3) but closes back inside it, between
    09:40 and 15:00: short at H3, long at L3. One signal per session."""
    lv = _levels(s)
    if not lv:
        return
    h3, l3, h4, l4 = lv
    for i in range(1, len(s.bars)):
        b = s.bars[i]
        if b.m >= 900:
            return
        if b.h >= h3 and b.c < h3 and b.h < h4:
            yield i, -1
            return
        if b.l <= l3 and b.c > l3 and b.l > l4:
            yield i, 1
            return


def camarilla_h4l4_break(s):
    """A 5-minute close beyond H4 (long) or below L4 (short) between 09:40
    and 14:30. One signal per session."""
    lv = _levels(s)
    if not lv:
        return
    h3, l3, h4, l4 = lv
    for i in range(1, len(s.bars)):
        b = s.bars[i]
        if b.m >= 870:
            return
        if b.c > h4:
            yield i, 1
            return
        if b.c < l4:
            yield i, -1
            return


SETUPS = [
    dict(id='camarilla_h3l3_fade', name='Camarilla H3/L3 reversal', family='levels',
         detect=camarilla_h3l3_fade,
         rules="Yesterday's Camarilla H3 = close + 1.1 x range / 4 (L3 the mirror). A 5-minute bar that "
               "trades through H3 but closes back below it, without reaching H4, leans short; through L3 "
               "and back above, without reaching L4, leans long. Before 15:00."),
    dict(id='camarilla_h4l4_break', name='Camarilla H4/L4 breakout', family='levels',
         detect=camarilla_h4l4_break,
         rules="Yesterday's Camarilla H4 = close + 1.1 x range / 2 (L4 the mirror). A 5-minute close "
               "beyond H4 leans long, below L4 leans short, before 14:30."),
]
