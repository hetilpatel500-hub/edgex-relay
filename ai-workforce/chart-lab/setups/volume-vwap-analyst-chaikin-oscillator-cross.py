"""Chaikin Oscillator (3,10) zero-line cross with VWAP agreement.
Added 2026-10-10 by volume-vwap-analyst via WebSearch (queue was fully coded; sources: strike.money Chaikin
Oscillator guide, lightningchart.com Chaikin Oscillator, metatrader5.com Chaikin Oscillator help). Distinct from
cmf_zero_cross_vwap (a windowed ratio): this is the MACD-style difference of EMAs of the accumulation/distribution line.
Rules fixed BEFORE any P&L was seen, with the published 3 and 10 periods (not retuned): ADL accumulates the
money-flow multiplier ((C-L)-(H-C))/(H-L) x volume from the session's first bar; CO = EMA3(ADL) - EMA10(ADL);
signals only after 12 bars so the EMAs have settled, before 15:00 ET, at most two a session.
"""


def chaikin_oscillator_cross(s):
    b = s.bars
    adl = 0.0
    e3 = e10 = None
    prev = None
    fired = 0
    for i, x in enumerate(b):
        r = x.h - x.l
        adl += ((x.c - x.l) - (x.h - x.c)) / r * x.v if r > 0 else 0.0
        e3 = adl if e3 is None else e3 + (adl - e3) * 0.5
        e10 = adl if e10 is None else e10 + (adl - e10) * (2 / 11)
        co = e3 - e10
        if i >= 12 and prev is not None and x.m < 900 and fired < 2:
            if prev <= 0 < co and x.c > s.vwap[i]:
                fired += 1
                yield i, 1
            elif prev >= 0 > co and x.c < s.vwap[i]:
                fired += 1
                yield i, -1
        prev = co


SETUPS = [
    dict(id='chaikin_oscillator_cross', name='Chaikin Oscillator zero cross + VWAP', family='volume',
         detect=chaikin_oscillator_cross,
         rules="The Chaikin Oscillator (3-bar EMA minus 10-bar EMA of the session's accumulation/distribution line) "
               "crossing above zero while price closes above VWAP leans long; crossing below zero while price closes "
               "below VWAP leans short. After the first 12 bars, before 15:00 ET, at most two a session; tested with "
               "and against."),
]
