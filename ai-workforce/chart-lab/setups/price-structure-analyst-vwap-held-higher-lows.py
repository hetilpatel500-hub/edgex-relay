"""VWAP-held higher lows (lower highs) break: structure sequence that respects VWAP, then breaks out.
Added 2026-10-07 by price-structure-analyst via the lab queue (swing-structure read gated by VWAP; distinct from
first_pullback, h2_l2 and failed_hod_break, none of which require two successive swing lows to hold the VWAP).
Parameters fixed BEFORE any P&L was seen: swing low = 5-bar pivot (2 bars each side), confirmed 2 bars later.
Long: two consecutive confirmed swing lows, the second higher than the first, both above session VWAP at their
own bar, the later pivot's bar starting 10:00-13:30 ET; signal at the first close above the high of the bar
range between the two pivots (the highest high from first pivot to now before this bar), before 14:30 ET.
Short is the mirror (two lower swing highs, both below VWAP). One signal per session; direction is the break.
"""


def vwap_held_structure(s):
    b = s.bars
    n = len(b)
    lows, highs = [], []
    for i in range(n):
        k = i - 2
        if k >= 2:
            if all(b[k].l < b[j].l for j in (k - 2, k - 1, k + 1, k + 2)):
                lows.append((k, b[k].l, b[k].l > s.vwap[k]))
            if all(b[k].h > b[j].h for j in (k - 2, k - 1, k + 1, k + 2)):
                highs.append((k, b[k].h, b[k].h < s.vwap[k]))
        if b[i].m >= 870 or b[i].m < 600:
            continue
        # long
        if len(lows) >= 2:
            (k1, l1, a1), (k2, l2, a2) = lows[-2], lows[-1]
            if a1 and a2 and l2 > l1 and b[k2].m >= 600 and b[k2].m <= 810:
                lvl = max(x.h for x in b[k1:i])
                if b[i].c > lvl and b[i - 1].c <= lvl:
                    yield i, 1
                    return
        if len(highs) >= 2:
            (k1, h1, a1), (k2, h2, a2) = highs[-2], highs[-1]
            if a1 and a2 and h2 < h1 and b[k2].m >= 600 and b[k2].m <= 810:
                lvl = min(x.l for x in b[k1:i])
                if b[i].c < lvl and b[i - 1].c >= lvl:
                    yield i, -1
                    return


SETUPS = [
    dict(id='vwap_held_structure', name='VWAP-held higher lows / lower highs break', family='structure',
         detect=vwap_held_structure,
         rules="Two successive swing lows (5-bar pivots) form, the second higher than the first and both above "
               "VWAP, the later one between 10:00 and 13:30 ET; the first close above the highest high since "
               "the first pivot, before 14:30, leans long (mirror for lower highs below VWAP). One signal per "
               "session, in the direction of the break; tested with and against."),
]
