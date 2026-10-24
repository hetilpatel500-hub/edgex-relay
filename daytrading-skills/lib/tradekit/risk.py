"""Risk guard: hard daily limits checked before every trade."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, time
from pathlib import Path

import pandas as pd

DEFAULTS = {
    "account_size": 25_000,
    "max_risk_per_trade_pct": 1.0,
    "max_daily_loss_pct": 3.0,
    "max_daily_loss_dollars": None,
    "max_trades_per_day": 6,
    "max_consecutive_losses": 3,
    "cooldown_minutes": 30,
    "max_open_positions": 3,
    "max_total_open_risk_pct": 3.0,
    "min_reward_risk": 1.5,
    "no_trade_windows": ["09:30-09:35", "15:55-16:00"],
    "protect_profits_after_dollars": None,
    "max_giveback_pct": 50,
    "pdt_threshold": 25_000,
    "pdt_max_day_trades": 3,
}


def default_path() -> Path:
    from .cli import home  # noqa: PLC0415

    return home() / "risk.json"


def load_config(path: Path | None = None) -> dict:
    path = path or default_path()
    cfg = dict(DEFAULTS)
    if path.exists():
        cfg.update(json.loads(path.read_text()))
        cfg["_configured"] = True
    else:
        cfg["_configured"] = False
    return cfg


def save_config(cfg: dict, path: Path | None = None) -> Path:
    path = path or default_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({k: v for k, v in cfg.items() if not k.startswith("_")}, indent=2) + "\n")
    return path


def daily_loss_limit(cfg: dict) -> float:
    lim = cfg["account_size"] * cfg["max_daily_loss_pct"] / 100
    if cfg.get("max_daily_loss_dollars"):
        lim = min(lim, float(cfg["max_daily_loss_dollars"]))
    return lim


@dataclass
class DayState:
    day: date
    realized: float = 0.0
    peak: float = 0.0
    trades: int = 0
    consecutive_losses: int = 0
    last_loss_at: datetime | None = None
    open_positions: int = 0
    open_risk: float = 0.0
    day_trades_5d: int = 0
    open_symbols: list[str] = field(default_factory=list)


def day_state(journal: pd.DataFrame, today: date) -> DayState:
    st = DayState(today)
    if journal is None or len(journal) == 0:
        return st
    j = journal[journal["entry_time"].notna()].sort_values("entry_time")
    td = j[j["date"] == today]
    closed = td[td["status"] == "closed"]
    st.trades = len(td)
    eq = closed.sort_values("exit_time")["pnl"].cumsum()
    st.realized = float(eq.iloc[-1]) if len(eq) else 0.0
    st.peak = float(max(0.0, eq.max())) if len(eq) else 0.0
    streak = 0
    for _, r in closed.sort_values("exit_time").iterrows():
        if r["pnl"] <= 0:
            streak += 1
            st.last_loss_at = r["exit_time"]
        else:
            streak = 0
    st.consecutive_losses = streak
    op = j[j["status"] == "open"]
    st.open_positions = len(op)
    st.open_risk = float(op["risk"].fillna(0).sum())
    st.open_symbols = list(op["symbol"])
    bdays = pd.bdate_range(end=pd.Timestamp(today), periods=5).date
    same_day = j[(j["status"] == "closed") & j["exit_time"].notna()]
    same_day = same_day[same_day["exit_time"].dt.date == same_day["date"]]
    st.day_trades_5d = int(same_day["date"].isin(bdays).sum())
    return st


def _in_window(t: time, spec: str) -> bool:
    a, b = spec.split("-")
    ta = datetime.strptime(a.strip(), "%H:%M").time()
    tb = datetime.strptime(b.strip(), "%H:%M").time()
    return ta <= t < tb


def check(cfg: dict, st: DayState, now: datetime, entry: float | None = None, stop: float | None = None,
          shares: float | None = None, target: float | None = None, side: str | None = None,
          point_value: float = 1.0, symbol: str | None = None) -> dict:
    """Return BLOCKED / CAUTION / CLEAR with every rule's result."""
    blocks, cautions, ok = [], [], []
    acct = float(cfg["account_size"])
    limit = daily_loss_limit(cfg)

    remaining = limit + st.realized  # realized is negative when losing
    if st.realized <= -limit:
        blocks.append(f"daily loss limit hit: {st.realized:+,.2f} vs -{limit:,.2f}. Done for the day.")
    else:
        ok.append(f"daily P&L {st.realized:+,.2f}; {remaining:,.2f} left before the {limit:,.2f} daily stop")

    if st.trades >= cfg["max_trades_per_day"]:
        blocks.append(f"{st.trades} trades today hits the max of {cfg['max_trades_per_day']}")
    else:
        ok.append(f"trade {st.trades + 1} of {cfg['max_trades_per_day']} allowed today")

    if st.consecutive_losses >= cfg["max_consecutive_losses"]:
        if st.last_loss_at is not None:
            mins = (pd.Timestamp(now).tz_localize(None) - pd.Timestamp(st.last_loss_at).tz_localize(None)
                    ).total_seconds() / 60
        else:
            mins = 0
        wait = cfg["cooldown_minutes"] - mins
        if wait > 0:
            blocks.append(f"{st.consecutive_losses} losses in a row: cooldown for {wait:.0f} more minutes")
        else:
            cautions.append(f"{st.consecutive_losses} losses in a row; cooldown is over, but size down")

    if st.open_positions >= cfg["max_open_positions"]:
        blocks.append(f"already {st.open_positions} open positions (max {cfg['max_open_positions']})")
    if symbol and symbol.upper() in [s.upper() for s in st.open_symbols]:
        cautions.append(f"already holding {symbol.upper()}: this adds to the position")

    if cfg.get("protect_profits_after_dollars") and st.peak >= float(cfg["protect_profits_after_dollars"]):
        floor = st.peak * (1 - cfg["max_giveback_pct"] / 100)
        if st.realized <= floor:
            blocks.append(f"gave back {cfg['max_giveback_pct']}% of today's peak {st.peak:+,.2f}: lock in the day")
        else:
            cautions.append(f"protect the green day: stop trading if P&L falls to {floor:+,.2f}")

    t = now.time() if isinstance(now, datetime) else now
    for w in cfg.get("no_trade_windows", []):
        if _in_window(t, w):
            blocks.append(f"{t:%H:%M} is inside the no-trade window {w}")

    if acct < cfg["pdt_threshold"] and st.day_trades_5d >= cfg["pdt_max_day_trades"]:
        cautions.append(f"{st.day_trades_5d} day trades in 5 business days with an account under "
                        f"{cfg['pdt_threshold']:,}: check your broker's pattern-day-trader rules first")

    trade = {}
    if entry is not None and stop is not None:
        risk_unit = abs(entry - stop) * point_value
        if risk_unit == 0:
            blocks.append("stop equals entry")
        else:
            if side is not None and (1 if side == "long" else -1) * (entry - stop) <= 0:
                blocks.append(f"a {side} needs its stop {'below' if side == 'long' else 'above'} the entry")
            max_risk = acct * cfg["max_risk_per_trade_pct"] / 100
            cap = acct * cfg["max_total_open_risk_pct"] / 100
            allowed = max(0.0, min(max_risk, remaining, cap - st.open_risk))
            trade["max_units_allowed"] = int(allowed // risk_unit)
            if shares is not None:
                risk = risk_unit * shares
                trade["risk"] = risk
                if risk > max_risk + 1e-9:
                    blocks.append(f"risk {risk:,.2f} is over the per-trade max {max_risk:,.2f} "
                                  f"({cfg['max_risk_per_trade_pct']}%); max size {trade['max_units_allowed']}")
                elif risk > remaining:
                    blocks.append(f"a full stop-out ({risk:,.2f}) would blow through today's loss limit; "
                                  f"max size {trade['max_units_allowed']}")
                else:
                    ok.append(f"risk {risk:,.2f} is within the {max_risk:,.2f} per-trade limit")
                total = st.open_risk + risk
                if total > cap:
                    blocks.append(f"total open risk would be {total:,.2f}, over the {cap:,.2f} cap")
        if target is not None and risk_unit:
            rr = abs(target - entry) * point_value / risk_unit
            trade["reward_risk"] = rr
            d = 1 if (side or ("long" if target > entry else "short")) == "long" else -1
            if d * (target - entry) <= 0 or d * (entry - stop) <= 0:
                blocks.append("stop and target are on the wrong sides of the entry for this direction")
            elif rr < cfg["min_reward_risk"]:
                cautions.append(f"reward:risk {rr:.2f} is under your minimum {cfg['min_reward_risk']}")
            else:
                ok.append(f"reward:risk {rr:.2f}")
    elif entry is not None:
        blocks.append("no stop: every trade needs a stop before entry")

    verdict = "BLOCKED" if blocks else "CAUTION" if cautions else "CLEAR"
    return {"verdict": verdict, "blocked": blocks, "cautions": cautions, "ok": ok, "trade": trade,
            "state": {"realized": st.realized, "peak": st.peak, "trades": st.trades,
                      "consecutive_losses": st.consecutive_losses, "open_positions": st.open_positions,
                      "open_risk": st.open_risk, "day_trades_5d": st.day_trades_5d,
                      "daily_loss_limit": limit}}
