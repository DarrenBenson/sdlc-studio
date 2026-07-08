"""MUTANT (audit-quiz grading only, never enters a workspace): breaks SPEC R8 - the
throttle counts every recorded send as TWO, standing in for the counts-notifications-
not-sends bug class. A cited check pinning "a digest flush counts as one send" must
fail against this."""
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
        # R8 broken: each send is double-counted
        self._sends[key] = self._sends.get(key, 0) + 2
