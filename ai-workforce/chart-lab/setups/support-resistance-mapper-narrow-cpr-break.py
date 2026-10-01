"""Narrow Central Pivot Range (CPR) breakout on 5-minute bars.
Added 2026-10-01 by support-resistance-mapper: the research queue's lines are
all coded, so this run used WebSearch (CPR rules summarised by choiceindia.com,
quantzee.com, optionx.trade: a narrow CPR hints at a trend day; trade the
break of TC/BC after the first 15 minutes, with volume). Levels use yesterday's
high/low/close only. Parameters (width <= 0.15 x prior range, rvol >= 1) were
fixed before testing and are not tuned.
"""


def narrow_cpr_break(s):
    """Pivot P=(H+L+C)/3, BC=(H+L)/2, TC=2P-BC. If |TC-BC| <= 0.15 x yesterday's
    range, the first 5-minute close above max(TC,BC) (long) or below
    min(TC,BC) (short) between 09:45 and 14:30 with relative volume >= 1
    fires. One signal per session."""
    p = s.prior
    if p is None:
        return
    r = p.hi - p.lo
    if r <= 0:
        return
    piv = (p.hi + p.lo + p.close) / 3
    bc = (p.hi + p.lo) / 2
    tc = 2 * piv - bc
    top, bot = max(tc, bc), min(tc, bc)
    if top - bot > 0.15 * r:
        return
    for i in range(3, len(s.bars)):
        b = s.bars[i]
        if b.m >= 870:
            return
        if s.rvol[i] is None or s.rvol[i] < 1:
            continue
        if b.c > top and s.bars[i - 1].c <= top:
            yield i, 1
            return
        if b.c < bot and s.bars[i - 1].c >= bot:
            yield i, -1
            return


SETUPS = [
    dict(id='narrow_cpr_break', name='Narrow CPR breakout', family='levels',
         detect=narrow_cpr_break,
         rules="When yesterday's central pivot range (BC to TC) is under 15% of yesterday's range, the first "
               "5-minute close through the top (long) or bottom (short) of that range, 09:45-14:30, on "
               "at-least-normal relative volume leans in the break's direction."),
]
