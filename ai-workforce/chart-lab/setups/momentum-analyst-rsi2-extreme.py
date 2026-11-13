"""Intraday RSI(2) extreme on 5-minute bars (Connors-style short-term mean reversion).
Added 2026-09-29 by momentum-analyst: the research queue's non-tape lines are
all coded, so this run used WebSearch (RSI(2) below 10 / above 90 as the
short-term exhaustion signal, per the mean-reversion write-ups at
edgeful.com and quantvero.com). Only a daily version (d_rsi2_pullback) was
tested before. Parameters (RSI period 2, thresholds 5/95, 10:00-14:30, one
signal per side per session) were fixed before testing.
"""


def _rsi2(closes):
    out = [None] * len(closes)
    ag = al = None
    for i in range(1, len(closes)):
        ch = closes[i] - closes[i - 1]
        g, l = max(ch, 0.0), max(-ch, 0.0)
        if i == 2:
            ag = (max(closes[1] - closes[0], 0.0) + g) / 2
            al = (max(closes[0] - closes[1], 0.0) + l) / 2
        elif i > 2:
            ag = (ag + g) / 2
            al = (al + l) / 2
        if i >= 2:
            out[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def rsi2_extreme(s):
    b = s.bars
    r = _rsi2([x.c for x in b])
    done = set()
    for i in range(2, len(b)):
        m = b[i].m
        if m < 600:
            continue
        if m >= 870:
            return
        if r[i] is None:
            continue
        if r[i] < 5 and 1 not in done:
            done.add(1); yield i, 1
        elif r[i] > 95 and -1 not in done:
            done.add(-1); yield i, -1


SETUPS = [
    dict(id='rsi2_extreme', name='Intraday RSI(2) extreme', family='momentum',
         detect=rsi2_extreme,
         rules="On 5-minute bars, a close with RSI(2) below 5 leans long (oversold snap-back) and above 95 "
               "leans short, between 10:00 and 14:30, at most once per side per session."),
]
