"""Turnaround Tuesday on daily bars.
Added 2026-10-04 by volatility-analyst: the research queue held only tape items, so this run took the documented
"Turnaround Tuesday" rule found by WebSearch (quantifiedstrategies.substack.com: Monday closes at least 1% below
Friday's close, buy, hold into Tuesday). Rules were fixed BEFORE any P&L was seen: the 1% threshold and the
Monday-only condition are the published ones. The lab enters at Tuesday's open and tests it with and against.
Distinct from d_turn_of_month (calendar only) and d_rsi2_pullback (no day-of-week or size condition).
"""


def turnaround_tuesday(ser):
    """A Monday whose close is at least 1% below the previous trading day's close leans long."""
    for i in range(1, len(ser.c) - 1):
        if ser.day[i].weekday() == 0 and ser.c[i] <= 0.99 * ser.c[i - 1]:
            yield i, 1


SETUPS = [
    dict(id='turnaround_tuesday', tf='D', name='Turnaround Tuesday (Monday down 1%+)', family='seasonal (daily)',
         detect=turnaround_tuesday,
         rules="When a Monday closes at least 1% below the previous trading day's close, lean long at the next "
               "open (Tuesday). One signal per qualifying Monday."),
]
