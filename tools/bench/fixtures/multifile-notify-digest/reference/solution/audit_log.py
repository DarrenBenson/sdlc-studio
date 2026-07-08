"""Append-only audit log of delivery attempts (SPEC R9)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

REASON_DELIVERED = "delivered"
REASON_SUPPRESSED_QUIET_HOURS = "suppressed_quiet_hours"
REASON_SUPPRESSED_UNSUBSCRIBED = "suppressed_unsubscribed"
REASON_THROTTLED = "throttled"


def delivered_reason(kind: str) -> str:
    """Reason code for a successful send of the given delivery kind.

    SPEC R9: kinds other than immediate use ``delivered_<kind>``.
    """
    return REASON_DELIVERED if kind == "immediate" else f"delivered_{kind}"


@dataclass(frozen=True)
class AuditEntry:
    user_id: str
    notification_ids: tuple[int, ...]
    reason: str
    at: datetime


class AuditLog:
    """Chronological record of every delivery attempt."""

    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []

    def append(
        self,
        user_id: str,
        notification_ids: tuple[int, ...],
        reason: str,
        at: datetime,
    ) -> None:
        self.entries.append(AuditEntry(user_id, tuple(notification_ids), reason, at))

    def for_user(self, user_id: str) -> list[AuditEntry]:
        return [e for e in self.entries if e.user_id == user_id]
