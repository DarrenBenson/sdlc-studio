"""MUTANT (audit-quiz grading only, never enters a workspace): breaks SPEC R5 - quiet
hours never apply, so nothing is suppressed or deferred by them. A cited check for the
quiet-hours behaviour must fail against this."""
from __future__ import annotations

from datetime import datetime

QUIET_START_HOUR = 22
QUIET_END_HOUR = 7


def local_hour(now: datetime, utc_offset_hours: int) -> int:
    return (now.hour + utc_offset_hours) % 24


def in_quiet_hours(now: datetime, utc_offset_hours: int) -> bool:
    # R5 broken: quiet hours never trigger
    return False
