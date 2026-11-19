"""Multi-day value migration: trade with value when two sessions' profiles stepped the same way.
Added 2026-10-04 by volume-vwap-analyst: volume profile family, from the Market Profile idea that
value moving higher day over day (higher POC, VAH and VAL) shows acceptance at new prices and favours
continuation (Dalton, "Mind Over Markets"; CME Group profile primers). poc_migration tests the POC move
alone; this requires the whole value area to step. Parameters fixed BEFORE any P&L was seen: yesterday's
POC, VAH and VAL are all higher (lower) than the session before's; signal at the 10:30 close (bar 11)
if price is above (below) yesterday's POC and today's VWAP; one per session. The lab tests it with and
against (against = the "migration gets overextended" reading).
"""


def value_migration_trend(s):
    p = s.prior
    if p is None or p.prior is None:
        return
    q = p.prior
    b = s.bars
    if len(b) < 13:
        return
    if p.poc > q.poc and p.vah > q.vah and p.val > q.val:
        d = 1
    elif p.poc < q.poc and p.vah < q.vah and p.val < q.val:
        d = -1
    else:
        return
    if d * (b[11].c - p.poc) > 0 and d * (b[11].c - s.vwap[11]) > 0:
        yield 11, d


SETUPS = [
    dict(id='value_migration_trend', name='Value migrating: two-day step in POC, VAH and VAL', family='volume profile',
         detect=value_migration_trend,
         rules="Yesterday's POC, value area high and value area low are all higher (or all lower) than the "
               "session before's. At the 10:30 close, if price is on that side of yesterday's POC and of "
               "today's VWAP, lean with the migration. Once per session, tested with and against."),
]
