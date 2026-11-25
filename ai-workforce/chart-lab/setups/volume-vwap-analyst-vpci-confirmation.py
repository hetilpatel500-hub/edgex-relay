"""Volume Price Confirmation Indicator (VPCI 5/20) turning positive, 5-minute session bars.
Added 2026-10-14 by volume-vwap-analyst via WebSearch (Buff Dormeier, CMT Association write-up of the VPCI; community
versions use short 5 / long 20 bars). The lab has no VPCI. Formula as published: VPC = long VWMA - long SMA,
VPR = short VWMA / short SMA, VM = short average volume / long average volume, VPCI = VPC * VPR * VM.
Rules fixed BEFORE any P&L was seen: windows 5 and 20 bars of the same session (restarts each day, so the first
signal can come after bar 20); closes are the price series. Signal on the bar where VPCI crosses from at-or-below
zero to above zero (volume confirming the move), direction = which side of the 20-bar SMA the close is on, and only
if the close is on the same side of session VWAP. 10:00 to 15:00 ET, at most two a session.
"""


def vpci_confirmation(s):
    b = s.bars
    n = len(b)
    S, L = 5, 20
    if n < L + 2:
        return
    fired = 0
    prev = None
    for i in range(L - 1, n):
        lc = [x.c for x in b[i - L + 1:i + 1]]
        lv = [x.v for x in b[i - L + 1:i + 1]]
        sc, sv = lc[-S:], lv[-S:]
        if sum(lv) <= 0 or sum(sv) <= 0:
            prev = None
            continue
        lsma = sum(lc) / L
        ssma = sum(sc) / S
        lvw = sum(c * v for c, v in zip(lc, lv)) / sum(lv)
        svw = sum(c * v for c, v in zip(sc, sv)) / sum(sv)
        vpc = lvw - lsma
        vpr = svw / ssma
        vm = (sum(sv) / S) / (sum(lv) / L)
        x = vpc * vpr * vm
        p, prev = prev, x
        if p is None or b[i].m < 600 or b[i].m >= 900 or fired >= 2:
            continue
        if p <= 0 < x:
            c = b[i].c
            if c > lsma and c > s.vwap[i]:
                fired += 1; yield i, 1
            elif c < lsma and c < s.vwap[i]:
                fired += 1; yield i, -1


SETUPS = [
    dict(id='vpci_confirmation', name='Volume Price Confirmation Indicator (5/20) turns positive', family='volume',
         detect=vpci_confirmation,
         rules="VPCI = (20-bar VWMA minus SMA) x (5-bar VWMA / SMA) x (5-bar volume / 20-bar volume), per session. "
               "When it crosses above zero, lean toward the side of the 20-bar average the close is on, if session "
               "VWAP agrees, 10:00 to 15:00 ET, at most two a session. Tested with and against."),
]
