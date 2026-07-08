# Ticket NT-142: digest delivery mode

Add a digest mode to the notification service.

Users can opt into digest delivery. Instead of receiving each
non-urgent notification immediately, an opted-in user has their
pending notifications batched into a single digest, which is flushed
by a new `send-digests` CLI command. Immediate delivery must keep
working for everyone else.

## Interface (agreed with the team)

- `User` gains a `delivery_mode` field, default `"immediate"`.
- `NotificationService.set_delivery_mode(user_id, mode)` switches a
  user between `"immediate"` and `"digest"`.
- `NotificationService.send_digests(*, now)` flushes pending digests
  and returns the deliveries it made. A flushed digest is a single
  `Delivery` of kind `"digest"` carrying the batched notification ids
  in creation order.
- `cli.py` gains `set-mode <user_id> <mode>` and
  `send-digests [--now ISO]` commands.

## Notes

- The service spec is in `docs/SPEC.md`.
- Existing tests live in `test_service.py`; they must keep passing.
