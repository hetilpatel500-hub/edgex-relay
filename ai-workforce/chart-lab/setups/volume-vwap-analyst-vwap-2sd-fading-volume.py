"""VWAP 2-sigma extension on fading volume.
Added 2026-10-06 by volume-vwap-analyst: VWAP deviation scalp from public
day-trading write-ups (fade the +/-2 SD stretch only when volume declines
into the extension and a reversal candle prints). Not on the original
queue; the queue is otherwise fully tested.
"""


def vwap_2sd_fading_volume(s):
    """High pierces the +2 SD VWAP band (low pierces -2 SD), the candle closes
    against the extension (red after up-stretch, green after down-stretch), and
    its volume is below the average of the previous three bars. Fade it."""
    b = s.bars
    fired = 0
    for i in range(4, len(b)):
        if not (600 <= b[i].m < 900) or fired >= 2:
            continue
        x = b[i]
        sd = s.vsd[i]
        if sd <= 0:
            continue
        prev_v = sum(b[j].v for j in range(i - 3, i)) / 3
        if x.v >= prev_v:
            continue
        if x.h > s.vwap[i] + 2 * sd and x.c < x.o:
            fired += 1
            yield i, -1
        elif x.l < s.vwap[i] - 2 * sd and x.c > x.o:
            fired += 1
            yield i, 1


SETUPS = [
    dict(id='vwap_2sd_fading_volume', name='VWAP 2-sigma stretch on fading volume', family='VWAP',
         detect=vwap_2sd_fading_volume,
         rules="A 5-minute bar whose high pierces VWAP +2 sigma (low pierces -2 sigma), closes against the "
               "stretch, on less volume than the average of the previous three bars, leans back toward VWAP. "
               "Up to two signals a session, 10:00 to 15:00."),
]
