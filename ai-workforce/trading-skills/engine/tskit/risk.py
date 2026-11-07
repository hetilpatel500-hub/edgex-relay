"""Risk sizer: how many shares, from the account size and the risk you set.

  shares = (account x risk %) / (entry - stop), rounded down to the lot size,
  then capped so the position is no larger than `max_position_pct` of the
  account (and no larger than buying power, if given).

Also shows the 1R/2R/3R prices, the reward at a given target, the dollar
expectation if a time-machine expected result is passed in, and warnings:
risk above 2% a trade, a stop tighter than half a 5-minute ATR, the daily
loss limit already hit, and accounts under $25,000 (US margin accounts that
size are limited by the pattern-day-trader rule; check your broker's
current rules). It never reads or touches a brokerage account.
"""
import math
from . import data, DISCLAIMER


def size(account, risk_pct, entry, stop, target=None, atr=None, max_position_pct=25.0, buying_power=None, lot=1,
         realized_today=0.0, daily_loss_limit_pct=None, expected_r=None):
    account, risk_pct, entry, stop = float(account), float(risk_pct), float(entry), float(stop)
    if account <= 0 or risk_pct <= 0:
        raise ValueError('account and risk % must be positive')
    d = 1 if entry > stop else -1
    rps = abs(entry - stop)
    if rps == 0:
        raise ValueError('entry and stop are the same price')
    budget = account * risk_pct / 100
    by_risk = math.floor(budget / rps / lot) * lot
    cap_notional = account * max_position_pct / 100
    if buying_power is not None:
        cap_notional = min(cap_notional, float(buying_power))
    by_cap = math.floor(cap_notional / entry / lot) * lot
    shares = max(0, min(by_risk, by_cap))
    warn = []
    if shares < by_risk:
        warn.append(f'capped by position size: {by_risk} shares would put {by_risk * entry / account:.0%} of the '
                    f'account in one trade (limit {max_position_pct:.0f}%)')
    if shares == 0:
        warn.append('the risk budget is smaller than the risk of one share (or one lot)')
    if risk_pct > 2:
        warn.append(f'{risk_pct}% of the account per trade is aggressive; many traders keep it at or under 1%')
    if atr and rps < 0.5 * float(atr):
        warn.append(f'the stop is {rps / float(atr):.2f} 5-minute ATRs away; noise hits stops that tight most of the time')
    if account < 25000:
        warn.append('under $25,000: US margin accounts are limited by the pattern-day-trader rule; check your broker\'s current rules')
    halted = False
    if daily_loss_limit_pct is not None and realized_today <= -account * float(daily_loss_limit_pct) / 100:
        halted = True
        warn.insert(0, f'daily loss limit reached ({realized_today:,.2f} vs -{daily_loss_limit_pct}% of the account): '
                       'the plan says no more trades today')
    risk_usd = shares * rps
    out = {'tool': 'risk-sizer', 'generated_at': data.now_utc(), 'side': 'long' if d == 1 else 'short',
           'entry': entry, 'stop': stop, 'risk_per_share': round(rps, 4),
           'risk_budget_usd': round(budget, 2), 'shares': int(shares), 'risk_usd': round(risk_usd, 2),
           'risk_pct_of_account': round(risk_usd / account * 100, 3), 'position_value_usd': round(shares * entry, 2),
           'position_pct_of_account': round(shares * entry / account * 100, 2),
           'r_levels': {f'{k}R': round(entry + d * k * rps, 4) for k in (1, 2, 3)},
           'halted_by_daily_limit': halted, 'warnings': warn, 'disclaimer': DISCLAIMER}
    if target is not None:
        target = float(target)
        rr = (target - entry) * d / rps
        out['target'] = target
        out['target_r'] = round(rr, 2)
        out['reward_usd_at_target'] = round(shares * (target - entry) * d, 2)
    if expected_r is not None:
        out['expected_usd_from_time_machine'] = round(float(expected_r) * risk_usd, 2)
    return out


def render(r):
    L = [f"RISK SIZER  {r['side']} {r['shares']} shares at {r['entry']}, stop {r['stop']}",
         f"risk ${r['risk_usd']:,.2f} ({r['risk_pct_of_account']}% of the account; budget ${r['risk_budget_usd']:,.2f}), "
         f"position ${r['position_value_usd']:,.2f} ({r['position_pct_of_account']}%)",
         '1R/2R/3R: ' + ', '.join(f'{k} {v}' for k, v in r['r_levels'].items())]
    if 'target' in r:
        L.append(f"target {r['target']} = {r['target_r']}R, ${r['reward_usd_at_target']:,.2f} if reached")
    if 'expected_usd_from_time_machine' in r:
        L.append(f"time-machine expectation: ${r['expected_usd_from_time_machine']:,.2f} per trade like this (an average, not a promise)")
    L += [f'! {w}' for w in r['warnings']] + ['', r['disclaimer']]
    return '\n'.join(L)
