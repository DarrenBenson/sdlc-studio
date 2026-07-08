"""Per-user daily send throttle (SPEC R8).

The throttle counts sends - delivery events - per user per UTC day,
not the notifications contained in them.
"""
from __future__ import annotations

from datetime import date, datetime


class DailyThrottle:
    """Limits how many sends a user may receive per UTC day."""

    DEFAULT_LIMIT = 5

    def __init__(self, limit: int = DEFAULT_LIMIT) -> None:
        self.limit = limit
        self._sends: dict[tuple[str, date], int] = {}

    def sends_today(self, user_id: str, now: datetime) -> int:
        return self._sends.get((user_id, now.date()), 0)

    def allow(self, user_id: str, now: datetime) -> bool:
        return self.sends_today(user_id, now) < self.limit

    def record_send(self, user_id: str, now: datetime) -> None:
        key = (user_id, now.date())
        self._sends[key] = self._sends.get(key, 0) + 1
