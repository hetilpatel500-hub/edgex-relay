"""Head and shoulders / inverse head and shoulders: neckline break.
Added 2026-10-15 by pattern-specialist via the classic chart-pattern literature (Bulkowski, Edwards & Magee);
no head-and-shoulders detector is in the lab yet. Parameters fixed BEFORE any P&L was seen: 3-bar pivots,
head at least 0.5 ATR beyond both shoulders, shoulders within 1 ATR of each other, pattern height at least
1 ATR, break within 12 bars. The lab tests it with and against.
"""


def head_shoulders(s):
    """Pivot highs/lows need 3 lower (higher) bars on each side and are known 3 bars later. Top: three
    consecutive pivot highs LS, H, RS with H above both shoulders by 0.5 ATR or more and the shoulders within
    1 ATR of each other; the neckline is the lower of the two pivot lows between them and must sit at least
    1 ATR under the head. The first close under the neckline within 12 bars of the right shoulder's
    confirmation (before price retakes the head) leans short. Inverse pattern mirrors it. 10:30 to 14:30 ET,
    one signal per side per session."""
    b = s.bars
    n = len(b)
    ph, pl = [], []                     # (index, price), confirmed at index + 3
    done = set()
    for i in range(3, n - 1):
        k = i - 3                        # pivot candidate k is confirmed at bar i
        if k >= 3:
            if b[k].h > max(x.h for x in b[k - 3:k]) and b[k].h > max(x.h for x in b[k + 1:k + 4]):
                ph.append((k, b[k].h))
            if b[k].l < min(x.l for x in b[k - 3:k]) and b[k].l < min(x.l for x in b[k + 1:k + 4]):
                pl.append((k, b[k].l))
        a = s.atr[i]
        if not a or b[i].m < 630 or b[i].m > 870:
            continue
        for d in (-1, 1):
            if d in done:
                continue
            hs, ls = (ph, pl) if d == -1 else (pl, ph)
            if len(hs) < 3:
                continue
            (k1, p1), (k2, p2), (k3, p3) = hs[-3:]
            if i - k3 > 3 + 12:           # right shoulder too old
                continue
            if d == -1:
                ok = p2 - max(p1, p3) >= 0.5 * a and abs(p1 - p3) <= a
            else:
                ok = min(p1, p3) - p2 >= 0.5 * a and abs(p1 - p3) <= a
            if not ok:
                continue
            between = [v for (k, v) in ls if k1 < k < k3]
            if len(between) < 2:
                continue
            neck = min(between) if d == -1 else max(between)
            if d == -1 and (p2 - neck < a or b[i].c >= neck or b[i - 1].c < neck or max(x.h for x in b[k3:i + 1]) > p2):
                continue
            if d == 1 and (neck - p2 < a or b[i].c <= neck or b[i - 1].c > neck or min(x.l for x in b[k3:i + 1]) < p2):
                continue
            done.add(d)
            yield i, d


SETUPS = [
    dict(id='head_shoulders_neckline', name='Head and shoulders neckline break (and inverse)', family='pattern',
         detect=head_shoulders,
         rules="Three 5-minute pivots with the middle one beyond both shoulders by 0.5 ATR, shoulders within 1 ATR, "
               "neckline (lower of the two pivots between them) at least 1 ATR from the head; the first close "
               "through the neckline within 12 bars of the right shoulder, before the head is retaken, is the "
               "signal; the inverse pattern mirrors it. 10:30 to 14:30 ET, one per side per session. Tested with and against."),
]
