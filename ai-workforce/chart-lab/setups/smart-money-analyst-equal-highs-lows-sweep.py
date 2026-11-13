"""Equal highs / equal lows liquidity sweep on 5-minute bars.
Added 2026-10-01 by smart-money-analyst: the research queue is fully coded, so
this run used WebSearch (luxalgo.com, innercircletrader.net, equiti.com) for
the ICT idea that stops cluster behind equal highs/lows and a sweep that
closes back inside reverses. Distinct from turtle_soup (rolling 20-bar extreme,
no pairing) and pd_sweep / ib_sweep (fixed session levels).
"""


def equal_hl_sweep(s):
    """Two confirmed 5-minute swing highs (3-bar pivots) at least 3 bars apart
    and within 0.15 ATR of each other form equal highs; a later bar that trades
    above them and closes back below leans short. Equal lows mirror to long.
    A pivot counts only once the bar after it has closed (no look-ahead).
    One signal per side per session, 10:30 to 14:30."""
    b = s.bars
    fired = set()
    for i in range(8, len(b)):
        m = b[i].m
        if m >= 870:
            break
        if m < 600:
            continue
        atr = s.atr[i - 1]
        if not atr:
            continue
        piv_h = [k for k in range(1, i - 1) if b[k].h > b[k - 1].h and b[k].h >= b[k + 1].h and k + 1 < i]
        piv_l = [k for k in range(1, i - 1) if b[k].l < b[k - 1].l and b[k].l <= b[k + 1].l and k + 1 < i]
        x = b[i]
        if -1 not in fired and len(piv_h) >= 2:
            k2, k1 = piv_h[-1], piv_h[-2]
            lvl = max(b[k1].h, b[k2].h)
            if k2 - k1 >= 3 and abs(b[k1].h - b[k2].h) <= 0.15 * atr \
                    and max(y.h for y in b[k2 + 1:i]) <= lvl and x.h > lvl and x.c < lvl:
                fired.add(-1)
                yield i, -1
                continue
        if 1 not in fired and len(piv_l) >= 2:
            k2, k1 = piv_l[-1], piv_l[-2]
            lvl = min(b[k1].l, b[k2].l)
            if k2 - k1 >= 3 and abs(b[k1].l - b[k2].l) <= 0.15 * atr \
                    and min(y.l for y in b[k2 + 1:i]) >= lvl and x.l < lvl and x.c > lvl:
                fired.add(1)
                yield i, 1


SETUPS = [
    dict(id='equal_hl_sweep', name='Equal highs / lows liquidity sweep', family='smart-money',
         detect=equal_hl_sweep,
         rules="Two swing highs at least 3 bars apart and within 0.15 ATR of each other are equal highs, where "
               "stops cluster. A later 5-minute bar that trades above them but closes back below leans short; "
               "equal lows swept and reclaimed lean long. One signal per side per session, 10:30 to 14:30 ET."),
]
