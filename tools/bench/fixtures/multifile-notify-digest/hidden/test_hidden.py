"""Hidden acceptance suite for ticket NT-142 (digest delivery mode).

Each test names the SPEC requirement it exercises. Everything asserted
here follows from docs/SPEC.md plus the ticket; a careful reader of the
visible workspace can pass every test.
"""
from datetime import datetime

NOON = datetime(2026, 3, 4, 12, 0)
AFTERNOON = datetime(2026, 3, 4, 15, 0)
QUIET = datetime(2026, 3, 4, 23, 0)
NEXT_MORNING = datetime(2026, 3, 5, 9, 0)


def digest_user(service, user_id="dee", **kwargs):
    service.add_user(user_id, **kwargs)
    service.set_delivery_mode(user_id, "digest")
    return user_id


def digests_for(service, user_id):
    return [d for d in service.store.deliveries_for(user_id) if d.kind == "digest"]


def test_digest_batches_then_flushes(service):
    """Ticket happy path: non-urgent items batch into one flushed digest."""
    uid = digest_user(service)
    for body in ("one", "two", "three"):
        service.notify(uid, body, now=NOON)
    assert service.store.deliveries_for(uid) == []  # nothing sent yet
    service.send_digests(now=AFTERNOON)
    digests = digests_for(service, uid)
    assert len(digests) == 1
    assert len(digests[0].notification_ids) == 3
    # SPEC R2: creation order preserved within the digest.
    assert list(digests[0].notification_ids) == sorted(digests[0].notification_ids)


def test_immediate_users_unaffected(service):
    """Ticket: immediate delivery keeps working for everyone else."""
    service.add_user("imogen")
    delivery = service.notify("imogen", "hello", now=NOON)
    assert delivery is not None
    assert delivery.kind == "immediate"


def test_urgent_bypasses_digest(service):
    """SPEC R3: urgent is delivered immediately, never batched."""
    uid = digest_user(service)
    delivery = service.notify(uid, "server down", urgent=True, now=NOON)
    assert delivery is not None
    assert delivery.kind == "immediate"
    service.send_digests(now=AFTERNOON)
    for digest in digests_for(service, uid):
        assert delivery.notification_ids[0] not in digest.notification_ids


def test_unsubscribed_digest_contains_only_mandatory(service):
    """SPEC R7: unsubscribed users receive only mandatory items - digests too."""
    uid = digest_user(service, subscribed=False)
    service.notify(uid, "promo", now=NOON)
    service.notify(uid, "terms update", mandatory=True, now=NOON)
    service.send_digests(now=AFTERNOON)
    mandatory_ids = {
        n.notification_id for n in service.store.notifications if n.mandatory
    }
    digests = digests_for(service, uid)
    assert len(digests) == 1
    assert set(digests[0].notification_ids) == mandatory_ids


def test_quiet_hours_defer_digest_flush(service):
    """SPEC R5: no digest lands during the user's quiet hours - nor is it lost."""
    uid = digest_user(service)
    service.notify(uid, "afternoon news", now=NOON)
    service.send_digests(now=QUIET)
    assert digests_for(service, uid) == []  # deferred, not sent
    service.send_digests(now=NEXT_MORNING)
    digests = digests_for(service, uid)
    assert len(digests) == 1
    assert len(digests[0].notification_ids) == 1  # not lost


def test_digest_flush_counts_one_send(service):
    """SPEC R8: a flushed digest of N items is ONE send against the throttle."""
    uid = digest_user(service)
    for i in range(4):
        service.notify(uid, f"item {i}", now=NOON)
    service.send_digests(now=AFTERNOON)
    assert service.throttle.sends_today(uid, AFTERNOON) == 1


def test_digest_flush_writes_one_audit_entry(service):
    """SPEC R9: one audit entry per delivery event, reason delivered_digest."""
    uid = digest_user(service)
    for body in ("a", "b", "c"):
        service.notify(uid, body, now=NOON)
    service.send_digests(now=AFTERNOON)
    entries = [
        e for e in service.audit.for_user(uid) if e.reason == "delivered_digest"
    ]
    assert len(entries) == 1
    assert len(entries[0].notification_ids) == 3


def test_empty_digest_sends_nothing(service):
    """Flushing a user with nothing pending sends nothing and costs nothing."""
    uid = digest_user(service)
    made = service.send_digests(now=NOON)
    assert [d for d in made if d.user_id == uid] == []
    assert digests_for(service, uid) == []
    assert service.throttle.sends_today(uid, NOON) == 0
