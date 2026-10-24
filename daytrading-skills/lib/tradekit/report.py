"""Plain-text and HTML rendering shared by the skills."""

from __future__ import annotations

import html
import json
import math
import sys
from typing import Iterable, Sequence


def bar(share: float, width: int = 30, char: str = "█") -> str:
    share = max(0.0, min(1.0, share))
    full = int(round(share * width))
    return char * full + "·" * (width - full)


def dots(label: str, width: int = 26) -> str:
    return (label + " ").ljust(width, ".") + " "


def table(rows: Sequence[Sequence], headers: Sequence[str], align: str | None = None) -> str:
    """Monospace table. ``align`` is a string of l/r per column."""
    cells = [[str(h) for h in headers]] + [["" if v is None else str(v) for v in r] for r in rows]
    widths = [max(len(r[i]) for r in cells) for i in range(len(headers))]
    align = align or "l" * len(headers)

    def fmt(r):
        return "  ".join(c.rjust(w) if a == "r" else c.ljust(w) for c, w, a in zip(r, widths, align)).rstrip()

    lines = [fmt(cells[0]), "  ".join("-" * w for w in widths)]
    lines += [fmt(r) for r in cells[1:]]
    return "\n".join(lines)


def money(x: float | None, places: int = 2) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    sign = "-" if x < 0 else ""
    return f"{sign}${abs(x):,.{places}f}"


def pct(x: float | None, places: int = 1, signed: bool = False) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    return f"{x:+.{places}%}" if signed else f"{x:.{places}%}"


def emit_json(obj, stream=None) -> None:
    json.dump(obj, stream or sys.stdout, indent=2, default=_json_default)
    (stream or sys.stdout).write("\n")


def _json_default(o):
    if hasattr(o, "isoformat"):
        return o.isoformat()
    if hasattr(o, "item"):
        return o.item()
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


def warn(msg: str) -> None:
    print(f"note: {msg}", file=sys.stderr)


# ---------------------------------------------------------------- HTML (time machine)

_CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a65;--grid:#e4e1d8;--band1:#c9d8f0;--band2:#9db7e3;
--line:#2f5fb3;--win:#2e8b57;--loss:#c4423a;--mid:#b08a2e;--card:#ffffff}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#151514;--fg:#ecebe6;--muted:#a3a29b;
--grid:#2d2c29;--band1:#1f3150;--band2:#2c4a7c;--line:#7ea6ec;--win:#5cc28a;--loss:#e97a70;--mid:#d9b45a;--card:#1d1d1b}}
:root[data-theme=dark]{--bg:#151514;--fg:#ecebe6;--muted:#a3a29b;--grid:#2d2c29;--band1:#1f3150;--band2:#2c4a7c;
--line:#7ea6ec;--win:#5cc28a;--loss:#e97a70;--mid:#d9b45a;--card:#1d1d1b}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:920px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:28px 0 8px}
.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.card{background:var(--card);border:1px solid var(--grid);border-radius:10px;padding:12px}
.big{font-size:26px;font-weight:650}.win{color:var(--win)}.loss{color:var(--loss)}.mid{color:var(--mid)}
svg{width:100%;height:auto;display:block}text{fill:var(--muted);font-size:11px}
.note{font-size:13px;color:var(--muted)}ul{padding-left:18px}
"""


def _poly(xs, ys) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))


def time_machine_html(title: str, subtitle: str, summary: dict, plan_lines: Iterable[str],
                      levels: dict, notes: Iterable[str]) -> str:
    """Self-contained page: outcome cards, price fan chart, odds-over-time chart."""
    esc = html.escape
    fan = summary.get("fan")
    W, H, PL, PR, PT, PB = 860, 320, 56, 16, 12, 28
    parts = [f"<!doctype html><html lang=en><head><meta charset=utf-8>"
             f"<meta name=viewport content='width=device-width,initial-scale=1'>"
             f"<title>{esc(title)}</title><style>{_CSS}</style></head><body><main>",
             f"<h1>{esc(title)}</h1><div class=muted>{esc(subtitle)}</div>"]

    between = summary["p_time_exit"] + summary["p_partial_then_stop"]
    cards = [
        ("Hit target", summary["p_target"], "win"),
        ("Hit stop", summary["p_stop"], "loss"),
        ("Ended in between", between, "mid"),
        ("Made money", summary["p_profit"], "win" if summary["p_profit"] >= 0.5 else "mid"),
    ]
    parts.append("<h2>Outcomes</h2><div class=grid>")
    for label, v, cls in cards:
        parts.append(f"<div class=card><div class=muted>{label}</div><div class='big {cls}'>{v:.1%}</div></div>")
    parts.append(f"<div class=card><div class=muted>Average result</div>"
                 f"<div class='big {'win' if summary['expected_r'] > 0 else 'loss'}'>{summary['expected_r']:+.2f}R</div></div>")
    parts.append("</div>")

    if fan:
        n = len(fan["p50"])
        lo = min(min(fan["p5"]), *levels.values()) if levels else min(fan["p5"])
        hi = max(max(fan["p95"]), *levels.values()) if levels else max(fan["p95"])
        pad = (hi - lo) * 0.06 or 1
        lo, hi = lo - pad, hi + pad
        X = lambda i: PL + (W - PL - PR) * i / max(1, n - 1)  # noqa: E731
        Y = lambda p: PT + (H - PT - PB) * (hi - p) / (hi - lo)  # noqa: E731
        xs = [X(i) for i in range(n)]
        svg = [f"<svg viewBox='0 0 {W} {H}' role=img aria-label='Simulated price paths'>"]
        for k in range(5):
            p = lo + (hi - lo) * k / 4
            svg.append(f"<line x1={PL} x2={W - PR} y1={Y(p):.1f} y2={Y(p):.1f} stroke='var(--grid)'/>"
                       f"<text x={PL - 6} y={Y(p) + 4:.1f} text-anchor=end>{p:.2f}</text>")
        band = lambda a, b, col: (f"<polygon fill='var({col})' points='"  # noqa: E731
                                  f"{_poly(xs, [Y(v) for v in fan[a]])} {_poly(xs[::-1], [Y(v) for v in fan[b][::-1]])}'/>")
        svg.append(band("p95", "p5", "--band1"))
        svg.append(band("p75", "p25", "--band2"))
        svg.append(f"<polyline fill=none stroke='var(--line)' stroke-width=2 points='{_poly(xs, [Y(v) for v in fan['p50']])}'/>")
        for name, price in levels.items():
            col = "--loss" if name.lower().startswith("stop") else "--win" if name.lower().startswith("t") else "--muted"
            svg.append(f"<line x1={PL} x2={W - PR} y1={Y(price):.1f} y2={Y(price):.1f} stroke='var({col})' "
                       f"stroke-dasharray='5 4'/><text x={W - PR - 4} y={Y(price) - 4:.1f} text-anchor=end>"
                       f"{esc(name)} {price:.2f}</text>")
        mins = summary["curve_minutes"]
        for i in range(0, n, max(1, n // 6)):
            label = f"+{mins[i - 1] if i else 0}m"
            anchor = "end" if i > n * 0.9 else "start" if i == 0 else "middle"
            svg.append(f"<text x={xs[i]:.1f} y={H - 8} text-anchor={anchor}>{label}</text>")
        svg.append("</svg>")
        parts.append("<h2>Where price went across the simulated paths</h2>"
                     "<div class=note>Median path, 25-75% band (dark) and 5-95% band (light). "
                     "This is the market path, whether or not the trade was still open.</div>")
        parts.append("".join(svg))

    ct, cs = summary["curve_target"], summary["curve_stop"]
    n = len(ct)
    X = lambda i: PL + (W - PL - PR) * i / max(1, n - 1)  # noqa: E731
    Y = lambda p: PT + (220 - PT - PB) * (1 - p)  # noqa: E731
    xs = [X(i) for i in range(n)]
    svg = ["<svg viewBox='0 0 860 220' role=img aria-label='Odds over time'>"]
    for k in range(5):
        p = k / 4
        svg.append(f"<line x1={PL} x2={W - PR} y1={Y(p):.1f} y2={Y(p):.1f} stroke='var(--grid)'/>"
                   f"<text x={PL - 6} y={Y(p) + 4:.1f} text-anchor=end>{p:.0%}</text>")
    svg.append(f"<polyline fill=none stroke='var(--win)' stroke-width=2 points='{_poly(xs, [Y(v) for v in ct])}'/>")
    svg.append(f"<polyline fill=none stroke='var(--loss)' stroke-width=2 points='{_poly(xs, [Y(v) for v in cs])}'/>")
    mins = summary["curve_minutes"]
    for i in range(0, n, max(1, n // 6)):
        anchor = "end" if i > n * 0.9 else "start" if i == 0 else "middle"
        svg.append(f"<text x={xs[i]:.1f} y={212} text-anchor={anchor}>+{mins[i]}m</text>")
    svg.append("</svg>")
    parts.append("<h2>Odds over time</h2><div class=note><span class=win>Green</span>: share of paths that "
                 "had reached the final target by then. <span class=loss>Red</span>: share stopped out for a full "
                 "loss before any target.</div>")
    parts.append("".join(svg))

    parts.append("<h2>Plan</h2><ul>" + "".join(f"<li>{esc(x)}</li>" for x in plan_lines) + "</ul>")
    parts.append("<h2>Read this before trusting the numbers</h2><ul>"
                 + "".join(f"<li class=note>{esc(x)}</li>" for x in notes) + "</ul>")
    parts.append("</main></body></html>")
    return "".join(parts)
