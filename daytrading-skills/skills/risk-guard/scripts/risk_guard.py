#!/usr/bin/env python3
"""Risk guard: daily loss limits, trade caps, cooldowns and a pre-trade check.

Examples
  risk_guard.py init --account 30000 --max-daily-loss-pct 2 --max-trades 5
  risk_guard.py status
  risk_guard.py check --symbol AAPL --side long --entry 187.5 --stop 186.2 --shares 200 --target 190.1
Reads today's trades from the trade-journal skill's journal.
"""

import sys
from pathlib import Path

_skill = Path(__file__).resolve().parents[1]  # engine is vendored in packaged skills, shared in the plugin
sys.path.insert(0, str(_skill / "lib" if (_skill / "lib").is_dir() else _skill.parents[1] / "lib"))

from tradekit.cli import run  # noqa: E402


def main():
    import argparse

    from tradekit import journal as jr, risk as rk
    from tradekit.report import emit_json, money
    from tradekit.session import now_in, parse_hhmm

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", help="risk settings JSON (default ~/.daytrading-skills/risk.json)")
    p.add_argument("--journal", help="journal CSV (default ~/.daytrading-skills/journal.csv)")
    p.add_argument("--tz", default="America/New_York")
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="create or update your limits")
    i.add_argument("--account", type=float)
    i.add_argument("--max-risk-pct", type=float, help="per-trade risk, %% of account")
    i.add_argument("--max-daily-loss-pct", type=float)
    i.add_argument("--max-daily-loss", type=float, help="daily loss cap in dollars")
    i.add_argument("--max-trades", type=int)
    i.add_argument("--max-losses-in-row", type=int)
    i.add_argument("--cooldown", type=int, help="minutes to sit out after the losing streak")
    i.add_argument("--max-open", type=int)
    i.add_argument("--max-open-risk-pct", type=float)
    i.add_argument("--min-rr", type=float)
    i.add_argument("--no-trade", help="comma list of HH:MM-HH:MM windows")
    i.add_argument("--protect-after", type=float, help="once up this many dollars, cap the giveback")
    i.add_argument("--max-giveback-pct", type=float)
    i.add_argument("--show", action="store_true", help="print the settings without changing them")

    sub.add_parser("status", help="today's usage of every limit")

    c = sub.add_parser("check", help="pre-trade check")
    c.add_argument("--symbol")
    c.add_argument("--side", choices=["long", "short"])
    c.add_argument("--entry", type=float)
    c.add_argument("--stop", type=float)
    c.add_argument("--target", type=float)
    c.add_argument("--shares", type=float)
    c.add_argument("--point-value", type=float, default=1.0)
    c.add_argument("--time", help="HH:MM to check against (default now)")
    args = p.parse_args()

    cfg_path = Path(args.config).expanduser() if args.config else rk.default_path()
    cfg = rk.load_config(cfg_path)

    if args.cmd == "init":
        if not args.show:
            mapping = {
                "account": "account_size", "max_risk_pct": "max_risk_per_trade_pct",
                "max_daily_loss_pct": "max_daily_loss_pct", "max_daily_loss": "max_daily_loss_dollars",
                "max_trades": "max_trades_per_day", "max_losses_in_row": "max_consecutive_losses",
                "cooldown": "cooldown_minutes", "max_open": "max_open_positions",
                "max_open_risk_pct": "max_total_open_risk_pct", "min_rr": "min_reward_risk",
                "protect_after": "protect_profits_after_dollars", "max_giveback_pct": "max_giveback_pct",
            }
            for arg, key in mapping.items():
                v = getattr(args, arg)
                if v is not None:
                    cfg[key] = v
            if args.no_trade is not None:
                cfg["no_trade_windows"] = [w.strip() for w in args.no_trade.split(",") if w.strip()]
            path = rk.save_config(cfg, cfg_path)
            print(f"saved {path}")
        for k, v in cfg.items():
            if not k.startswith("_"):
                print(f"  {k}: {v}")
        return 0

    jpath = Path(args.journal).expanduser() if args.journal else jr.default_path()
    journal = jr.load(jpath)
    now = now_in(args.tz)
    if args.cmd == "check" and args.time:
        t = parse_hhmm(args.time)
        now = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
    st = rk.day_state(journal, now.date())
    naive_now = now.tz_localize(None).to_pydatetime()

    if args.cmd == "status":
        res = rk.check(cfg, st, naive_now)
    else:
        res = rk.check(cfg, st, naive_now, args.entry, args.stop, args.shares, args.target, args.side,
                       args.point_value, args.symbol)
    res["configured"] = cfg["_configured"]

    if args.json:
        emit_json(res)
        return 0 if res["verdict"] != "BLOCKED" else 1

    s = res["state"]
    icon = {"CLEAR": "✅", "CAUTION": "⚠️ ", "BLOCKED": "⛔"}[res["verdict"]]
    title = "RISK STATUS" if args.cmd == "status" else "PRE-TRADE CHECK"
    print(f"{title} · {now:%Y-%m-%d %H:%M} · {icon} {res['verdict']}")
    print(f"Today: P&L {money(s['realized'])} (peak {money(s['peak'])}) · {s['trades']} trades · "
          f"{s['consecutive_losses']} losses in a row · {s['open_positions']} open "
          f"({money(s['open_risk'])} at risk) · daily stop {money(-s['daily_loss_limit'])}")
    for b in res["blocked"]:
        print(f"  ⛔ {b}")
    for c_ in res["cautions"]:
        print(f"  ⚠  {c_}")
    for o in res["ok"]:
        print(f"  ✓ {o}")
    if "max_units_allowed" in res["trade"]:
        print(f"  max size allowed right now: {res['trade']['max_units_allowed']:,}")
    if not cfg["_configured"]:
        print("  (using default limits: run `risk_guard.py init --account <size>` to set your own)")
    return 0 if res["verdict"] != "BLOCKED" else 1


if __name__ == "__main__":
    run(main)
