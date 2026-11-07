"""Three drives to a high / low (three-push exhaustion).
Added 2026-10-01 by pattern-specialist: the classic three-drive / "three
pushes" exhaustion pattern, not on the research queue. Rules fixed before
any P&L was looked at: three consecutive confirmed swing highs (lows), each
at least 0.2 ATR beyond the one before and at least 3 bars apart. The third
pivot's confirmation bar (two bars after the pivot) is the signal, leaning
against the third push, before 15:00. One signal per side per session.
"""


def three_drives(s):
    b = s.bars
    n = len(b)
    highs, lows = [], []
    fired_top = fired_bot = False
    for i in range(4, n):
        if b[i].m >= 900:
            return
        k = i - 2
        if k < 2:
            continue
        atr = s.atr[k]
        if not atr:
            continue
        if all(b[k].h > b[j].h for j in (k - 2, k - 1, k + 1, k + 2)):
            if not highs or (k - highs[-1][0] >= 3 and b[k].h >= highs[-1][1] + 0.2 * atr):
                highs.append((k, b[k].h))
            else:
                highs = [(k, b[k].h)]
            if len(highs) >= 3 and not fired_top:
                fired_top = True
                yield i, -1
        if all(b[k].l < b[j].l for j in (k - 2, k - 1, k + 1, k + 2)):
            if not lows or (k - lows[-1][0] >= 3 and b[k].l <= lows[-1][1] - 0.2 * atr):
                lows.append((k, b[k].l))
            else:
                lows = [(k, b[k].l)]
            if len(lows) >= 3 and not fired_bot:
                fired_bot = True
                yield i, 1


SETUPS = [
    dict(id='three_drives', name='Three drives to a high / low', family='pattern',
         detect=three_drives,
         rules="Three consecutive swing highs, each at least 0.2 ATR above the last and 3+ bars apart (or three "
               "swing lows, each lower), mark three pushes into exhaustion. The bar that confirms the third swing "
               "leans against the push, before 15:00, once per side per session."),
]
