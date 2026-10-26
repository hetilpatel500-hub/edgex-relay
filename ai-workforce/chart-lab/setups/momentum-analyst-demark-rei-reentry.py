"""DeMark Range Expansion Index (REI, 5 bars) re-entry from +/-45, 5-minute bars.
Added 2026-10-12 by momentum-analyst via WebSearch (Tom DeMark, "DeMark on Day Trading Options", 1999, as described by
ProRealCode: five-bar summation, output -100..+100, 45 / -45 read as overbought / oversold, a bar's value is zeroed when
the high two bars back sits below the close 7-8 bars back and today's high below the low 5-6 bars back, or the mirror
on the low side). The exact zeroing tests are the lab's reading of that description; the source gives no entry rule.
Parameters fixed BEFORE any P&L was seen: 5-bar sum, +/-45, built inside the session (needs 9 bars), signal when REI
crosses back inside the band, 10:00 to 14:30 ET, at most 2 signals per side per session. Everything is known at the
signal bar's close.
"""


def demark_rei_reentry(s):
    b = s.bars
    n = len(b)
    num, den = [0.0] * n, [0.0] * n
    for i in range(8, n):
        h2, l2 = b[i - 2].h, b[i - 2].l
        dh, dl = b[i].h - h2, b[i].l - l2
        c1 = h2 < b[i - 7].c and h2 < b[i - 8].c and b[i].h < b[i - 5].l and b[i].h < b[i - 6].l
        c2 = l2 > b[i - 7].c and l2 > b[i - 8].c and b[i].l > b[i - 5].h and b[i].l > b[i - 6].h
        den[i] = abs(dh) + abs(dl)
        num[i] = 0.0 if (c1 or c2) else dh + dl
    rei = [0.0] * n
    for i in range(12, n):
        d = sum(den[i - 4:i + 1])
        rei[i] = 100 * sum(num[i - 4:i + 1]) / d if d else 0.0
    cnt = {1: 0, -1: 0}
    for i in range(13, n):
        if b[i].m < 600 or b[i].m >= 870:
            continue
        if rei[i - 1] <= -45 < rei[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif rei[i - 1] >= 45 > rei[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='demark_rei_reentry', name='DeMark Range Expansion Index re-entry from +/-45', family='momentum',
         detect=demark_rei_reentry,
         rules="Tom DeMark's 5-bar Range Expansion Index (high and low moves two bars apart, zeroed when the bar "
               "gaps away from the range of 5-8 bars ago). When it climbs back above -45 from oversold the setup "
               "leans long; when it drops back below +45 from overbought it leans short. 10:00 to 14:30 ET, at "
               "most two signals per side per session; tested with and against."),
]
