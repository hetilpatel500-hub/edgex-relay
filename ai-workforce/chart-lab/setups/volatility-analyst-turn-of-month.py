"""Turn-of-the-month seasonal on daily bars.
Added 2026-10-04 by volatility-analyst via WebSearch (documented calendar anomaly: index returns
cluster around the month change as pension/fund flows arrive). Rule fixed BEFORE any P&L was
seen: long only, signal at the close of the second-to-last trading day of each calendar month
(the lab enters at the next open), no other filter. The lab tests it with and against.
"""


def tom_long(ser):
    n = len(ser.c)
    for i in range(1, n - 2):
        if ser.day[i + 1].month == ser.day[i].month and ser.day[i + 2].month != ser.day[i].month:
            yield i, 1


SETUPS = [
    dict(id='d_turn_of_month', tf='D', name='Turn of the month (long)', family='seasonal (daily)',
         detect=tom_long,
         rules="Buy the close of the second-to-last trading day of each month and hold per the lab's "
               "exit; no other condition."),
]
