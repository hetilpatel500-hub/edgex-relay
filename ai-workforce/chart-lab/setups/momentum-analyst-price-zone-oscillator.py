"""Price Zone Oscillator (PZO) re-entry from +/-40, 5-minute bars.
Added 2026-10-12 by momentum-analyst via WebSearch (Walid Khalil / David Steckler's Price Zone Oscillator; sources
list +/-40 as the overbought/oversold zones for non-trending markets and describe PZO as the EMA of close times the
sign of the close-to-close change, divided by the EMA of close, times 100). The sources describe daily use; this is an
untested intraday adaptation. Parameters fixed BEFORE any P&L was seen: EMA length 14 in 5-minute bars within the
session (seeded at the first bar), thresholds +/-40, window 10:30-14:30 ET. Long at the close of the first bar where
PZO crosses back up through -40 after being below it (re-entry from oversold); mirror short through +40. No VWAP
filter. One signal per session.
"""


def pzo_reentry(s):
    b = s.bars
    n = len(b)
    k = 2 / 15
    num = den = None
    pz = [0.0] * n
    for i in range(1, n):
        sg = 1 if b[i].c > b[i - 1].c else (-1 if b[i].c < b[i - 1].c else 0)
        x = sg * b[i].c
        num = x if num is None else num + k * (x - num)
        den = b[i].c if den is None else den + k * (b[i].c - den)
        pz[i] = 100 * num / den
    for i in range(15, n - 1):
        if b[i].m < 630 or b[i].m > 870:
            continue
        if pz[i - 1] < -40 <= pz[i]:
            yield i, 1
            return
        if pz[i - 1] > 40 >= pz[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='pzo_reentry', name='Price Zone Oscillator re-entry from +/-40', family='momentum',
         detect=pzo_reentry,
         rules="PZO is the 14-bar EMA of the close signed by the direction of each bar's change, divided by the 14-bar "
               "EMA of the close. Between 10:30 and 14:30, when it climbs back above -40 it leans long; when it falls "
               "back below +40 it leans short. One signal per session; tested with and against."),
]
