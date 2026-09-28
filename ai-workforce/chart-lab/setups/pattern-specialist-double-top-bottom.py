"""Double top / double bottom at a prior-day level.
Added 2026-09-28 by pattern-specialist: next open line of the research queue
in ai-workforce/chart-lab/README.md ("Double top/bottom at a prior-day
level"). Two confirmed swing highs (lows) both within 0.3 ATR of yesterday's
high (low), the second no more than 0.1 ATR above (below) the first: the
level rejected the probe twice. The first close back through the low
(high) between the two peaks (troughs) -- the neckline -- confirms the
pattern and leans against the level, before 15:00.
"""


def double_top_bottom(s):
    b = s.bars
    p = s.prior
    if p is None:
        return
    n = len(b)
    top1 = top2 = bot1 = bot2 = None
    neck_hi = neck_lo = None
    fired_top = fired_bot = False
    for i in range(4, n):
        if b[i].m >= 900:
            return
        k = i - 2
        if k < 2 or k + 2 >= n:
            continue
        atr = s.atr[k]
        if not atr:
            continue
        is_sh = all(b[k].h > b[j].h for j in (k - 2, k - 1, k + 1, k + 2))
        is_sl = all(b[k].l < b[j].l for j in (k - 2, k - 1, k + 1, k + 2))
        if is_sh and abs(b[k].h - p.hi) <= 0.3 * atr:
            if top1 is None:
                top1 = (k, b[k].h)
            elif top2 is None and b[k].h <= top1[1] + 0.1 * atr and k > top1[0]:
                neck_hi = min(x.l for x in b[top1[0]:k + 1])
                top2 = (k, b[k].h)
        if is_sl and abs(b[k].l - p.lo) <= 0.3 * atr:
            if bot1 is None:
                bot1 = (k, b[k].l)
            elif bot2 is None and b[k].l >= bot1[1] - 0.1 * atr and k > bot1[0]:
                neck_lo = max(x.h for x in b[bot1[0]:k + 1])
                bot2 = (k, b[k].l)
        if not fired_top and top2 is not None and b[i].c < neck_hi:
            fired_top = True
            yield i, -1
        if not fired_bot and bot2 is not None and b[i].c > neck_lo:
            fired_bot = True
            yield i, 1


SETUPS = [
    dict(id='double_top_bottom', name='Double top / bottom at a prior-day level', family='pattern',
         detect=double_top_bottom,
         rules="Two confirmed swing highs (lows) both within 0.3 ATR of yesterday's high (low), the second no "
               "more than 0.1 ATR above (below) the first, mark a double top (bottom) at that level. The first "
               "close back through the low (high) between the two peaks (troughs) confirms it and leans against "
               "the level, before 15:00."),
]
