"""Darvas box breakout on 5-minute bars, with VWAP agreement.
Added 2026-10-13 by pattern-specialist via WebSearch (neostox Darvas box guide, tradingsim Darvas box, TradingView
"Advanced Intraday Darvas Box"): a box top is a fresh high that the next 3 bars do not exceed; the bottom is the lowest
low from the top through those 3 bars; a CLOSE beyond the top/bottom is the breakout; tiny boxes are filtered by an ATR
multiple and a VWAP trend filter is common. The sources give no intraday bar count, so these were fixed BEFORE any P&L
was seen: confirm after 3 bars (the sources' number), box height >= 0.75 ATR(14), signal within 12 bars of confirmation,
close on the VWAP side of the break, 10:00 to 15:00 ET, one signal per side per session.
"""


def darvas(s):
    b = s.bars
    n = len(b)
    done = {1: False, -1: False}
    for t in range(3, n - 4):
        # box top: bar t's high is the highest of the previous 6 bars and not exceeded by the next 3
        if t >= 6 and b[t].h > max(x.h for x in b[t - 6:t]) and all(b[t + j].h <= b[t].h for j in (1, 2, 3)):
            top = b[t].h
            bot = min(x.l for x in b[t:t + 4])
            c0 = t + 3
            if top - bot >= 0.75 * s.atr[c0]:
                for i in range(c0 + 1, min(c0 + 13, n)):
                    if b[i].h > top and b[i].c <= top:
                        break           # wicked out without a close: box is spent
                    if b[i].l < bot:
                        break
                    if b[i].c > top:
                        if not done[1] and 600 <= b[i].m < 900 and b[i].c > s.vwap[i]:
                            done[1] = True
                            yield i, 1
                        break
        if t >= 6 and b[t].l < min(x.l for x in b[t - 6:t]) and all(b[t + j].l >= b[t].l for j in (1, 2, 3)):
            bot = b[t].l
            top = max(x.h for x in b[t:t + 4])
            c0 = t + 3
            if top - bot >= 0.75 * s.atr[c0]:
                for i in range(c0 + 1, min(c0 + 13, n)):
                    if b[i].l < bot and b[i].c >= bot:
                        break
                    if b[i].h > top:
                        break
                    if b[i].c < bot:
                        if not done[-1] and 600 <= b[i].m < 900 and b[i].c < s.vwap[i]:
                            done[-1] = True
                            yield i, -1
                        break


SETUPS = [
    dict(id='darvas_box_break', name='Darvas box breakout with VWAP', family='pattern',
         detect=darvas,
         rules="A box forms when a 5-minute high (the highest of the previous 6 bars) is not exceeded for the next 3 bars; "
               "the box floor is the lowest low from that high through those 3 bars, and the box must be at least 0.75 ATR tall. "
               "A close above the box top within 12 bars of confirmation, on the VWAP side, leans long; the mirror box "
               "(a low held for 3 bars) closing below its floor under VWAP leans short. 10:00 to 15:00 ET, one signal per side "
               "per session; tested with and against."),
]
