"""Time-of-day filter study: does restricting to before 11:00 change a setup's edge?
Added 2026-09-28 by risk-manager: next open line of the research queue in
ai-workforce/chart-lab/README.md ("Time-of-day filter study: which setups
only work before 11:00"). The lab's method picks ONE filter and ONE exit per
setup from the existing FILTERS table (vwap, rvol, ppoc, trend and their
pairs); none of those is a time-of-day filter, so this idea can't be tested
by adding a filter to an existing setup file -- it has to be its own
detector with the time window baked into detect() itself. A full sweep of
"every setup restricted to before 11:00" isn't possible without changing
lab.py's filter engine, which is out of scope for a setups/ file (core.py
and lab.py are the fixed method, never edited to chase a result). Instead
this tests the two clearest candidates for a real time-of-day effect: the
two structure setups already in the lab (intraday.py's bos and choch, both
read straight from core.py's precomputed s.event/s.trend, no new logic
duplicated) restricted to signals whose bar closes before 11:00 ET, instead
of their normal 10:00-15:00 window. If continuation or reversal off the
protected level is really an early-session phenomenon (opening-drive
follow-through fades by midday), narrowing the window should show it.
"""


def bos_before1100(s):
    n = 0
    for i, ev in enumerate(s.event):
        if not (600 <= s.bars[i].m < 660) or n >= 3:
            continue
        if ev == 'bos_up' and s.trend[i - 1] == 1:
            n += 1; yield i, 1
        elif ev == 'bos_dn' and s.trend[i - 1] == -1:
            n += 1; yield i, -1


def choch_before1100(s):
    for i, ev in enumerate(s.event):
        if not (600 <= s.bars[i].m < 660):
            continue
        if ev == 'choch_up':
            yield i, 1
        elif ev == 'choch_dn':
            yield i, -1


SETUPS = [
    dict(id='bos_before1100', name='Break of structure (continuation), before 11:00 only', family='time of day',
         detect=bos_before1100,
         rules="Same event as bos (close beyond the last swing in the trend's direction) but only counted "
               "when the break closes before 11:00 ET, instead of the usual 10:00-15:00 window."),
    dict(id='choch_before1100', name='Change of character, before 11:00 only', family='time of day',
         detect=choch_before1100,
         rules="Same event as choch (the protected swing that held the trend is closed through) but only "
               "counted when it closes before 11:00 ET, instead of the usual 10:00-15:00 window."),
]
