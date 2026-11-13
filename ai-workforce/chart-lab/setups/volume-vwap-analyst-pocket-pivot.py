"""Pocket pivot (daily).
Added 2026-10-05 by volume-vwap-analyst: the research queue held only tape items, so this run took the
documented Morales/Kacher pocket pivot (up-day volume larger than every down-day volume of the prior 10 sessions;
sources: luxalgo.com/library/concept/pocket-pivot, TradingView pocket pivot scripts). Rules fixed BEFORE any P&L was
seen: 10-session look-back, 10-day SMA position as the trend gate, the mirror image for shorts.
"""


def pocket_pivot(ser):
    n = len(ser.c)
    for j in range(21, n):
        if ser.c[j] == ser.c[j - 1]:
            continue
        up = ser.c[j] > ser.c[j - 1]
        opp = [ser.v[k] for k in range(j - 10, j) if (ser.c[k] < ser.c[k - 1]) == up and ser.c[k] != ser.c[k - 1]]
        if not opp:
            continue
        sma10 = sum(ser.c[j - 9:j + 1]) / 10
        if up and ser.v[j] > max(opp) and ser.c[j] > sma10:
            yield j, 1
        elif not up and ser.v[j] > max(opp) and ser.c[j] < sma10:
            yield j, -1


SETUPS = [
    dict(id='d_pocket_pivot', tf='D', name='Pocket pivot', family='volume (daily)', detect=pocket_pivot,
         rules="A daily close above the prior close, on volume greater than every down day's volume in the prior 10 "
               "sessions, with the close above its 10-day average, is a pocket pivot (institutional buying "
               "outweighing recent selling). The mirror image (down day, volume above every prior-10 up day, close "
               "below the 10-day average) is the bearish version."),
]
