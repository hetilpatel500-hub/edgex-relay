"""Arms' Ease of Movement (14) zero cross confirmed by VWAP side.
Added 2026-10-10 by volume-vwap-analyst via WebSearch (queue fully coded; search found no ready-made 5-minute
rules for Klinger/EMV, so this is a lab adaptation of Richard Arms' Ease of Movement: how far the midpoint moved per
unit of volume, so a rise on thin volume reads as 'easy'). The lab had Force Index, MFI, CMF and CLV-delta but no
EMV. Parameters fixed BEFORE any P&L was seen: per 5-minute bar, distance = midpoint - previous midpoint (first
bar uses its own open as previous midpoint); box ratio = (volume / session mean volume so far) / ((high - low) /
ATR) (bars with zero range skipped); EMV = distance / ATR / box ratio; smoothed with a 14-bar simple average
restarted each session. Signal at the close of the first bar between 10:00 and 14:30 ET where the smoothed EMV
crosses zero and the close is on the same side of session VWAP as the cross; one per session; direction = sign of
the cross.
"""


def emv_cross(s):
    b = s.bars
    prev_mid = b[0].o
    vals, vsum = [], 0.0
    prev_sm = None
    for i, x in enumerate(b):
        vsum += x.v
        mid = (x.h + x.l) / 2
        atr = s.atr[i]
        e = 0.0
        if atr and x.h > x.l and x.v > 0:
            box = (x.v / (vsum / (i + 1))) / ((x.h - x.l) / atr)
            e = (mid - prev_mid) / atr / box
        prev_mid = mid
        vals.append(e)
        if len(vals) < 14:
            continue
        sm = sum(vals[-14:]) / 14
        ps, prev_sm = prev_sm, sm
        if ps is None or x.m < 600 or x.m > 870 or i + 1 >= len(b):
            continue
        d = 1 if (ps <= 0 < sm) else (-1 if (ps >= 0 > sm) else 0)
        if d and (x.c - s.vwap[i]) * d > 0:
            yield i, d
            return


SETUPS = [
    dict(id='emv_cross_vwap', name='Ease of Movement (14) zero cross with VWAP', family='volume',
         detect=emv_cross,
         rules="Arms' Ease of Movement (midpoint change per unit of relative volume, 14-bar average, restarted each "
               "session) crosses zero between 10:00 and 14:30 while price closes on the same side of VWAP: "
               "up-cross above VWAP leans long, down-cross below VWAP leans short. One signal per session; "
               "tested with and against."),
]
