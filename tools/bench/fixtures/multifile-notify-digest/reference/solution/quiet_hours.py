"""Quiet-hours calculation (SPEC R5).

Quiet hours run 22:00-07:00 in the user's local time, derived from an
integer UTC offset in whole hours.
"""
from __future__ import annotations

from datetime import datetime

QUIET_START_HOUR = 22
QUIET_END_HOUR = 7


def local_hour(now: datetime, utc_offset_hours: int) -> int:
    """The user's local hour of day for a naive UTC ``now``."""
    return (now.hour + utc_offset_hours) % 24


def in_quiet_hours(now: datetime, utc_offset_hours: int) -> bool:
    hour = local_hour(now, utc_offset_hours)
    return hour >= QUIET_START_HOUR or hour < QUIET_END_HOUR
