"""Trade plan: every skill on one trade idea, in one report.

Runs, in order: market context, event flags, the entry checklist, the time
machine (past days at this clock time, and the setup's own history when a
setup is named), the exit planner, and the risk sizer; optionally records
the plan in the journal as a paper trade. The summary states the evidence
and stops there: it never says buy or sell.
"""
import json
from . import (data, context, entry as entry_mod, timemachine as tm, exits, risk, journal as jr, DISCLAIMER)


def trade_plan(store, symbol, side, entry=None, stop=None, target=None, stop_atr=None, target_r=None, account=None,
               risk_pct=1.0, setup=None, results=None, level=None, trigger='break', events=None, ticks=None, book=None,
               flow=None, date=None, time=None, journal=None, setup_dirs=None, paths=10000, target_atr=None):
    symbol = symbol.upper()
    out = {'tool': 'trade-plan', 'generated_at': data.now_utc(), 'symbol': symbol, 'side': side}
    out['market'] = context.context(store, date=date)
    ev = json.load(open(events)) if isinstance(events, str) else events
    out['event_flags'] = [f for f in (ev or {}).get('flags', []) if f.get('symbol') in (symbol, '*')]
    days = tm.time_machine(store, symbol, side, entry, stop, target, stop_atr, target_r, target_atr, date, time, paths=paths)
    out['time_machine_days'] = days
    e, stp, tgt = days['entry'], days['stop'], days['target']
    if setup:
        try:
            out['time_machine_setup'] = tm.time_machine(store, symbol, side, e, stp, tgt, date=date, time=time,
                                                        paths=paths, setup=setup, setup_dirs=setup_dirs, results=results)
        except ValueError as err:
            out['time_machine_setup'] = {'error': str(err)}
    out['entry_checks'] = entry_mod.check(store, symbol, side, setup=setup, level=level, trigger=trigger, stop=stp,
                                          results=results, setup_dirs=setup_dirs, ticks=ticks, book=book, flow=flow,
                                          events=ev, date=date, time=time)
    out['exit_plan'] = exits.plan(store, symbol, side, e, date, time, paths=1500,
                                  setup=setup if 'error' not in out.get('time_machine_setup', {}) else None,
                                  setup_dirs=setup_dirs, results=results)
    best_tm = out.get('time_machine_setup') if setup and 'error' not in out.get('time_machine_setup', {}) else days
    if account:
        out['size'] = risk.size(account, risk_pct, e, stp, tgt, days['atr_5m'], expected_r=best_tm['expected_r'])
    if journal:
        out['journal_entry'] = jr.plan(journal, symbol, side, e, stp, tgt, setup, days['session'],
                                       days['entry_time_et'], best_tm, 'from trade-plan', 'paper',
                                       out.get('size', {}).get('shares'))
    s = []
    s.append(f"Market: {out['market']['regime']}.")
    for f in out['event_flags']:
        s.append(f"Event [{f['severity']}]: {f['flag']}.")
    if tgt is None:
        s.append('No target given: every path is held to the close (or the stop), so only the stop odds and the '
                 'expected result are meaningful.')
        s.append(f"Past days at {days['entry_time_et']} ET: stop hit {days['odds']['stop_first']:.0%} vs coin flip "
                 f"{days['coin_flip_baseline']['odds']['stop_first']:.0%}; expected {days['expected_r']:+.2f}R.")
    else:
        s.append(f"Past days at {days['entry_time_et']} ET: target first {days['odds']['target_first']:.0%} vs coin flip "
                 f"{days['coin_flip_baseline']['odds']['target_first']:.0%}; expected {days['expected_r']:+.2f}R.")
    tsu = out.get('time_machine_setup')
    if tsu and 'error' not in tsu:
        s.append(f"{setup}'s own {tsu['memory']['signals_used']} past signals: target first {tsu['odds']['target_first']:.0%} "
                 f"vs coin flip {tsu['coin_flip_baseline']['odds']['target_first']:.0%}; expected {tsu['expected_r']:+.2f}R "
                 f"(90% range {tsu['expected_r_range_90'][0]:+.2f} to {tsu['expected_r_range_90'][1]:+.2f}).")
    elif tsu:
        s.append(f"Setup history: {tsu['error']}.")
    ec = out['entry_checks']
    against = [c['check'] for c in ec['checks'] if c['result'] == 'fail']
    s.append(f"Entry checklist: {ec['status']}" + (f" (against: {', '.join(against)})." if against else '.'))
    s.append(f"Exit planner: {out['exit_plan']['summary']}")
    if out.get('size'):
        z = out['size']
        s.append(f"Size at {risk_pct}% risk: {z['shares']} shares, ${z['risk_usd']:,.2f} at risk" +
                 (f"; {z['warnings'][0]}" if z['warnings'] else '') + '.')
    s.append('This is a summary of the evidence, not a recommendation to trade.')
    out['summary'] = s
    out['disclaimer'] = DISCLAIMER
    return out


def render(r):
    L = [f"TRADE PLAN  {r['symbol']} {r['side']}  entry {r['time_machine_days']['entry']}  stop "
         f"{r['time_machine_days']['stop']}  target {r['time_machine_days']['target']}", '']
    L += [f'- {x}' for x in r['summary']]
    L += ['', tm.render(r['time_machine_days'])]
    if r.get('time_machine_setup') and 'error' not in r['time_machine_setup']:
        L += ['', tm.render(r['time_machine_setup'])]
    L += ['', entry_mod.render(r['entry_checks']), '', exits.render(r['exit_plan'])]
    if r.get('size'):
        L += ['', risk.render(r['size'])]
    if r.get('journal_entry'):
        L += ['', f"journal: recorded paper plan {r['journal_entry']['id']}"]
    return '\n'.join(L)
