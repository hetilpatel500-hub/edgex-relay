"""Mass Index reversal bulge on 5-minute bars.
Added 2026-10-11 by volatility-analyst via WebSearch (TradingSim "3 Ways to Spot Trend Reversals with the Mass Index",
Dorsey's classic rule: Mass Index = 25-bar sum of EMA9(high-low) / EMA9(EMA9(high-low)); a reversal bulge is the index
rising above 27 and then falling back below 26.5. The index has no direction, so the rule pairs it with a 9-bar EMA of
the close: a bulge while that EMA is falling means a bottom is forming, rising means a top). The source gives no
intraday evidence. Untested adaptation.
Parameters fixed BEFORE any P&L was seen: the classic 9/25/27/26.5 and EMA9 of closes. Computed inside the session
only (the first signal is possible after about 13:00 ET because of warm-up). One signal per session.
"""


def ema(x, n):
    k = 2.0 / (n + 1)
    out, e = [], None
    for v in x:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def mass_index_bulge(s):
    b = s.bars
    rng = [x.h - x.l for x in b]
    e1 = ema(rng, 9)
    e2 = ema(e1, 9)
    ratio = [e1[i] / e2[i] if e2[i] else 1.0 for i in range(len(b))]
    mi = [None] * len(b)
    for i in range(24, len(b)):
        mi[i] = sum(ratio[i - 24:i + 1])
    ec = ema([x.c for x in b], 9)
    armed = False
    for i in range(25, len(b) - 1):
        if mi[i] > 27:
            armed = True
        elif armed and mi[i] < 26.5:
            if ec[i] < ec[i - 1]:
                yield i, 1
            elif ec[i] > ec[i - 1]:
                yield i, -1
            return


SETUPS = [
    dict(id='mass_index_bulge', name='Mass Index reversal bulge', family='volatility',
         detect=mass_index_bulge,
         rules="Add up, over 25 bars, how wide the 5-minute range is relative to its own smoothed average (the Mass "
               "Index). When it climbs above 27 and then drops back under 26.5 (a 'reversal bulge'), the trend is "
               "tiring: lean long if the 9-bar average of closes is falling, short if it is rising. One signal per "
               "session; tested with and against."),
]
