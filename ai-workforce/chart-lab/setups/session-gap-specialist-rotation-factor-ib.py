"""Rotation factor of the initial balance (Dalton, Mind Over Markets).
Added 2026-10-05 by session-gap-specialist: web-sourced idea (Dalton's rotation factor: each bar scores +1 for a
higher high or higher low, -1 for a lower high or lower low, summed over the first hour). Rules fixed BEFORE any
P&L was seen: IB = first 12 five-minute bars, |RF| >= 6 of a maximum 22, first close beyond the IB extreme
in the RF direction between 10:30 and 15:00 trades with the rotation.
"""


def rotation_factor_break(s):
    b = s.bars
    if len(b) < 14:
        return
    rf = 0
    for i in range(1, 12):
        rf += (b[i].h > b[i - 1].h) - (b[i].h < b[i - 1].h)
        rf += (b[i].l > b[i - 1].l) - (b[i].l < b[i - 1].l)
    if abs(rf) < 6:
        return
    d = 1 if rf > 0 else -1
    for i in range(12, len(b)):
        if b[i].m >= 900:
            break
        if (d == 1 and b[i].c > s.ib_hi) or (d == -1 and b[i].c < s.ib_lo):
            yield i, d
            return


SETUPS = [
    dict(id='rotation_factor_ib_break', name='Rotation factor IB break', family='session / initial balance',
         detect=rotation_factor_break,
         rules="Score each of the first hour's 5-minute bars +1 for a higher high, -1 for a lower high, and the same "
               "for the low (Dalton's rotation factor). If the total is +6 or more (or -6 or less), the first close "
               "beyond the initial-balance high (low) after 10:30 and before 15:00 leans long (short) with that "
               "one-sided rotation."),
]
