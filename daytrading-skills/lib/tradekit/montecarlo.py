"""The Time Machine: replay the rest of a trading day thousands of times.

How a simulation works
----------------------
1. Every historical session is cut into fixed clock-time slots (e.g. 78 five-
   minute bars from 09:30 to 16:00). Each bar is stored as four log returns
   relative to the previous bar's close: open, high, low, close.
2. A simulated path starts at your entry price and walks forward one slot at a
   time. For each slot it borrows that same clock-time bar from a randomly
   chosen historical day, sticking with that day for a random stretch (a
   stationary block bootstrap, average block ``block_bars``) before jumping to
   another day. Same-clock sampling keeps the open/lunch/close volatility
   rhythm; blocks keep momentum and mean-reversion streaks intact.
3. Returns can be rescaled to today's volatility (how violent the morning has
   been versus the same stretch on historical days) and optionally de-meaned so
   a stock's recent uptrend does not leak into the odds.
4. Each path is managed exactly like the plan says: stop, scale-out targets,
   breakeven moves, trailing stop and a flat-by time, with gap-through fills
   and slippage. Bars that touch both the stop and a target are resolved with
   the usual OHLC path heuristic, or worst-case if asked.

Nothing here is a forecast. It answers one question: "if the rest of today
behaves like a random remix of the recent past, how does this trade play out?"
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

from .session import Session, rth, split_days

TARGET, STOP, PARTIAL_STOP, TIME = 0, 1, 2, 3
OUTCOME_NAMES = {TARGET: "target", STOP: "stop", PARTIAL_STOP: "partial_then_stop", TIME: "time_exit"}


@dataclass
class Target:
    price: float
    fraction: float


@dataclass
class TradePlan:
    side: str
    entry: float
    stop: float
    targets: list[Target] = field(default_factory=list)
    breakeven_after: int | None = None  # 0-based target index; stop -> entry once it fills
    trail_r: float | None = None  # trailing stop distance in R (after first target, or from entry)
    slippage: float = 0.0  # price units lost on stop and market exits

    def __post_init__(self) -> None:
        self.side = self.side.lower()
        if self.side not in ("long", "short"):
            raise ValueError("side must be long or short")
        if self.risk <= 0:
            raise ValueError("stop must differ from entry")
        s = self.sign
        if s * (self.entry - self.stop) <= 0:
            raise ValueError(f"for a {self.side} the stop must be {'below' if s > 0 else 'above'} the entry")
        last = self.entry
        for t in self.targets:
            if s * (t.price - last) <= 0:
                raise ValueError(
                    f"targets must be {'above' if s > 0 else 'below'} the entry and in order; got {t.price}"
                )
            if not 0 < t.fraction <= 1:
                raise ValueError("target fractions must be in (0, 1]")
            last = t.price
        if sum(t.fraction for t in self.targets) > 1 + 1e-9:
            raise ValueError("target fractions add up to more than 100%")
        if self.breakeven_after is not None and not 0 <= self.breakeven_after < max(1, len(self.targets)):
            self.breakeven_after = None
        if self.trail_r is not None and self.trail_r <= 0:
            raise ValueError("trail_r must be positive")

    @property
    def sign(self) -> int:
        return 1 if self.side == "long" else -1

    @property
    def risk(self) -> float:
        return abs(self.entry - self.stop)

    @property
    def runner_fraction(self) -> float:
        return max(0.0, 1.0 - sum(t.fraction for t in self.targets))

    def r_of(self, price: float) -> float:
        return self.sign * (price - self.entry) / self.risk

    def describe(self) -> str:
        parts = [f"{self.side} @ {self.entry:.2f}", f"stop {self.stop:.2f} (-1R = {self.risk:.2f})"]
        for i, t in enumerate(self.targets, 1):
            parts.append(f"T{i} {t.price:.2f} (+{self.r_of(t.price):.2f}R, {t.fraction:.0%})")
        if self.runner_fraction > 1e-9 and self.targets:
            parts.append(f"runner {self.runner_fraction:.0%}")
        if self.breakeven_after is not None and self.targets:
            parts.append(f"stop to breakeven after T{self.breakeven_after + 1}")
        if self.trail_r:
            parts.append(f"trail {self.trail_r:g}R")
        return " · ".join(parts)


# ---------------------------------------------------------------- return bank

@dataclass
class ReturnBank:
    ro: np.ndarray  # (D, S) log(open / prev close)
    rh: np.ndarray
    rl: np.ndarray
    rc: np.ndarray
    valid: np.ndarray  # (D, S) bool: a real bar existed in this slot
    days: list[date]
    interval: int
    session: Session

    @property
    def n_days(self) -> int:
        return len(self.days)

    def select(self, mask: np.ndarray) -> "ReturnBank":
        idx = np.flatnonzero(mask)
        return ReturnBank(self.ro[idx], self.rh[idx], self.rl[idx], self.rc[idx], self.valid[idx],
                          [self.days[i] for i in idx], self.interval, self.session)

    def day_index(self, d: date) -> int | None:
        try:
            return self.days.index(d)
        except ValueError:
            return None


def build_bank(bars: pd.DataFrame, session: Session, interval: int, min_coverage: float = 0.5) -> ReturnBank:
    """Turn intraday bars into per-day, per-slot log returns."""
    S = session.n_slots(interval)
    if S < 2:
        raise ValueError("session too short for this bar size")
    days, rows = [], []
    for d, g in split_days(rth(bars, session)).items():
        slots = ((g.index.hour * 60 + g.index.minute - session.start_min) // interval).to_numpy()
        keep = (slots >= 0) & (slots < S)
        g, slots = g[keep], slots[keep]
        if len(g) == 0:
            continue
        o = np.full(S, np.nan); h = np.full(S, np.nan); lo = np.full(S, np.nan); c = np.full(S, np.nan)
        o[slots] = g["open"].to_numpy(); h[slots] = g["high"].to_numpy()
        lo[slots] = g["low"].to_numpy(); c[slots] = g["close"].to_numpy()
        valid = ~np.isnan(c)
        if valid.mean() < min_coverage:
            continue
        prev = pd.Series(c).ffill().shift(1).to_numpy()
        prev = np.where(np.isnan(prev), o, prev)
        with np.errstate(invalid="ignore", divide="ignore"):
            r = [np.log(x / prev) for x in (o, h, lo, c)]
        r = [np.where(valid & np.isfinite(x), x, 0.0) for x in r]
        days.append(d)
        rows.append((*r, valid))
    if not rows:
        raise ValueError("no usable sessions in the data (check --session and the bar timestamps)")
    ro, rh, rl, rc, valid = (np.vstack([row[i] for row in rows]) for i in range(5))
    return ReturnBank(ro, rh, rl, rc, valid, days, interval, session)


def parkinson_var(bank: ReturnBank, day: int, start: int, stop: int) -> float:
    """Sum of per-bar Parkinson variances (high/low range) over slots [start, stop)."""
    hl = bank.rh[day, start:stop] - bank.rl[day, start:stop]
    v = bank.valid[day, start:stop]
    return float(np.sum((hl[v] ** 2)) / (4 * math.log(2)))


def auto_vol_scale(bank: ReturnBank, today: ReturnBank | None, upto_slot: int, clip=(0.5, 3.0)) -> tuple[float, str]:
    """How violent today has been so far versus the same clock window historically."""
    if today is None or upto_slot < 3:
        return 1.0, "no session data before entry yet, so volatility is left at its historical level"
    n_today = int(today.valid[0, :upto_slot].sum())
    if n_today < 3:
        return 1.0, "too few bars before entry to measure today's volatility"
    t_var = parkinson_var(today, 0, 0, upto_slot) * upto_slot / n_today
    hist = np.array([parkinson_var(bank, d, 0, upto_slot) for d in range(bank.n_days)])
    hist = hist[hist > 0]
    if len(hist) == 0 or t_var <= 0:
        return 1.0, "could not measure volatility"
    raw = math.sqrt(t_var / float(np.median(hist)))
    scale = float(np.clip(raw, *clip))
    note = f"today's session so far is running at {raw:.2f}x typical volatility for this time of day"
    if scale != raw:
        note += f" (clipped to {scale:.2f}x)"
    return scale, note


# ---------------------------------------------------------------- simulation

@dataclass
class SimResult:
    plan: TradePlan
    n: int
    steps: int
    interval: int
    pnl: np.ndarray  # per share, all fractions combined, after slippage
    outcome: np.ndarray  # TARGET / STOP / PARTIAL_STOP / TIME
    target_hit: np.ndarray  # (n, K)
    t_exit: np.ndarray  # step index of the final exit
    t_first_target: np.ndarray  # -1 when never
    t_all_targets: np.ndarray  # step the last target leg filled, -1 when never
    mfe: np.ndarray  # max favourable excursion, price units
    mae: np.ndarray  # max adverse excursion, price units (<= 0)
    ambiguous_bars: int
    days_used: int
    fan: np.ndarray | None = None  # (5, steps + 1) price percentiles 5/25/50/75/95
    mode: str = "bootstrap"

    @property
    def r(self) -> np.ndarray:
        return self.pnl / self.plan.risk


def simulate(bank: ReturnBank, plan: TradePlan, start_slot: int, end_slot: int, n_sims: int = 10_000,
             block_bars: float = 6, vol_scale: float = 1.0, demean: bool = False, ambiguous: str = "ohlc",
             seed: int | None = None, mode: str = "bootstrap", min_coverage: float = 0.8,
             record_fan: bool = True) -> SimResult:
    """Run the trade through ``n_sims`` remixed rest-of-day paths.

    ``start_slot`` is the first bar simulated (the one after entry) and
    ``end_slot`` the last bar, whose close is the time exit. ``mode='replay'``
    instead walks each eligible historical day once, unshuffled.
    """
    if ambiguous not in ("ohlc", "worst"):
        raise ValueError("ambiguous must be 'ohlc' or 'worst'")
    T = end_slot - start_slot + 1
    if start_slot < 0 or T <= 0 or end_slot >= bank.ro.shape[1]:
        raise ValueError("no session time left between entry and the exit time")
    window = slice(start_slot, end_slot + 1)
    eligible = bank.valid[:, window].mean(axis=1) >= min_coverage
    if eligible.sum() == 0:
        raise ValueError("no historical day has data covering the simulated window")
    RO, RH, RL, RC = (x[eligible][:, window] * vol_scale for x in (bank.ro, bank.rh, bank.rl, bank.rc))
    if demean:
        mu = RC.mean(axis=0, keepdims=True)
        RO, RH, RL, RC = RO - mu, RH - mu, RL - mu, RC - mu
    De = RO.shape[0]

    rng = np.random.default_rng(seed)
    if mode == "replay":
        n, day, p_switch = De, np.arange(De), 0.0
    else:
        n, day, p_switch = n_sims, rng.integers(0, De, n_sims), 1.0 / max(1.0, block_bars)

    s, entry, slip = plan.sign, plan.entry, plan.slippage
    tp = np.array([t.price for t in plan.targets], dtype=float)
    fr = np.array([t.fraction for t in plan.targets], dtype=float)
    K = len(tp)
    trail_dist = plan.trail_r * plan.risk if plan.trail_r else None

    price = np.full(n, entry)
    remaining = np.ones(n)
    realized = np.zeros(n)
    stop = np.full(n, plan.stop)
    k_next = np.zeros(n, dtype=int)
    active = np.ones(n, dtype=bool)
    outcome = np.full(n, TIME)
    t_exit = np.full(n, T - 1)
    t_first = np.full(n, -1)
    t_all = np.full(n, -1)
    hit = np.zeros((n, K), dtype=bool)
    mfe = np.zeros(n)
    mae = np.zeros(n)
    ambiguous_bars = 0
    fan = np.empty((5, T + 1)) if record_fan else None
    if record_fan:
        fan[:, 0] = entry

    tighter = np.maximum if s > 0 else np.minimum

    def close_out(mask, fill, code, t):
        realized[mask] += remaining[mask] * s * (fill[mask] - entry)
        remaining[mask] = 0.0
        active[mask] = False
        outcome[mask] = code
        t_exit[mask] = t

    def stop_check(mask, level, fill, t):
        m = mask & active & (s * (level - stop) <= 0)
        if m.any():
            code = np.where(k_next > 0, PARTIAL_STOP, STOP)
            realized[m] += remaining[m] * s * (fill[m] - s * slip - entry)
            remaining[m] = 0.0
            active[m] = False
            outcome[m] = code[m]
            t_exit[m] = t

    def fill_targets(mask, level, o, t):
        for k in range(K):
            m = mask & active & (k_next == k) & (s * (level - tp[k]) >= 0)
            if not m.any():
                continue
            fill = np.where(s * (o - tp[k]) >= 0, o, tp[k])  # a gap through the limit fills at the open
            q = np.minimum(fr[k], remaining)
            realized[m] += q[m] * s * (fill[m] - entry)
            remaining[m] -= q[m]
            hit[m, k] = True
            k_next[m] = k + 1
            if k == 0:
                t_first[m] = t
            if k == K - 1:
                t_all[m] = t
            if plan.breakeven_after == k:
                stop[m] = tighter(stop[m], entry)
            done = m & (remaining <= 1e-9)
            active[done] = False
            outcome[done] = TARGET
            t_exit[done] = t

    for t in range(T):
        if t > 0 and p_switch > 0:
            sw = rng.random(n) < p_switch
            day[sw] = rng.integers(0, De, int(sw.sum()))
        o = price * np.exp(RO[day, t])
        h = price * np.exp(RH[day, t])
        lo = price * np.exp(RL[day, t])
        c = price * np.exp(RC[day, t])
        fav, adv = (h, lo) if s > 0 else (lo, h)
        was_active = active.copy()

        if K:
            ambiguous_bars += int(np.sum(active & (s * (adv - stop) <= 0)
                                         & (s * (fav - tp[np.minimum(k_next, K - 1)]) >= 0) & (k_next < K)))

        # 1. the open: gaps through the stop fill at the open, gaps through targets fill at the open
        stop_check(active, o, o, t)
        fill_targets(active, o, o, t)

        # 2. inside the bar
        if ambiguous == "worst":
            pre, post = active.copy(), active.copy()
        else:
            adverse_first = s * (c - o) >= 0  # O->L->H->C for an up bar, O->H->L->C for a down bar
            pre, post = active & adverse_first, active & ~adverse_first
        stop_check(pre, adv, stop.copy(), t)
        fill_targets(active, fav, o, t)
        stop_check(post, adv, stop.copy(), t)
        stop_check(active, c, stop.copy(), t)  # a close beyond the stop crossed it whatever the order

        # 3. excursions, trailing stop, time exit
        mfe[was_active] = np.maximum(mfe[was_active], s * (fav[was_active] - entry))
        mae[was_active] = np.minimum(mae[was_active], s * (adv[was_active] - entry))
        if trail_dist is not None:
            on = active & ((k_next > 0) if K else True)
            stop[on] = tighter(stop[on], entry + s * (mfe[on] - trail_dist))
        if t == T - 1 and active.any():
            close_out(active.copy(), c - s * slip, TIME, t)

        price = c
        if record_fan:
            fan[:, t + 1] = np.percentile(c, [5, 25, 50, 75, 95])

    if K:
        # every target leg filled: a win for the plan even if a runner later exits on its trail
        outcome[k_next == K] = TARGET
    return SimResult(plan, n, T, bank.interval, realized, outcome, hit, t_exit, t_first, t_all, mfe, mae,
                     ambiguous_bars, De, fan, mode)


# ---------------------------------------------------------------- summary

def _pct(x: np.ndarray) -> float:
    return float(np.mean(x)) if len(x) else 0.0


def summarize(res: SimResult) -> dict:
    plan, r, n = res.plan, res.r, res.n
    oc = res.outcome
    green = res.pnl > 0
    minutes = (res.t_exit + 1) * res.interval
    t_win = np.where(res.t_all_targets >= 0, res.t_all_targets, res.t_exit)
    se = lambda p: 1.96 * math.sqrt(max(p * (1 - p), 1e-12) / n)  # noqa: E731
    p_target = _pct(oc == TARGET)
    p_stop = _pct(oc == STOP)
    p_partial = _pct(oc == PARTIAL_STOP)
    p_time = _pct(oc == TIME)
    out = {
        "mode": res.mode,
        "paths": n,
        "days_used": res.days_used,
        "steps": res.steps,
        "interval_min": res.interval,
        "p_target": p_target,
        "p_stop": p_stop,
        "p_partial_then_stop": p_partial,
        "p_time_exit": p_time,
        "p_time_exit_green": _pct((oc == TIME) & green),
        "p_time_exit_red": _pct((oc == TIME) & ~green),
        "p_profit": _pct(green),
        "p_profit_ci95": se(_pct(green)),
        "p_target_ci95": se(p_target),
        "p_stop_ci95": se(p_stop),
        "p_each_target": [float(x) for x in res.target_hit.mean(axis=0)] if res.target_hit.size else [],
        "expected_r": float(np.mean(r)),
        "expected_r_se": float(np.std(r) / math.sqrt(n)),
        "expected_pnl_per_share": float(np.mean(res.pnl)),
        "median_r": float(np.median(r)),
        "r_percentiles": dict(zip(["p5", "p25", "p50", "p75", "p95"],
                                  map(float, np.percentile(r, [5, 25, 50, 75, 95])))),
        "avg_win_r": float(np.mean(r[green])) if green.any() else 0.0,
        "avg_loss_r": float(np.mean(r[~green])) if (~green).any() else 0.0,
        "profit_factor": float(r[green].sum() / -r[~green].sum()) if (~green).any() and r[~green].sum() < 0 else None,
        "median_minutes_to_target": float(np.median((t_win[oc == TARGET] + 1) * res.interval))
        if (oc == TARGET).any() else None,
        "median_minutes_to_stop": float(np.median(minutes[oc == STOP])) if (oc == STOP).any() else None,
        "median_mae_of_winners_r": float(np.median(res.mae[green] / plan.risk)) if green.any() else None,
        "p_full_loss_after_1r_open_profit": _pct((oc == STOP) & (res.mfe >= plan.risk)),
        "ambiguous_bar_share": res.ambiguous_bars / max(1, n),
    }
    if plan.targets:
        reward = sum(t.fraction * plan.r_of(t.price) for t in plan.targets) + plan.runner_fraction * plan.r_of(
            plan.targets[-1].price)
        out["breakeven_win_rate_if_all_or_nothing"] = 1 / (1 + reward) if reward > 0 else None
    # cumulative odds over time (for charts)
    steps = np.arange(res.steps)
    out["curve_minutes"] = [int((i + 1) * res.interval) for i in steps]
    out["curve_target"] = [float(np.mean((oc == TARGET) & (t_win <= i))) for i in steps]
    out["curve_stop"] = [float(np.mean((oc == STOP) & (res.t_exit <= i))) for i in steps]
    # half-R buckets centred on round numbers, so a -1.02R stop lands in the "-1.0R" bucket
    lo_c = math.floor(np.percentile(r, 0.5) * 2) / 2
    hi_c = math.ceil(np.percentile(r, 99.5) * 2) / 2
    centers = np.arange(lo_c, hi_c + 0.25, 0.5)
    edges = np.append(centers - 0.25, centers[-1] + 0.25)
    counts, _ = np.histogram(np.clip(r, edges[0], edges[-1] - 1e-9), bins=edges)
    out["histogram"] = {"centers": [float(c) for c in centers], "edges": [float(e) for e in edges],
                        "share": [float(c) / n for c in counts]}
    if res.fan is not None:
        out["fan"] = {k: [float(v) for v in res.fan[i]] for i, k in enumerate(["p5", "p25", "p50", "p75", "p95"])}
    return out


def headline(summary: dict) -> str:
    between = summary["p_time_exit"] + summary["p_partial_then_stop"]
    return (f"target {summary['p_target']:.1%} · stop {summary['p_stop']:.1%} · in between {between:.1%} · "
            f"made money {summary['p_profit']:.1%} · avg {summary['expected_r']:+.2f}R")
