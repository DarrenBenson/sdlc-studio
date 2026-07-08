"""In-memory persistence for users, notifications and deliveries.

All collections are plain attributes so tests and tooling can inspect
service state directly.
"""
from __future__ import annotations

from models import Delivery, Notification, User


class InMemoryStore:
    """Holds all service state."""

    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.notifications: list[Notification] = []
        self.deliveries: list[Delivery] = []
        self.deferred: list[Notification] = []
        self._next_id = 1

    # -- users ------------------------------------------------------------

    def add_user(self, user: User) -> None:
        if user.user_id in self.users:
            raise ValueError(f"duplicate user id: {user.user_id}")
        self.users[user.user_id] = user

    def get_user(self, user_id: str) -> User:
        try:
            return self.users[user_id]
        except KeyError:
            # SPEC R4: unknown ids fail loudly.
            raise KeyError(f"unknown user id: {user_id}") from None

    # -- notifications ----------------------------------------------------

    def create_notification(
        self, user_id: str, body: str, urgent: bool, mandatory: bool
    ) -> Notification:
        # SPEC R1: unique, monotonically increasing ids.
        note = Notification(self._next_id, user_id, body, urgent, mandatory)
        self._next_id += 1
        self.notifications.append(note)
        return note

    # -- deliveries -------------------------------------------------------

    def record_delivery(self, delivery: Delivery) -> None:
        self.deliveries.append(delivery)

    def deliveries_for(self, user_id: str) -> list[Delivery]:
        return [d for d in self.deliveries if d.user_id == user_id]

    # -- quiet-hours deferrals (SPEC R5) ------------------------------------

    def defer(self, note: Notification) -> None:
        self.deferred.append(note)

    def drain_deferred(self) -> list[Notification]:
        drained, self.deferred = self.deferred, []
        return drained
