#!/usr/bin/env python3
"""Position sizer: how many shares or contracts for a fixed amount of risk.

Examples
  position_sizer.py --account 30000 --risk-pct 1 --entry 187.50 --stop 186.20
  position_sizer.py --risk-dollars 150 --entry 52.10 --stop 51.60 --slippage 0.02
  position_sizer.py --account 10000 --risk-pct 0.5 --symbol MESZ6 --entry 6012.25 --stop 6006.75
With no --account, the account size saved by the risk-guard skill is used.
"""

import sys
from pathlib import Path

_skill = Path(__file__).resolve().parents[1]  # engine is vendored in packaged skills, shared in the plugin
sys.path.insert(0, str(_skill / "lib" if (_skill / "lib").is_dir() else _skill.parents[1] / "lib"))

from tradekit.cli import run  # noqa: E402


def main():
    import argparse

    from tradekit import risk as rk
    from tradekit.report import emit_json, money, table
    from tradekit.sizing import FUTURES, contract_point_value, size_position

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--account", type=float, help="account equity (default: risk-guard config)")
    p.add_argument("--risk-pct", type=float, help="percent of the account to risk (default: config, else 1)")
    p.add_argument("--risk-dollars", type=float, help="fixed dollars to risk instead of a percent")
    p.add_argument("--entry", type=float, required=True)
    p.add_argument("--stop", type=float, required=True)
    p.add_argument("--target", type=float, help="optional target to show reward:risk")
    p.add_argument("--symbol", help="ticker; futures like MESZ6, /MES or MES=F set the point value")
    p.add_argument("--contract", choices=sorted(FUTURES), help="futures root, if the symbol does not say")
    p.add_argument("--point-value", type=float, help="dollars per point per unit (stocks 1)")
    p.add_argument("--lot", type=int, default=1, help="round size down to this lot (default 1)")
    p.add_argument("--max-position-pct", type=float,
                   help="cap notional at this %% of the account (default 100, or none when --buying-power is set)")
    p.add_argument("--buying-power", type=float, help="cap notional at your buying power")
    p.add_argument("--margin", type=float, help="futures: day-trade margin per contract")
    p.add_argument("--commission", type=float, default=0.0, help="commission per share/contract per side")
    p.add_argument("--slippage", type=float, default=0.0, help="expected slippage on the stop, in price units")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    cfg = rk.load_config()
    account = args.account or float(cfg["account_size"])
    risk_pct = args.risk_pct if args.risk_pct is not None else float(cfg["max_risk_per_trade_pct"])
    pv = args.point_value or (FUTURES[args.contract] if args.contract else None) or \
        contract_point_value(args.symbol) or 1.0
    res = size_position(account, args.entry, args.stop, risk_pct=risk_pct, risk_dollars=args.risk_dollars,
                        point_value=pv, lot=args.lot,
                        max_position_pct=args.max_position_pct or (None if args.buying_power else 100.0),
                        buying_power=args.buying_power, margin_per_unit=args.margin,
                        commission_per_unit=args.commission, slippage=args.slippage)
    if args.target:
        res["reward_risk"] = abs(args.target - args.entry) / abs(args.entry - args.stop)
    res.update(account=account, point_value=pv, account_from_config=args.account is None)

    if args.json:
        emit_json(res)
        return 0
    unit = ("contract" if pv != 1.0 else "share") + ("" if res["units"] == 1 else "s")
    side = "long" if args.entry > args.stop else "short"
    print(f"POSITION SIZE · {(args.symbol or '').upper()} {side} @ {args.entry:g}, stop {args.stop:g}")
    src = " (from risk-guard config)" if args.account is None else ""
    budget = money(args.risk_dollars) if args.risk_dollars is not None else f"{risk_pct:g}% = {money(res['risk_budget'])}"
    print(f"Account {money(account, 0)}{src} · risk budget {budget}"
          + (f" · {pv:g} $/point" if pv != 1.0 else ""))
    print()
    print(f"  ➜ {res['units']:,} {unit}   (limited by: {res['binding_constraint']})")
    print(f"    risk if stopped: {money(res['risk_total'])} ({res['risk_pct_of_account']:.2f}% of account)")
    lev = " notional; futures are leveraged" if pv != 1.0 else " of account"
    print(f"    position value:  {money(res['notional'], 0)} ({res['notional_pct_of_account']:.0f}%{lev})")
    if "reward_risk" in res:
        print(f"    reward:risk:     {res['reward_risk']:.2f}")
    print()
    print(table([[f"{r['r']}R", f"{r['price']:.2f}", money(r["pnl"])] for r in res["r_ladder"]],
                ["at", "price", "profit"], "rrr"))
    caps = ", ".join(f"{k} {v:,}" for k, v in res["caps"].items())
    print(f"\n  caps checked: {caps}")
    for w in res["warnings"]:
        print(f"  ! {w}")
    if not cfg.get("_configured") and args.account is None:
        print("  ! using a default $25,000 account; save yours with: risk_guard.py init --account <size>")
    return 0


if __name__ == "__main__":
    run(main)
