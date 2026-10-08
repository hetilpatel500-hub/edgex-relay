"""Tight pause at the day's extreme after a thrust, break of the pause.
Added 2026-10-04 by pattern-specialist via WebSearch-style "high tight flag / pause" day-trading write-ups
(thrust, then a few small bars hugging the extreme, then the break). Parameters fixed BEFORE any P&L was seen:
6-bar thrust >= 2 ATR, 4-bar pause range <= 1.5 ATR, pause within 0.5 ATR of the day extreme, 10:30 to 14:30.
The lab tests it with and against.
"""


def tight_pause_break(s):
    """A 6-bar thrust of at least 2 ATR ends at (or near) a new session extreme; the next 4 bars form a pause
    whose total range is at most 1.5 ATR and sits within 0.5 ATR of that extreme. The first close beyond the
    pause (within 6 bars) gives the signal in that direction. One signal per side per session."""
    b = s.bars
    done = set()
    for k in range(10, len(b) - 1):
        if b[k].m < 630 or b[k].m > 870:
            continue
        a = s.atr[k]
        if not a:
            continue
        p = b[k - 3:k + 1]                       # 4-bar pause ends at k
        ph, pl = max(x.h for x in p), min(x.l for x in p)
        if ph - pl > 1.5 * a:
            continue
        t0, t1 = b[k - 9].c, b[k - 4].c           # thrust: 6 bars before the pause
        for d in (1, -1):
            if d in done:
                continue
            if d * (t1 - t0) < 2 * a:
                continue
            ext = max(x.h for x in b[:k - 3]) if d == 1 else min(x.l for x in b[:k - 3])
            if d == 1 and ph < ext - 0.5 * a:
                continue
            if d == -1 and pl > ext + 0.5 * a:
                continue
            # first close beyond the pause within the next 6 bars
            for j in range(k + 1, min(k + 7, len(b) - 1)):
                if b[j].m > 870:
                    break
                if (d == 1 and b[j].c > ph) or (d == -1 and b[j].c < pl):
                    done.add(d)
                    yield j, d
                    break
                if (d == 1 and b[j].c < pl) or (d == -1 and b[j].c > ph):
                    break


SETUPS = [
    dict(id='tight_pause_break', name='Tight pause at the day extreme after a thrust: break', family='pattern',
         detect=tight_pause_break,
         rules="A 6-bar thrust of 2+ ATR into a session high (low), then 4 small bars (range 1.5 ATR or less) "
               "hugging that extreme; the first close beyond the pause within 6 bars is the signal, 10:30 to "
               "14:30. Tested with and against; one per side per session."),
]
