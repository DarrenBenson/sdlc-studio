"""Delivery routing.

Decides, for each notification, whether it is delivered immediately,
deferred by quiet hours, throttled, or suppressed. See docs/SPEC.md
for the numbered requirements cited below.
"""
from __future__ import annotations

from datetime import datetime

import audit_log
from audit_log import AuditLog
from models import Delivery, Notification, User
from quiet_hours import in_quiet_hours
from store import InMemoryStore
from throttle import DailyThrottle


class NotificationService:
    """Facade combining the store, throttle, quiet hours and audit log."""

    def __init__(self, throttle_limit: int = DailyThrottle.DEFAULT_LIMIT) -> None:
        self.store = InMemoryStore()
        self.throttle = DailyThrottle(throttle_limit)
        self.audit = AuditLog()

    def add_user(
        self, user_id: str, *, subscribed: bool = True, utc_offset_hours: int = 0
    ) -> User:
        user = User(user_id, subscribed, utc_offset_hours)
        self.store.add_user(user)
        return user

    def notify(
        self,
        user_id: str,
        body: str,
        *,
        urgent: bool = False,
        mandatory: bool = False,
        now: datetime,
    ) -> Delivery | None:
        """Create a notification and route it.

        Returns the resulting delivery, or None if the notification was
        suppressed or deferred.
        """
        user = self.store.get_user(user_id)
        note = self.store.create_notification(user_id, body, urgent, mandatory)
        return self._route(user, note, now)

    def release_deferred(self, *, now: datetime) -> list[Delivery]:
        """Re-attempt notifications deferred by quiet hours (SPEC R5)."""
        made: list[Delivery] = []
        still_quiet: list[Notification] = []
        for note in self.store.drain_deferred():
            user = self.store.get_user(note.user_id)
            if in_quiet_hours(now, user.utc_offset_hours):
                still_quiet.append(note)
                continue
            if not self.throttle.allow(user.user_id, now):
                self.audit.append(
                    user.user_id,
                    (note.notification_id,),
                    audit_log.REASON_THROTTLED,
                    now,
                )
                continue
            made.append(self._deliver(user, (note,), "immediate", now))
        for note in still_quiet:
            self.store.defer(note)
        return made

    # -- internals ----------------------------------------------------------

    def _route(
        self, user: User, note: Notification, now: datetime
    ) -> Delivery | None:
        if not user.subscribed and not note.mandatory:
            # SPEC R7: unsubscribed users receive only mandatory items.
            self.audit.append(
                user.user_id,
                (note.notification_id,),
                audit_log.REASON_SUPPRESSED_UNSUBSCRIBED,
                now,
            )
            return None
        if note.urgent:
            # SPEC R3: urgent is never suppressed or deferred.
            return self._deliver(user, (note,), "immediate", now)
        if in_quiet_hours(now, user.utc_offset_hours):
            # SPEC R5: defer non-urgent delivery until quiet hours end.
            self.store.defer(note)
            self.audit.append(
                user.user_id,
                (note.notification_id,),
                audit_log.REASON_SUPPRESSED_QUIET_HOURS,
                now,
            )
            return None
        if not self.throttle.allow(user.user_id, now):
            # SPEC R8: daily send limit reached.
            self.audit.append(
                user.user_id,
                (note.notification_id,),
                audit_log.REASON_THROTTLED,
                now,
            )
            return None
        return self._deliver(user, (note,), "immediate", now)

    def _deliver(
        self,
        user: User,
        notes: tuple[Notification, ...],
        kind: str,
        now: datetime,
    ) -> Delivery:
        """Record one send event: delivery record, throttle count, audit entry."""
        delivery = Delivery(
            user.user_id, tuple(n.notification_id for n in notes), kind, now
        )
        self.store.record_delivery(delivery)  # SPEC R6
        self.throttle.record_send(user.user_id, now)  # SPEC R8: one send event
        self.audit.append(  # SPEC R9
            user.user_id,
            delivery.notification_ids,
            audit_log.delivered_reason(kind),
            now,
        )
        return delivery
