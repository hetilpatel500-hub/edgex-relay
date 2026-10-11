"""Percentage Volume Oscillator (PVO) crossing above its signal line, direction taken from price (VWAP side + bar colour), 5-minute bars.
Added 2026-10-11 by volume-vwap-analyst via WebSearch (TradingView support, LuxAlgo and StockSharp PVO pages: PVO = 100 *
(EMA12(volume) - EMA26(volume)) / EMA26(volume), signal = EMA9 of PVO, a signal-line cross is the early read of volume
momentum turning; all sources stress PVO is direction-blind, so direction must come from price). Those are daily-chart
sources, so this is an untested intraday adaptation. Parameters fixed BEFORE any P&L was seen: Long at the close of the
first bar between 10:30 and 14:30 ET where PVO crosses above its signal line, the bar closes above its open and the
close is above session VWAP (mirror for short). One signal per session.
"""


def _ema(x, n):
    k = 2 / (n + 1)
    out, e = [], None
    for v in x:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def pvo_signal_cross(s):
    b = s.bars
    v = [x.v for x in b]
    f, sl = _ema(v, 12), _ema(v, 26)
    pvo = [100 * (f[i] - sl[i]) / sl[i] if sl[i] else 0.0 for i in range(len(b))]
    sig = _ema(pvo, 9)
    for i in range(27, len(b) - 1):
        x = b[i]
        if x.m < 630 or x.m > 870:
            continue
        if pvo[i] > sig[i] and pvo[i - 1] <= sig[i - 1]:
            if x.c > x.o and x.c > s.vwap[i]:
                yield i, 1
                return
            if x.c < x.o and x.c < s.vwap[i]:
                yield i, -1
                return


SETUPS = [
    dict(id='pvo_signal_cross', name='Percentage Volume Oscillator signal cross with VWAP', family='volume',
         detect=pvo_signal_cross,
         rules="The Percentage Volume Oscillator compares a fast (12-bar) and slow (26-bar) average of 5-minute "
               "volume; when it crosses above its 9-bar signal line, volume momentum is picking up. Between 10:30 "
               "and 14:30, if that bar also closes up and above VWAP it leans long; closing down and below VWAP "
               "leans short. One signal per session; tested with and against."),
]
