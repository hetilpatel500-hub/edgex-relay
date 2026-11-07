"""Klinger Volume Oscillator signal-line cross confirmed by VWAP side.
Added 2026-10-10 by volume-vwap-analyst via WebSearch (queue was fully coded; sources: capital.com Klinger
oscillator guide, luxalgo.com Klinger article). The lab had no Klinger setup. Standard settings 34/55/13 used
unchanged (not tuned): volume force = volume x |2*dm/cm - 1| x trend x 100, KVO = EMA34 - EMA55 of volume force,
signal = EMA13 of KVO, all restarted each session. Signal at the close of the first bar between 11:00 and 14:30 ET
where KVO crosses its signal line and the close is on the same side of session VWAP; one per session.
"""


def klinger_signal_cross(s):
    b = s.bars
    ef = es = esig = None
    prev_hlc = prev_dm = cm = None
    trend = 0
    prev_diff = None
    for i, x in enumerate(b):
        hlc = x.h + x.l + x.c
        dm = x.h - x.l
        if prev_hlc is None:
            prev_hlc, prev_dm, cm = hlc, dm, dm
            continue
        t = 1 if hlc > prev_hlc else -1
        cm = (cm + dm) if t == trend else (prev_dm + dm)
        trend = t
        prev_hlc, prev_dm = hlc, dm
        vf = x.v * abs(2 * dm / cm - 1) * t * 100 if cm else 0.0
        ef = vf if ef is None else ef + (2 / 35) * (vf - ef)
        es = vf if es is None else es + (2 / 56) * (vf - es)
        kvo = ef - es
        esig = kvo if esig is None else esig + (2 / 14) * (kvo - esig)
        diff = kvo - esig
        pd, prev_diff = prev_diff, diff
        if pd is None or x.m < 660 or x.m > 870 or i + 1 >= len(b):
            continue
        d = 1 if (pd <= 0 < diff) else (-1 if (pd >= 0 > diff) else 0)
        if d and (x.c - s.vwap[i]) * d > 0:
            yield i, d
            return


SETUPS = [
    dict(id='klinger_signal_cross', name='Klinger oscillator signal cross with VWAP', family='volume',
         detect=klinger_signal_cross,
         rules="The Klinger Volume Oscillator (standard 34/55/13, restarted each session) crosses its signal line "
               "between 11:00 and 14:30 while price closes on the same side of VWAP: up-cross above VWAP leans "
               "long, down-cross below VWAP leans short. One signal per session; tested with and against."),
]
