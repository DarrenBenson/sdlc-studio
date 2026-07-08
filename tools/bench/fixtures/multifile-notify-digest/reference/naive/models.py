"""Data models for the notification service.

All datetimes are naive and interpreted as UTC; time-dependent logic
always receives an explicit ``now`` (SPEC R10).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """A registered recipient of notifications."""

    user_id: str
    subscribed: bool = True
    utc_offset_hours: int = 0
    delivery_mode: str = "immediate"  # NT-142: "immediate" or "digest"


@dataclass(frozen=True)
class Notification:
    """A single message addressed to one user."""

    notification_id: int
    user_id: str
    body: str
    urgent: bool = False
    mandatory: bool = False


@dataclass(frozen=True)
class Delivery:
    """A record of one send event (SPEC R6).

    ``notification_ids`` lists every notification carried by the send;
    ``kind`` names the delivery mechanism (currently ``"immediate"``).
    """

    user_id: str
    notification_ids: tuple[int, ...]
    kind: str
    sent_at: datetime
