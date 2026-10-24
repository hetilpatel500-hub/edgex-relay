"""Exit planning: where the stop goes, where profits get taken, when to give up."""

from __future__ import annotations

from dataclasses import dataclass, field

from .levels import Level, merge, nearest

STYLES = {
    # (reward in R, fraction sold) per target; whatever is left is a runner on a trailing stop
    "scale": [(1.0, 0.5), (2.0, 0.25)],
    "thirds": [(1.0, 1 / 3), (2.0, 1 / 3)],
    "single": [(2.0, 1.0)],
    "runner": [(1.0, 0.5)],
}


@dataclass
class ExitPlan:
    side: str
    entry: float
    stop: float
    stop_reason: str
    targets: list[dict]  # {price, fraction, r, reason}
    breakeven_after: int | None  # 1-based
    trail_r: float | None
    time_stop_minutes: int | None
    flat_by: str
    notes: list[str] = field(default_factory=list)
    stop_options: list[dict] = field(default_factory=list)

    @property
    def risk(self) -> float:
        return abs(self.entry - self.stop)

    def to_dict(self) -> dict:
        return {
            "side": self.side, "entry": round(self.entry, 4), "stop": round(self.stop, 4),
            "risk": round(self.risk, 4), "stop_reason": self.stop_reason,
            "targets": [{**t, "price": round(t["price"], 4), "r": round(t["r"], 2)} for t in self.targets],
            "breakeven_after": self.breakeven_after, "trail_r": self.trail_r,
            "time_stop_minutes": self.time_stop_minutes, "flat_by": self.flat_by,
            "stop_options": self.stop_options, "notes": self.notes,
        }


def stop_candidates(side: str, entry: float, levels: list[Level], daily_atr: float | None,
                    bar_atr: float | None) -> list[dict]:
    d = 1 if side == "long" else -1
    buf = 0.05 * daily_atr if daily_atr else entry * 0.001
    out = []
    lv = nearest(levels, entry, -d, min_dist=buf, min_strength=2)
    if lv:
        out.append({"kind": "structure", "price": lv.price - d * buf,
                    "reason": f"just {'under' if d > 0 else 'over'} {lv.label} {lv.price:.2f}"})
    if bar_atr:
        out.append({"kind": "atr", "price": entry - d * 2.0 * bar_atr, "reason": "2x the intraday bar ATR"})
    if daily_atr:
        out.append({"kind": "daily-atr", "price": entry - d * 0.25 * daily_atr, "reason": "a quarter of daily ATR"})
    out.append({"kind": "percent", "price": entry * (1 - d * 0.01), "reason": "1% fallback"})
    for c in out:
        c["risk"] = abs(entry - c["price"])
        c["atr_fraction"] = c["risk"] / daily_atr if daily_atr else None
    return out


def choose_stop(cands: list[dict], daily_atr: float | None) -> dict:
    """Prefer structure when it is a sane distance; otherwise the volatility stop."""
    for c in cands:
        if c["kind"] == "structure" and (not daily_atr or 0.08 <= c["atr_fraction"] <= 0.5):
            return c
    for kind in ("atr", "daily-atr", "percent"):
        for c in cands:
            if c["kind"] == kind and (not daily_atr or c["atr_fraction"] <= 0.6):
                return c
    return cands[-1]


def plan_exits(side: str, entry: float, stop: float | None = None, levels: list[Level] | None = None,
               daily_atr: float | None = None, bar_atr: float | None = None, day_high: float | None = None,
               day_low: float | None = None, style: str = "scale", first_r: float | None = None,
               trail_r: float | None = 1.0, time_stop_minutes: int | None = 45,
               flat_by: str = "15:55") -> ExitPlan:
    if style not in STYLES:
        raise ValueError(f"style must be one of {list(STYLES)}")
    d = 1 if side == "long" else -1
    levels = merge(levels or [], (daily_atr or entry * 0.02) * 0.05)
    cands = stop_candidates(side, entry, levels, daily_atr, bar_atr)
    if stop is not None:
        if d * (entry - stop) <= 0:
            raise ValueError(f"a {side} stop must be {'below' if d > 0 else 'above'} the entry")
        chosen = {"kind": "given", "price": stop, "reason": "your stop", "risk": abs(entry - stop)}
    else:
        chosen = choose_stop(cands, daily_atr)
    risk = chosen["risk"]
    notes = []

    legs = list(STYLES[style])
    if first_r is not None:
        legs[0] = (first_r, legs[0][1])
    targets = []
    prev_r = 0.0
    for i, (want_r, frac) in enumerate(legs):
        want_r = max(want_r, prev_r + 0.5)
        # a real level near the R target beats a round R number: [want-0.5R, want+1R], never under 1R for T1
        lo_r = max(want_r - (0.0 if i == 0 else 0.5), prev_r + 0.25)
        hi_r = want_r + 1.0
        near = [lv for lv in levels if lv.strength >= 2 and lo_r <= d * (lv.price - entry) / risk <= hi_r]
        if near:
            lv = min(near, key=lambda x: d * (x.price - entry))
            price = lv.price - d * 0.02 * risk  # sit just in front of the level
            reason = f"in front of {lv.label} {lv.price:.2f}"
        else:
            price = entry + d * want_r * risk
            reason = f"{want_r:g}R"
        r = d * (price - entry) / risk
        targets.append({"price": price, "fraction": round(frac, 4), "r": r, "reason": reason})
        prev_r = r

    runner = 1 - sum(f for _, f in legs)
    if runner > 1e-6:
        notes.append(f"{runner:.0%} runner rides a {trail_r:g}R trailing stop after T1 until the flat-by time")
    else:
        trail_r = None

    if daily_atr and day_high is not None and day_low is not None:
        used = day_high - day_low
        left = max(0.0, daily_atr - used)
        reach = (day_low + daily_atr) if d > 0 else (day_high - daily_atr)
        notes.append(f"today has used {used / daily_atr:.0%} of a normal day's range ({daily_atr:.2f}); "
                     f"a typical day would top out near {reach:.2f}" if d > 0 else
                     f"today has used {used / daily_atr:.0%} of a normal day's range ({daily_atr:.2f}); "
                     f"a typical day would bottom near {reach:.2f}")
        for i, t in enumerate(targets, 1):
            if d * (t["price"] - reach) > 0:
                t["stretch"] = True
                notes.append(f"T{i} {t['price']:.2f} is beyond a normal day's range: treat it as a stretch")
        if left < risk:
            notes.append("less than 1R of normal range is left today; consider a smaller target or skipping")

    if daily_atr and risk > 0.5 * daily_atr:
        notes.append(f"the stop is {risk / daily_atr:.2f} daily ATRs away: wide for a day trade, so size down")
    be = 1 if len(targets) > 1 else None
    plan = ExitPlan(side, entry, chosen["price"], chosen["reason"], targets, be, trail_r, time_stop_minutes,
                    flat_by, notes, [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()}
                                     for c in cands])
    return plan
