"""Break and retest of yesterday's high / low on 5-minute bars.
Added 2026-09-29 by support-resistance-mapper: a level-break idea not yet
tested (pd_sweep is the failed-break version). Rules and parameters were
fixed before testing: retest window 12 bars, touch tolerance 0.1 ATR.
"""


def pd_break_retest(s):
    """A 5-minute close beyond yesterday's high (low), then within the next
    12 bars a bar whose low (high) comes within 0.1 ATR of that level and
    closes back on the breakout side. Signal on the retest bar, 09:40-14:30,
    one per direction per session."""
    p = s.prior
    if p is None:
        return
    b = s.bars
    for level, d in ((p.hi, 1), (p.lo, -1)):
        brk = None
        for i in range(1, len(b)):
            if b[i].m >= 870:
                break
            if brk is None:
                if d * (b[i].c - level) > 0:
                    brk = i
                continue
            if i - brk > 12:
                break
            atr = s.atr[i]
            if not atr:
                continue
            if d == 1 and b[i].l <= level + 0.1 * atr and b[i].c > level:
                yield i, 1
                break
            if d == -1 and b[i].h >= level - 0.1 * atr and b[i].c < level:
                yield i, -1
                break
            if d * (b[i].c - level) < 0:
                break


SETUPS = [
    dict(id='pd_break_retest', name="Break and retest of yesterday's high/low", family='levels',
         detect=pd_break_retest,
         rules="A 5-minute close beyond yesterday's high (low), then within 12 bars a pullback that "
               "trades within 0.1 ATR of that level and closes back on the breakout side, before 14:30, "
               "leans in the breakout direction."),
]
