"""VSA no-demand / no-supply bar with a confirming bar, 5-minute bars.
Added 2026-10-12 by wyckoff-phase-analyst via WebSearch (Volume Spread Analysis no-demand / no-supply bars as defined by
LuxAlgo's indicator library and the TradingView "No Supply/Demand bars" script, which add a rejection wick and a confirming
next bar; ProRealCode's TAC VSA uses a looser version). Sources are indicator descriptions with no performance evidence.
Distinct from squat_bar_reversal and effort_no_result (those need high volume with little result; this is LOW volume with a
narrow spread).
Parameters fixed BEFORE any P&L was seen: signal bar i (between 10:45 and 14:55 ET) has spread < 0.7 x the mean spread of
the 20 bars before it, volume below both of the two bars before it, and a wick of at least 30% of its range on the rejection
side. No demand: closes up (c > o), upper wick >= 30% of range; the next bar i+1 closes down (c < o) and below bar i's close.
Signal short at the close of i+1. No supply is the mirror (closes down, lower wick >= 30%, next bar closes up above bar i's
close; signal long). One signal per side per session. No VWAP or other filter.
"""


def no_demand_supply(s):
    b = s.bars
    done = {1: False, -1: False}
    for i in range(21, len(b) - 1):
        j = i + 1                                    # confirming bar; the signal is known at its close
        if b[j].m < 645 or b[j].m + 5 > 900:
            continue
        x = b[i]
        rng = x.h - x.l
        if rng <= 0:
            continue
        avg = sum(y.h - y.l for y in b[i - 20:i]) / 20
        if rng >= 0.7 * avg or x.v >= b[i - 1].v or x.v >= b[i - 2].v:
            continue
        c = b[j]
        if not done[-1] and x.c > x.o and (x.h - max(x.o, x.c)) >= 0.3 * rng and c.c < c.o and c.c < x.c:
            done[-1] = True; yield j, -1
        elif not done[1] and x.c < x.o and (min(x.o, x.c) - x.l) >= 0.3 * rng and c.c > c.o and c.c > x.c:
            done[1] = True; yield j, 1


SETUPS = [
    dict(id='no_demand_no_supply', name="VSA no-demand / no-supply bar, confirmed", family='wyckoff',
         detect=no_demand_supply,
         rules="A narrow-spread bar on lower volume than the two bars before it, with a wick rejecting the move "
               "(up bar with an upper wick = no demand; down bar with a lower wick = no supply). When the next bar "
               "closes the other way beyond the signal bar's close, that is the signal: short after no demand, long "
               "after no supply. Between 10:45 and 15:00 ET, one per side per session; tested with and against."),
]
