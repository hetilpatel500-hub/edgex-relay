"""Accumulation/Distribution Line breaking its own 20-bar range ahead of price, 5-minute bars.
Added 2026-10-13 by volume-vwap-analyst (WebSearch 2026-10-13: volume-flow indicators are read for a
"confirmation" or "non-confirmation" of price; an A/D line making a new range extreme is read as money flow
leading). Not the Chaikin oscillator cross and not a divergence setup. Rules fixed BEFORE any P&L was seen:
ADL = running sum of ((close-low)-(high-close))/(high-low)*volume from the session's first bar; signal when
ADL closes above its prior 20-bar maximum (below its prior 20-bar minimum) while the bar closes on the same
side of session VWAP and price itself has NOT yet broken its prior 20-bar high (low); 10:15 to 14:30 ET;
signal on that bar's close; at most two a session.
"""


def adl_range_break(s):
    b = s.bars
    adl, tot = [], 0.0
    for x in b:
        r = x.h - x.l
        tot += ((x.c - x.l) - (x.h - x.c)) / r * x.v if r > 0 else 0.0
        adl.append(tot)
    fired = 0
    for i in range(20, len(b)):
        if b[i].m < 615 or b[i].m >= 870 or fired >= 2:
            continue
        pa = adl[i - 20:i]
        ph = max(x.h for x in b[i - 20:i]); pl = min(x.l for x in b[i - 20:i])
        if adl[i] > max(pa) and b[i].c > s.vwap[i] and b[i].c <= ph:
            fired += 1; yield i, 1
        elif adl[i] < min(pa) and b[i].c < s.vwap[i] and b[i].c >= pl:
            fired += 1; yield i, -1


SETUPS = [
    dict(id='adl_range_break', name='A/D line breaks its 20-bar range before price does', family='volume',
         detect=adl_range_break,
         rules="The running Accumulation/Distribution line closes above its prior 20-bar maximum (or below its "
               "minimum) while the bar closes on the same side of session VWAP and price has not yet broken its "
               "own prior 20-bar high (or low). 10:15 to 14:30 ET, at most two a session. Leans with the "
               "money flow. Tested with and against."),
]
