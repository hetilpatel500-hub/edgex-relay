"""A plain-CSV trade journal and the statistics that make it useful."""

from __future__ import annotations

import csv
import math
import uuid
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .data import DEFAULT_TZ, parse_times

FIELDS = [
    "id", "status", "symbol", "side", "entry_time", "entry", "shares", "stop", "target", "exit_time", "exit",
    "fees", "point_value", "setup", "tags", "notes", "predicted_win", "predicted_r",
]


def default_path() -> Path:
    from .cli import home  # noqa: PLC0415

    return home() / "journal.csv"


def _read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    tmp.replace(path)


def _clean(v):
    if v is None:
        return ""
    if isinstance(v, float) and math.isnan(v):
        return ""
    if isinstance(v, datetime):
        return v.isoformat(timespec="minutes")
    return v


def _local_time(v, tz: str) -> str:
    """Any timestamp string to naive exchange-local 'YYYY-MM-DD HH:MM' (what the journal stores)."""
    if v in (None, ""):
        return ""
    ts = parse_times([str(v)], tz).iloc[0]
    if pd.isna(ts):
        raise ValueError(f"cannot read time {v!r}; use YYYY-MM-DD HH:MM")
    return ts.tz_localize(None).strftime("%Y-%m-%d %H:%M")


def add(path: Path, tz: str = DEFAULT_TZ, **trade) -> str:
    rows = _read_rows(path)
    trade = {k: _clean(v) for k, v in trade.items()}
    for k in ("entry_time", "exit_time"):
        if k in trade:
            trade[k] = _local_time(trade[k], tz)
    trade.setdefault("id", uuid.uuid4().hex[:8])
    trade.setdefault("status", "closed" if trade.get("exit") not in (None, "") else "open")
    trade.setdefault("point_value", 1)
    if trade.get("side") not in ("long", "short"):
        raise ValueError("side must be long or short")
    rows.append(trade)
    _write_rows(path, rows)
    return trade["id"]


def close(path: Path, trade_id: str, exit_price: float, exit_time: str, fees: float | None = None,
          notes: str | None = None, tz: str = DEFAULT_TZ) -> dict:
    exit_time = _local_time(exit_time, tz)
    rows = _read_rows(path)
    for r in rows:
        if r["id"] == trade_id:
            if r.get("status") == "closed":
                raise ValueError(f"trade {trade_id} is already closed")
            r.update(status="closed", exit=exit_price, exit_time=exit_time)
            if fees is not None:
                r["fees"] = float(r.get("fees") or 0) + fees
            if notes:
                r["notes"] = (r.get("notes", "") + " | " + notes).strip(" |")
            _write_rows(path, rows)
            return r
    raise ValueError(f"no trade with id {trade_id}")


def load(path: Path) -> pd.DataFrame:
    rows = _read_rows(path)
    df = pd.DataFrame(rows, columns=FIELDS)
    for c in ("entry", "shares", "stop", "target", "exit", "fees", "point_value", "predicted_win", "predicted_r"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ("entry_time", "exit_time"):
        # older rows may carry offsets; everything becomes naive exchange-local time
        df[c] = parse_times(df[c].replace("", None), DEFAULT_TZ).dt.tz_localize(None).to_numpy()
    df["fees"] = df["fees"].fillna(0.0)
    df["point_value"] = df["point_value"].fillna(1.0)
    sign = np.where(df["side"] == "short", -1.0, 1.0)
    df["pnl"] = sign * (df["exit"] - df["entry"]) * df["shares"] * df["point_value"] - df["fees"]
    risk = (df["entry"] - df["stop"]).abs() * df["shares"] * df["point_value"]
    df["risk"] = risk
    df["r"] = df["pnl"] / risk.replace(0, np.nan)
    df["open_risk"] = np.where(df["status"] == "open", risk, 0.0)
    df["hold_min"] = (df["exit_time"] - df["entry_time"]).dt.total_seconds() / 60
    df["date"] = df["entry_time"].dt.date
    return df


def _streak(wins: list[bool], value: bool) -> int:
    best = cur = 0
    for w in wins:
        cur = cur + 1 if w == value else 0
        best = max(best, cur)
    return best


def _block(df: pd.DataFrame) -> dict:
    n = len(df)
    if n == 0:
        return {"trades": 0}
    w = df[df["pnl"] > 0]
    lo = df[df["pnl"] <= 0]
    gross_loss = -lo["pnl"].sum()
    return {
        "trades": n,
        "win_rate": len(w) / n,
        "total_pnl": float(df["pnl"].sum()),
        "avg_pnl": float(df["pnl"].mean()),
        "avg_win": float(w["pnl"].mean()) if len(w) else 0.0,
        "avg_loss": float(lo["pnl"].mean()) if len(lo) else 0.0,
        "profit_factor": float(w["pnl"].sum() / gross_loss) if gross_loss > 0 else None,
        "expectancy_r": float(df["r"].mean()) if df["r"].notna().any() else None,
        "avg_win_r": float(w["r"].mean()) if len(w) and w["r"].notna().any() else None,
        "avg_loss_r": float(lo["r"].mean()) if len(lo) and lo["r"].notna().any() else None,
    }


def stats(df: pd.DataFrame, since=None, setup: str | None = None, symbol: str | None = None) -> dict:
    closed = df[(df["status"] == "closed") & df["pnl"].notna()].copy()
    if since is not None:
        closed = closed[closed["entry_time"] >= pd.Timestamp(since)]
    if setup:
        closed = closed[closed["setup"].str.lower() == setup.lower()]
    if symbol:
        closed = closed[closed["symbol"].str.upper() == symbol.upper()]
    closed = closed.sort_values("entry_time")
    out = {"overall": _block(closed)}
    if len(closed) == 0:
        return out
    equity = closed["pnl"].cumsum()
    out["overall"]["max_drawdown"] = float((equity - equity.cummax()).min())
    wins = list(closed["pnl"] > 0)
    out["overall"]["longest_win_streak"] = _streak(wins, True)
    out["overall"]["longest_loss_streak"] = _streak(wins, False)
    out["overall"]["avg_hold_min"] = float(closed["hold_min"].mean()) if closed["hold_min"].notna().any() else None
    out["overall"]["best"] = float(closed["pnl"].max())
    out["overall"]["worst"] = float(closed["pnl"].min())

    def by(col, key=None):
        g = closed.groupby(key if key is not None else closed[col].replace("", "(none)"))
        return {str(k): _block(v) for k, v in g}

    out["by_setup"] = by("setup")
    out["by_side"] = by("side")
    out["by_hour"] = by(None, closed["entry_time"].dt.hour.fillna(-1).astype(int))
    out["by_weekday"] = by(None, closed["entry_time"].dt.day_name().fillna("?"))
    out["by_symbol"] = by("symbol")
    tags = closed.assign(tag=closed["tags"].fillna("").str.split(",")).explode("tag")
    tags["tag"] = tags["tag"].str.strip()
    tags = tags[tags["tag"] != ""]
    out["by_tag"] = {str(k): _block(v) for k, v in tags.groupby("tag")}

    # did the time machine's odds match reality?
    cal = closed[closed["predicted_win"].notna()]
    if len(cal) >= 5:
        won = (cal["pnl"] > 0).astype(float)
        p = cal["predicted_win"].clip(0, 1)
        bins = pd.cut(p, [0, 0.4, 0.5, 0.6, 1.0], include_lowest=True,
                      labels=["under 40%", "40-50%", "50-60%", "over 60%"])
        out["calibration"] = {
            "trades": len(cal),
            "brier": float(((p - won) ** 2).mean()),
            "brier_coin_flip": 0.25,
            "bins": {str(b): {"trades": int(len(g)), "predicted": float(p[g.index].mean()),
                              "actual": float(won[g.index].mean())}
                     for b, g in cal.groupby(bins, observed=True)},
        }

    out["insights"] = insights(closed, out)
    return out


def insights(closed: pd.DataFrame, s: dict) -> list[str]:
    tips = []
    o = s["overall"]
    if o.get("avg_loss_r") is not None and o["avg_loss_r"] < -1.2:
        tips.append(f"average loser is {o['avg_loss_r']:.2f}R: losses run past the planned stop")
    if o.get("avg_win_r") is not None and o.get("avg_loss_r") and o["avg_win_r"] < abs(o["avg_loss_r"]) \
            and o["win_rate"] < 0.55:
        tips.append("winners are smaller than losers and the win rate is not high enough to carry that")
    hours = {h: b for h, b in s["by_hour"].items() if b["trades"] >= 3}
    if len(hours) >= 2:
        worst = min(hours, key=lambda h: hours[h]["total_pnl"])
        best = max(hours, key=lambda h: hours[h]["total_pnl"])
        if hours[worst]["total_pnl"] < 0:
            tips.append(f"the {worst}:00 hour is the costliest ({hours[worst]['total_pnl']:+,.0f} over "
                        f"{hours[worst]['trades']} trades); the {best}:00 hour is the best")
    setups = {k: b for k, b in s["by_setup"].items() if b["trades"] >= 3}
    for k, b in setups.items():
        if b.get("expectancy_r") is not None and b["expectancy_r"] < -0.2:
            tips.append(f"setup '{k}' is losing {b['expectancy_r']:.2f}R per trade over {b['trades']} trades")
    # tilt: trades taken right after two losses in a row on the same day
    after_two = []
    for _, day in closed.groupby("date"):
        res = list(day["pnl"] > 0)
        for i in range(2, len(res)):
            if not res[i - 1] and not res[i - 2]:
                after_two.append(day["pnl"].iloc[i])
    if len(after_two) >= 3 and np.mean(after_two) < 0 and o["avg_pnl"] > np.mean(after_two):
        tips.append(f"after two straight losses, the next trade averages {np.mean(after_two):+,.0f}: "
                    "a cooldown rule would have helped")
    per_day = closed.groupby("date")["pnl"].agg(["count", "sum"])
    if len(per_day) >= 5:
        busy = per_day[per_day["count"] > per_day["count"].median()]
        calm = per_day[per_day["count"] <= per_day["count"].median()]
        if len(busy) >= 2 and len(calm) >= 2 and busy["sum"].mean() < calm["sum"].mean() and busy["sum"].mean() < 0:
            tips.append("days with more trades than usual lose money on average: overtrading")
    return tips
