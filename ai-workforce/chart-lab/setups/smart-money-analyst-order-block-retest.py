"""Order block: last opposite candle before a displacement, first retest.
Added 2026-10-12 by smart-money-analyst: smart-money family, next open line of
the research queue in ai-workforce/chart-lab/README.md.
"""


def order_block_retest(s):
    """A displacement is one bar whose body is at least 1.2 ATR with a close in
    the top (bottom) 25% of its range. The order block is the last opposite-colour
    bar before it (a red bar before a bullish displacement). The first later bar
    within 15 bars that trades into the block's body without closing through
    its far side, and closes in the displacement direction, leans with the
    displacement. A close through the block voids it. Judged at that bar's close."""
    b = s.bars
    fired = 0
    for i in range(2, len(b)):
        if b[i].m >= 900 or fired >= 3:
            break
        atr = s.atr[i]
        if not atr:
            continue
        rng = b[i].h - b[i].l
        body = b[i].c - b[i].o
        if rng <= 0 or abs(body) < 1.2 * atr:
            continue
        d = 1 if body > 0 else -1
        if d == 1 and b[i].c < b[i].h - 0.25 * rng:
            continue
        if d == -1 and b[i].c > b[i].l + 0.25 * rng:
            continue
        k = None
        for q in range(i - 1, max(i - 6, -1), -1):
            if (b[q].c < b[q].o) if d == 1 else (b[q].c > b[q].o):
                k = q
                break
        if k is None:
            continue
        top, bot = max(b[k].o, b[k].c), min(b[k].o, b[k].c)
        for j in range(i + 1, min(i + 16, len(b))):
            if b[j].m >= 900:
                break
            if d == 1:
                if b[j].c < bot:
                    break
                if b[j].l <= top:
                    if b[j].c > b[j].o:
                        fired += 1; yield j, 1
                    break
            else:
                if b[j].c > top:
                    break
                if b[j].h >= bot:
                    if b[j].c < b[j].o:
                        fired += 1; yield j, -1
                    break


SETUPS = [
    dict(id='order_block_retest', name='Order block first retest', family='smart-money',
         detect=order_block_retest,
         rules="A displacement bar (body at least 1.2 ATR, closing in the outer quarter of its range) "
               "marks the last opposite-colour bar before it (within 5 bars) as the order block. The first "
               "bar within 15 bars that trades back into the block's body, does not close through it, and "
               "closes in the displacement direction leans with the displacement; a close through the "
               "block voids it. Before 15:00."),
]
