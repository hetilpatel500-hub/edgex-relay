"""Trading-session helpers (regular hours, slots, day splitting)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time

import pandas as pd

from .data import DEFAULT_TZ


def parse_hhmm(text: str) -> time:
    text = text.strip()
    for fmt in ("%H:%M", "%H%M", "%I:%M%p", "%I:%M %p", "%H:%M:%S"):
        try:
            return datetime.strptime(text.upper(), fmt).time()
        except ValueError:
            continue
    raise ValueError(f"cannot read time {text!r}; use HH:MM in exchange time, e.g. 10:45")


@dataclass(frozen=True)
class Session:
    """A same-day trading session, e.g. US equities 09:30-16:00 New York time."""

    start: time = time(9, 30)
    end: time = time(16, 0)
    tz: str = DEFAULT_TZ

    @classmethod
    def parse(cls, spec: str | None, tz: str = DEFAULT_TZ) -> "Session":
        if not spec:
            return cls(tz=tz)
        a, b = spec.split("-")
        s, e = parse_hhmm(a), parse_hhmm(b)
        if e <= s:
            raise ValueError("sessions must start and end on the same day (e.g. 09:30-16:00)")
        return cls(s, e, tz)

    @property
    def start_min(self) -> int:
        return self.start.hour * 60 + self.start.minute

    @property
    def end_min(self) -> int:
        return self.end.hour * 60 + self.end.minute

    @property
    def minutes(self) -> int:
        return self.end_min - self.start_min

    def n_slots(self, interval: int) -> int:
        return self.minutes // interval

    def minute_of(self, ts) -> int:
        return ts.hour * 60 + ts.minute - self.start_min

    def slot_of(self, ts, interval: int) -> int:
        return self.minute_of(ts) // interval

    def slot_time(self, slot: int, interval: int) -> time:
        m = self.start_min + slot * interval
        return time(m // 60, m % 60)

    def label(self) -> str:
        return f"{self.start:%H:%M}-{self.end:%H:%M}"


def rth(df: pd.DataFrame, session: Session) -> pd.DataFrame:
    """Keep bars whose start time falls inside the session."""
    mins = df.index.hour * 60 + df.index.minute
    return df[(mins >= session.start_min) & (mins < session.end_min)]


def premarket(df: pd.DataFrame, session: Session) -> pd.DataFrame:
    mins = df.index.hour * 60 + df.index.minute
    return df[mins < session.start_min]


def split_days(df: pd.DataFrame) -> dict[date, pd.DataFrame]:
    return {d: g for d, g in df.groupby(df.index.date)}


def session_dates(df: pd.DataFrame) -> list[date]:
    return sorted(set(df.index.date))


def now_in(tz: str = DEFAULT_TZ) -> pd.Timestamp:
    return pd.Timestamp.now(tz=tz)


def at(d: date, t: time, tz: str = DEFAULT_TZ) -> pd.Timestamp:
    return pd.Timestamp(datetime.combine(d, t)).tz_localize(tz)
