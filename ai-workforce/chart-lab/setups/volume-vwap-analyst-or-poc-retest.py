"""Opening-range volume-profile POC retest after a breakout, 5-minute session bars.
Added 2026-10-15 by volume-vwap-analyst via WebSearch (TradingView opening-range scripts that apply a volume profile to the
opening range itself, to see where the heaviest trading sat before a breakout; the pages publish no backtest). The lab
tests opening-range breaks and the developing/prior-day POC, but not the POC of the opening range as a retest level.
Fixed BEFORE any P&L was seen: opening range = first 30 minutes (bars 0-5); its POC from core.profile on those 6 bars
(5 bp bins, volume spread over each bar's range). A breakout is the first close beyond the 30-minute high (low) after
bar 5. After a breakout, a later bar (before 14:00 ET) whose low (high) trades down (up) to the OR POC and that closes
back above (below) the POC on a candle in the breakout direction signals a long (short). One signal per side per session.
"""
import core


def or_poc_retest(s):
    b = s.bars
    if len(b) < 12:
        return
    poc = core.profile(b[:6])[0]
    hi = max(x.h for x in b[:6]); lo = min(x.l for x in b[:6])
    up_at = dn_at = None
    done = {1: False, -1: False}
    for i in range(6, len(b)):
        if b[i].m + 5 > 840:
            break
        if up_at is None and b[i].c > hi:
            up_at = i
        if dn_at is None and b[i].c < lo:
            dn_at = i
        if up_at is not None and i > up_at and not done[1] and b[i].l <= poc and b[i].c > poc and b[i].c > b[i].o:
            done[1] = True; yield i, 1
        if dn_at is not None and i > dn_at and not done[-1] and b[i].h >= poc and b[i].c < poc and b[i].c < b[i].o:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='or_poc_retest', name='Opening-range POC retest after a breakout', family='volume',
         detect=or_poc_retest,
         rules="Take the volume profile of the first 30 minutes and its point of control. After price closes beyond the "
               "30-minute high (low), a later bar before 14:00 ET that dips (pokes) back to the opening-range POC and "
               "closes back above (below) it on a candle in the breakout direction signals a long (short). One signal "
               "per side per session. Tested with and against."),
]
