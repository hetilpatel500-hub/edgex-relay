"""SPY-led initial balance break: the stock's own IB break that comes after SPY's, in the same direction.
Added 2026-10-07 by smart-money-analyst via WebSearch on market-alignment ORB guides (trade the breakout only when
the index has already broken out). Distinct from ib_break (stock alone) and rel_strength_spy (return gap, no IB).
Parameters fixed BEFORE any P&L was seen: IB = first 60 minutes (bars 0-11). Look at bars 12-50 (10:30-13:40 ET).
SPY must have closed beyond its own IB at an earlier bar than the stock; the signal is the stock's first close
beyond its own IB in that same direction, on a bar where SPY's close is still beyond its IB. One signal per
session. SPY itself is skipped.
"""
import core

_spy = {}


def _spy_day(day):
    if not _spy:
        for x in core.sessions('SPY'):
            _spy[x.day] = x
    return _spy.get(day)


def spy_led_ib_break(s):
    if s.sym == 'SPY':
        return
    p = _spy_day(s.day)
    if p is None:
        return
    b, pb = s.bars, p.bars
    spy_first = {}
    for i in range(12, min(51, len(b), len(pb))):
        if pb[i].c > p.ib_hi and 1 not in spy_first:
            spy_first[1] = i
        if pb[i].c < p.ib_lo and -1 not in spy_first:
            spy_first[-1] = i
        d = 1 if b[i].c > s.ib_hi else -1 if b[i].c < s.ib_lo else 0
        if not d:
            continue
        if d in spy_first and spy_first[d] < i and (pb[i].c - (p.ib_hi if d == 1 else p.ib_lo)) * d > 0:
            yield i, d
        return


SETUPS = [
    dict(id='spy_led_ib_break', name='SPY-led initial balance break', family='smart-money',
         detect=spy_led_ib_break,
         rules="Between 10:30 and 13:40, a stock closes beyond its first-hour range (initial balance) after SPY has "
               "already closed beyond its own first-hour range in the same direction, and SPY is still beyond it. "
               "The stock's first IB break of the session is the only candidate (if SPY hasn't led, no signal); "
               "tested with and against. SPY itself is skipped."),
]
