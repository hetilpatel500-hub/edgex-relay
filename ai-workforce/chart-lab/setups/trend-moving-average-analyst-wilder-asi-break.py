"""Wilder Accumulation Swing Index (ASI) leading a price breakout, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst (WebSearch 2026-10-13: the search surfaced Kaufman/Connors
style rules already in the lab, so a not-yet-tested Wilder indicator was taken instead). Swing Index per Wilder
(R by the largest of |H-Cy|, |L-Cy|, H-L; K = max(|H-Cy|,|L-Cy|); limit-move T taken as 1 because only the sign
and the ASI's own highs/lows are used). ASI is cumulated from the session open.
Rules fixed BEFORE any P&L was seen: ASI closes above its prior 12-bar highest value (below lowest) while the bar
closes on the same side of session VWAP and price has NOT yet closed beyond its own prior 12-bar high (low) -
the ASI "leads" price; 10:00 to 14:30 ET; direction = ASI break; signal on that bar's close; at most two a session.
"""


def wilder_asi_break(s):
    b = s.bars
    asi = [0.0] * len(b)
    for i in range(1, len(b)):
        cy, oy = b[i - 1].c, b[i - 1].o
        a, bb, c = abs(b[i].h - cy), abs(b[i].l - cy), b[i].h - b[i].l
        d = abs(cy - oy)
        if a >= bb and a >= c:
            r = a - 0.5 * bb + 0.25 * d
        elif bb >= a and bb >= c:
            r = bb - 0.5 * a + 0.25 * d
        else:
            r = c + 0.25 * d
        n = (b[i].c - cy) + 0.5 * (b[i].c - b[i].o) + 0.25 * (cy - oy)
        si = 50 * n / r * max(a, bb) if r > 0 else 0.0
        asi[i] = asi[i - 1] + si
    fired = 0
    for i in range(13, len(b)):
        if b[i].m < 600 or b[i].m >= 870 or fired >= 2:
            continue
        pa = asi[i - 12:i]
        ph, pl = max(x.h for x in b[i - 12:i]), min(x.l for x in b[i - 12:i])
        if asi[i] > max(pa) and b[i].c > s.vwap[i] and b[i].c <= ph:
            fired += 1; yield i, 1
        elif asi[i] < min(pa) and b[i].c < s.vwap[i] and b[i].c >= pl:
            fired += 1; yield i, -1


SETUPS = [
    dict(id='wilder_asi_break', name="Wilder Accumulation Swing Index leads price", family='trend',
         detect=wilder_asi_break,
         rules="Wilder's Accumulation Swing Index (cumulated from the open) closes above its prior 12-bar high "
               "(or below its low) while the bar is on the same side of VWAP and price itself has not yet closed "
               "beyond its own 12-bar high (low): the index leads price. 10:00 to 14:30 ET, at most two a "
               "session. Leans with the ASI break. Tested with and against."),
]
