"""ConnorsRSI re-entry from 10/90, 5-minute bars.
Added 2026-10-12 by momentum-analyst via WebSearch (luxalgo.com Connors RSI concept and guide, therighttrader.com:
ConnorsRSI = average of RSI(3) of price, RSI(2) of the up/down streak length, and the percent rank of the latest
one-bar return; 3,2,100 on intraday bars with lines at 10 and 90. The sources give no intraday evidence and one notes
extra noise; the percent-rank window here is adapted to the session). Untested intraday adaptation.
Parameters fixed BEFORE any P&L was seen: RSI(3) and streak RSI(2) with simple-average gains/losses; percent rank of
the bar's return among the earlier returns of the SAME session (at least 24 earlier returns, so no signal before about
11:00); 10:30 to 14:30 ET; long at the close of the first bar where ConnorsRSI crosses back up through 10 (short: back
down through 90). One signal per session. No VWAP or candle filter.
"""


def _rsi(x, n, i):
    g = l = 0.0
    for k in range(i - n + 1, i + 1):
        d = x[k] - x[k - 1]
        if d > 0:
            g += d
        else:
            l -= d
    return 100.0 if l == 0 and g > 0 else 50.0 if l == 0 else 100 - 100 / (1 + g / l)


def connors_rsi_reentry(s):
    b = s.bars
    c = [x.c for x in b]
    streak = [0] * len(b)
    for i in range(1, len(b)):
        d = c[i] - c[i - 1]
        streak[i] = (streak[i - 1] + 1 if streak[i - 1] > 0 else 1) if d > 0 else \
                    (streak[i - 1] - 1 if streak[i - 1] < 0 else -1) if d < 0 else 0
    ret = [0.0] + [(c[i] - c[i - 1]) / c[i - 1] for i in range(1, len(b))]
    crsi = [None] * len(b)
    for i in range(26, len(b)):
        prior = ret[1:i]
        rank = 100.0 * sum(1 for r in prior if r < ret[i]) / len(prior)
        crsi[i] = (_rsi(c, 3, i) + _rsi(streak, 2, i) + rank) / 3
    for i in range(27, len(b) - 1):
        m = b[i].m
        if m < 630 or m > 870:
            continue
        if crsi[i] > 10 and crsi[i - 1] <= 10:
            yield i, 1
            return
        if crsi[i] < 90 and crsi[i - 1] >= 90:
            yield i, -1
            return


SETUPS = [
    dict(id='connors_rsi_reentry', name='ConnorsRSI re-entry from 10/90', family='momentum',
         detect=connors_rsi_reentry,
         rules="ConnorsRSI averages a 3-bar RSI of price, a 2-bar RSI of the up/down streak length and the "
               "percent rank of the latest bar's return among earlier returns that session. Between 10:30 and "
               "14:30 the first cross back up through 10 leans long and the first cross back down through 90 "
               "leans short. One signal per session; tested with and against."),
]
