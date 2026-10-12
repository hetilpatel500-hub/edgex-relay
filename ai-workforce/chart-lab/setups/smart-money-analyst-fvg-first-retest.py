"""Fair value gap (3-bar imbalance) first retest.
Added 2026-10-12 by smart-money-analyst: smart-money family, next open line of
the research queue in ai-workforce/chart-lab/README.md.
"""


def fvg_first_retest(s):
    """A bullish gap exists when bar i's low is above the high of bar i-2 (the
    middle bar was a displacement); bearish is the mirror. The gap must be at
    least 0.3 ATR wide. The first later bar (within 12 bars) whose range
    trades back into the gap, and which closes on the gap's far side from the
    fill (bullish: close >= gap bottom and above the bar's open-side, i.e. holds
    inside or above the gap), leans with the original displacement. Gaps are
    only known after bar i closes; the retest is judged at its own close."""
    b = s.bars
    fired = 0
    for i in range(2, len(b)):
        if b[i].m >= 900 or fired >= 3:
            break
        atr = s.atr[i]
        if not atr:
            continue
        for d in (1, -1):
            if d == 1:
                top, bot = b[i].l, b[i - 2].h
            else:
                top, bot = b[i - 2].l, b[i].h
            if d == 1 and not top > bot:
                continue
            if d == -1 and not top > bot:
                continue
            if top - bot < 0.3 * atr:
                continue
            for j in range(i + 1, min(i + 13, len(b))):
                if b[j].m >= 900:
                    break
                if d == 1:
                    if b[j].l < bot:
                        break  # gap fully filled: invalid
                    if b[j].l <= top:
                        if b[j].c > bot and b[j].c > b[j].o:
                            fired += 1; yield j, 1
                        break
                else:
                    if b[j].h > top:
                        break
                    if b[j].h >= bot:
                        if b[j].c < top and b[j].c < b[j].o:
                            fired += 1; yield j, -1
                        break


SETUPS = [
    dict(id='fvg_first_retest', name='Fair value gap first retest', family='smart-money',
         detect=fvg_first_retest,
         rules="A 3-bar imbalance (bar 3's low above bar 1's high, or the mirror) at least 0.3 ATR wide. "
               "The first bar within 12 bars that trades back into the gap without closing through it and "
               "closes in the displacement direction (green for a bullish gap, red for bearish) leans with "
               "the displacement; a bar that trades through the gap voids it. Before 15:00."),
]
