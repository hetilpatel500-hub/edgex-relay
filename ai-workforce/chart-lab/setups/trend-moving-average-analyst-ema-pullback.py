"""EMA 9/20 pullback in a trending session.
Added 2026-09-27 by trend-moving-average-analyst: trend family, next open
line of the research queue in ai-workforce/chart-lab/README.md.
"""


def _ema(closes, n):
    k = 2 / (n + 1)
    out, prev = [], None
    for c in closes:
        prev = c if prev is None else c * k + prev * (1 - k)
        out.append(prev)
    return out


def ema9_20_pullback(s):
    """A session is trending once EMA9 sits on one side of EMA20 and EMA20
    itself has risen (fallen) over the last 5 bars. In that trend, a pullback
    that touches EMA9 and then closes back beyond it, in the trend's
    direction and above (below) the prior bar's close, is the entry."""
    b = s.bars
    closes = [x.c for x in b]
    ema9 = _ema(closes, 9)
    ema20 = _ema(closes, 20)
    fired = 0
    for i in range(20, len(b)):
        if b[i].m >= 900 or fired >= 3:
            break
        if ema9[i] > ema20[i] and ema20[i] > ema20[i - 5]:
            d = 1
        elif ema9[i] < ema20[i] and ema20[i] < ema20[i - 5]:
            d = -1
        else:
            continue
        if d == 1:
            touched = b[i - 1].l <= ema9[i - 1]
            confirm = b[i].c > ema9[i] and b[i].c > b[i - 1].c
        else:
            touched = b[i - 1].h >= ema9[i - 1]
            confirm = b[i].c < ema9[i] and b[i].c < b[i - 1].c
        if touched and confirm:
            fired += 1
            yield i, d


SETUPS = [
    dict(id='ema9_20_pullback', name='EMA 9/20 pullback in trend', family='trend', detect=ema9_20_pullback,
         rules="EMA9 on one side of EMA20 with EMA20 sloping the same way over the last 5 bars marks a trending "
               "session. A bar that touches EMA9 against the trend and the next bar closes back beyond EMA9 in "
               "the trend's direction (and beyond the prior close) confirms the pullback held, before 15:00."),
]
