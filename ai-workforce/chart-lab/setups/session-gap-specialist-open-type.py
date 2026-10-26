"""Open type: open-drive, open-test-drive, open-rejection-reverse.
Added 2026-09-28 by session-gap-specialist: next open line of the research
queue in ai-workforce/chart-lab/README.md ("Open type (open-drive,
open-test-drive, open-rejection-reverse, open-auction)"). Classifies how the
session opened by the close of the initial balance (10:30 ET, 60 minutes)
and leans with the resolved direction for the rest of the session. A fourth
type, open-auction (price stays in a tight rotational range through the
IB), is not tested here: it has no directional resolution by definition, so
there is nothing for a with/fade backtest to lean on.

Classification at the IB close (bar 11), using the IB's own excursions
against the day's ATR (s.atr[11]) as the yardstick:
  open-drive             price never moves more than 0.15 ATR against its
                         own eventual direction through the IB and closes
                         the IB at least 0.75 ATR from the open: a one-way
                         session from the bell.
  open-test-drive        the IB's extreme against the eventual direction
                         happened in the first 15 minutes (a quick test), at
                         least 0.35 ATR from the open, and the IB then
                         closed at least 0.35 ATR beyond the open the other
                         way: the test failed fast and the session drove off.
  open-rejection-reverse the same shape as open-test-drive but the test can
                         land anywhere in the IB (not just the first 15
                         minutes) and the close only needs to clear 0.15 ATR
                         beyond the open: a slower, less clean rejection.
Every session gets at most one type (checked in that order) and fires once,
at the IB close, leaning with the resolved direction.
"""


def _classify(s):
    b = s.bars
    o = s.open
    a = s.atr[11]
    if not a:
        return None
    ib = b[:12]
    hi = max(x.h for x in ib) - o
    lo = o - min(x.l for x in ib)
    close = b[11].c - o
    or3 = b[:3]
    or_hi = max(x.h for x in or3) - o
    or_lo = o - min(x.l for x in or3)

    if close >= 0.75 * a and lo <= 0.15 * a:
        return 'open_drive', 1
    if close <= -0.75 * a and hi <= 0.15 * a:
        return 'open_drive', -1
    if or_lo >= 0.35 * a and close >= 0.35 * a:
        return 'open_test_drive', 1
    if or_hi >= 0.35 * a and close <= -0.35 * a:
        return 'open_test_drive', -1
    if lo >= 0.35 * a and close >= 0.15 * a:
        return 'open_rejection_reverse', 1
    if hi >= 0.35 * a and close <= -0.15 * a:
        return 'open_rejection_reverse', -1
    return None


def open_drive(s):
    r = _classify(s)
    if r and r[0] == 'open_drive':
        yield 11, r[1]


def open_test_drive(s):
    r = _classify(s)
    if r and r[0] == 'open_test_drive':
        yield 11, r[1]


def open_rejection_reverse(s):
    r = _classify(s)
    if r and r[0] == 'open_rejection_reverse':
        yield 11, r[1]


SETUPS = [
    dict(id='open_drive', name='Open type: open-drive', family='session/gaps', detect=open_drive,
         rules="The session never moves more than 0.15 ATR against its own eventual direction through the "
               "initial balance (60 minutes) and closes the IB at least 0.75 ATR from the open: a one-way "
               "drive from the bell. Leans with the drive."),
    dict(id='open_test_drive', name='Open type: open-test-drive', family='session/gaps', detect=open_test_drive,
         rules="The first 15 minutes test at least 0.35 ATR opposite the eventual direction, then the IB "
               "closes at least 0.35 ATR beyond the open the other way: a fast-failing test followed by a "
               "drive. Leans with the drive."),
    dict(id='open_rejection_reverse', name='Open type: open-rejection-reverse', family='session/gaps',
         detect=open_rejection_reverse,
         rules="Anywhere in the initial balance price tests at least 0.35 ATR one way, then the IB closes at "
               "least 0.15 ATR the other way: a slower, less clean rejection than open-test-drive. Leans with "
               "the reversal."),
]
