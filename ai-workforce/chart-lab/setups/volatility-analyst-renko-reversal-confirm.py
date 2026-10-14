"""ATR-Renko reversal with a second confirming brick, 5-minute closes.
Added 2026-10-14 by volatility-analyst via WebSearch (LuxAlgo Renko concept page and MQL5 classic-Renko indicator:
brick size from ATR, a reversal needs two full bricks against the run, practitioners enter after the flip is
confirmed; the sources give no backtested entry rule, so this is a test, not an assumption).
Rules fixed BEFORE any P&L was seen: brick = 0.5 x the session's opening ATR(14) of 5-minute bars (fixed at the open so
bricks never repaint); bricks are built from 5-minute closes starting at the first bar's open; a brick in the opposite
direction needs two brick sizes beyond the last brick close. Signal: the bar whose close completes the SECOND brick of a
run that began with a reversal, with the close on the same side of session VWAP, 10:00 to 15:00 ET, at most two a session.
Everything is known at the signal bar's close.
"""


def renko_reversal_confirm(s):
    b = s.bars
    brick = 0.5 * s.atr[0]
    if brick <= 0:
        return
    last, dr, run, reversed_run = b[0].o, 0, 0, False
    fired = 0
    for i, x in enumerate(b):
        c = x.c
        before = (dr, run, reversed_run)
        while True:
            if dr >= 0 and c >= last + brick:
                last += brick
                if dr == 1: run += 1
                else: dr, run, reversed_run = 1, 1, dr == -1
            elif dr <= 0 and c <= last - brick:
                last -= brick
                if dr == -1: run += 1
                else: dr, run, reversed_run = -1, 1, dr == 1
            elif dr == 1 and c <= last - 2 * brick:
                last -= 2 * brick
                dr, run, reversed_run = -1, 1, True
            elif dr == -1 and c >= last + 2 * brick:
                last += 2 * brick
                dr, run, reversed_run = 1, 1, True
            else:
                break
        if (dr, reversed_run) == (before[0], True) and before[1] < 2 <= run and fired < 2 and 600 <= x.m < 900:
            if dr * (c - s.vwap[i]) > 0:
                fired += 1
                yield i, dr


SETUPS = [
    dict(id='renko_reversal_confirm', name='ATR-Renko reversal confirmed by a second brick', family='volatility',
         detect=renko_reversal_confirm,
         rules="Renko bricks of half the opening 5-minute ATR are built from 5-minute closes (a reversal needs two "
               "bricks). When a run that began with a reversal gets its second brick, and the close is on the same "
               "side of VWAP, between 10:00 and 15:00 ET, the setup leans with the new run; at most two a session. "
               "Tested with and against."),
]
