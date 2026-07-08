"""Tests for the notification service (docs/SPEC.md, R1-R10)."""
from datetime import datetime

from routing import NotificationService

NOON = datetime(2026, 3, 4, 12, 0)
LATE = datetime(2026, 3, 4, 23, 0)
NEXT_MORNING = datetime(2026, 3, 5, 8, 0)


def make_service(**kwargs) -> NotificationService:
    service = NotificationService(**kwargs)
    service.add_user("alice")
    return service


def test_immediate_delivery_and_audit():
    service = make_service()
    delivery = service.notify("alice", "hello", now=NOON)
    assert delivery.kind == "immediate"
    assert service.store.deliveries_for("alice") == [delivery]
    assert [e.reason for e in service.audit.for_user("alice")] == ["delivered"]


def test_notification_ids_unique_and_ordered():
    # SPEC R1/R2
    service = make_service()
    first = service.notify("alice", "one", now=NOON)
    second = service.notify("alice", "two", now=NOON)
    assert first.notification_ids[0] < second.notification_ids[0]


def test_quiet_hours_defer_then_release():
    # SPEC R5
    service = make_service()
    assert service.notify("alice", "late news", now=LATE) is None
    assert service.audit.for_user("alice")[-1].reason == "suppressed_quiet_hours"
    assert service.release_deferred(now=LATE) == []  # still quiet
    made = service.release_deferred(now=NEXT_MORNING)
    assert len(made) == 1


def test_quiet_hours_respect_user_offset():
    # SPEC R5: quiet hours follow the user's local time.
    service = make_service()
    service.add_user("dana", utc_offset_hours=5)
    evening_utc = datetime(2026, 3, 4, 18, 0)  # 23:00 local for dana
    assert service.notify("dana", "late there", now=evening_utc) is None
    assert service.notify("alice", "fine here", now=evening_utc) is not None


def test_urgent_ignores_quiet_hours():
    # SPEC R3
    service = make_service()
    assert service.notify("alice", "server down", urgent=True, now=LATE) is not None


def test_unsubscribed_receives_only_mandatory():
    # SPEC R7
    service = make_service()
    service.add_user("bob", subscribed=False)
    assert service.notify("bob", "promo", now=NOON) is None
    assert service.notify("bob", "terms update", mandatory=True, now=NOON) is not None
    reasons = [e.reason for e in service.audit.for_user("bob")]
    assert reasons == ["suppressed_unsubscribed", "delivered"]


def test_daily_throttle_blocks_after_limit():
    # SPEC R8
    service = make_service(throttle_limit=2)
    assert service.notify("alice", "one", now=NOON) is not None
    assert service.notify("alice", "two", now=NOON) is not None
    assert service.notify("alice", "three", now=NOON) is None
    assert service.audit.for_user("alice")[-1].reason == "throttled"
    assert service.throttle.sends_today("alice", NOON) == 2


def test_unknown_user_errors():
    # SPEC R4
    service = make_service()
    try:
        service.notify("nobody", "hi", now=NOON)
    except KeyError as exc:
        assert "nobody" in str(exc)
    else:
        raise AssertionError("expected KeyError for unknown user")


def test_cli_roundtrip():
    import cli

    service = NotificationService()
    assert cli.main(["add-user", "carol"], service=service) == 0
    assert (
        cli.main(
            ["notify", "carol", "hi", "--now", "2026-03-04T12:00:00"],
            service=service,
        )
        == 0
    )
    assert len(service.store.deliveries_for("carol")) == 1
