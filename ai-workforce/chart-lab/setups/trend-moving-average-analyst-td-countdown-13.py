"""TD Sequential countdown 13 (qualified) on 5-minute session bars.
Added 2026-10-14 by trend-moving-average-analyst via WebSearch (prorealcode / oxfordstrat / LuxAlgo TD Sequential write-ups of
DeMark's countdown). td_setup_nine only tests the 9; the 13 countdown was never tested.
Parameters fixed BEFORE any P&L was seen: setup = nine consecutive closes each below (above) the close four bars earlier;
countdown starts after bar 9, a bar counts when its close is <= the low (>= the high) two bars earlier, counts need not be
consecutive; bar 13 must also have its low <= the close of count bar 8 (high >= for sells) or it is deferred until a later
bar qualifies. A completed opposite setup 9 cancels the countdown. Session-only, signal before 15:00, one per side per session.
"""


def td_countdown(s):
    b = s.bars
    n = len(b)
    up = dn = 0
    cd = {1: None, -1: None}      # per side: dict(count, c8) once its setup completed
    done = set()
    for i in range(4, n):
        if b[i].m >= 900:
            return
        dn = dn + 1 if b[i].c < b[i - 4].c else 0
        up = up + 1 if b[i].c > b[i - 4].c else 0
        if dn == 9:
            cd[1] = dict(count=0, c8=None); cd[-1] = None
        elif up == 9:
            cd[-1] = dict(count=0, c8=None); cd[1] = None
        else:
            for d in (1, -1):
                st = cd[d]
                if st is None or i < 2 or d in done:
                    continue
                hit = b[i].c <= b[i - 2].l if d == 1 else b[i].c >= b[i - 2].h
                if not hit:
                    continue
                if st['count'] == 12:
                    ok = b[i].l <= st['c8'] if d == 1 else b[i].h >= st['c8']
                    if ok:
                        done.add(d)
                        yield i, d
                else:
                    st['count'] += 1
                    if st['count'] == 8:
                        st['c8'] = b[i].c


SETUPS = [
    dict(id='td_countdown_13', name='TD Sequential countdown 13 (qualified)', family='trend',
         detect=td_countdown,
         rules="After nine 5-minute closes each below (above) the close four bars earlier, count bars that close at or "
               "below the low (at or above the high) two bars earlier, not necessarily in a row. Bar 13 must also trade "
               "to or beyond the close of count bar 8. Leans long (short) at that close before 15:00 as an exhaustion "
               "signal; a completed opposite 9 cancels the count. One signal per side per session; tested with and against."),
]
