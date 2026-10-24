"""Position sizing from a fixed risk budget."""

from __future__ import annotations

import math
import re

# dollars per one-point move, per contract
FUTURES = {
    "ES": 50.0, "MES": 5.0, "NQ": 20.0, "MNQ": 2.0, "YM": 5.0, "MYM": 0.5, "RTY": 50.0, "M2K": 5.0,
    "CL": 1000.0, "MCL": 100.0, "GC": 100.0, "MGC": 10.0,
}


def contract_point_value(symbol: str | None) -> float | None:
    """MESZ6 -> 5.0; returns None for anything that is not a known future."""
    if not symbol:
        return None
    raw = symbol.upper()
    marked = raw.endswith("=F") or raw.startswith("/")  # Yahoo MES=F, broker /MES
    s = raw.removesuffix("=F").lstrip("/")
    for root in sorted(FUTURES, key=len, reverse=True):
        # a bare "CL" or "ES" is a stock (Colgate, Eversource), so roots need a marker or a contract month
        if (marked and s == root) or re.fullmatch(rf"{root}[FGHJKMNQUVXZ]\d{{1,2}}", s):
            return FUTURES[root]
    return None


def size_position(account: float, entry: float, stop: float, risk_pct: float | None = 1.0,
                  risk_dollars: float | None = None, point_value: float = 1.0, lot: int = 1,
                  max_position_pct: float | None = 100.0, buying_power: float | None = None,
                  margin_per_unit: float | None = None, commission_per_unit: float = 0.0,
                  commission_per_order: float = 0.0, slippage: float = 0.0,
                  max_units: int | None = None) -> dict:
    if account <= 0:
        raise ValueError("account size must be positive")
    if entry <= 0 or stop <= 0:
        raise ValueError("prices must be positive")
    per_unit_move = abs(entry - stop)
    if per_unit_move == 0:
        raise ValueError("entry and stop are the same price")
    budget = risk_dollars if risk_dollars is not None else account * (risk_pct or 0) / 100
    budget_after_fees = budget - 2 * commission_per_order
    risk_per_unit = (per_unit_move + slippage) * point_value + 2 * commission_per_unit
    by_risk = math.floor(max(0.0, budget_after_fees) / risk_per_unit)

    caps = {"risk budget": by_risk}
    is_future = point_value != 1.0 or margin_per_unit is not None
    if not is_future:
        if max_position_pct:
            caps["max position size"] = math.floor(account * max_position_pct / 100 / entry)
        if buying_power:
            caps["buying power"] = math.floor(buying_power / entry)
    elif margin_per_unit:
        caps["margin"] = math.floor((buying_power or account) / margin_per_unit)
    if max_units is not None:
        caps["max units"] = max_units
    binding = min(caps, key=caps.get)
    units = max(0, (caps[binding] // lot) * lot)

    risk_total = units * risk_per_unit + (2 * commission_per_order if units else 0)
    notional = units * entry * point_value
    out = {
        "units": int(units),
        "binding_constraint": binding,
        "caps": {k: int(v) for k, v in caps.items()},
        "risk_budget": budget,
        "risk_per_unit": risk_per_unit,
        "risk_total": risk_total,
        "risk_pct_of_account": risk_total / account * 100,
        "notional": notional,
        "notional_pct_of_account": notional / account * 100,
        "r_ladder": [{"r": r, "price": entry + (1 if entry > stop else -1) * r * per_unit_move,
                      "pnl": units * r * per_unit_move * point_value - 2 * units * commission_per_unit
                      - 2 * commission_per_order if units else 0.0} for r in (1, 2, 3)],
        "warnings": [],
    }
    if units == 0:
        out["warnings"].append("the risk budget does not cover even one unit at this stop distance")
    if not is_future and notional > account and not buying_power:
        out["warnings"].append("position is larger than the account: this needs margin")
    if budget > account * 0.02:
        out["warnings"].append(f"risking {budget / account:.1%} of the account on one trade is aggressive "
                               "(many day traders cap it at 0.5-1%)")
    if slippage == 0 and per_unit_move / entry < 0.003:
        out["warnings"].append("tight stop and no slippage assumed: real fills will cost more than shown")
    return out
