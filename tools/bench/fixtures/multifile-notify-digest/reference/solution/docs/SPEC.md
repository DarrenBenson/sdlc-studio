# Notification Service Specification

The service delivers notifications to registered users. All datetimes
are naive and interpreted as UTC; every time-dependent operation takes
an explicit `now`.

## Requirements

- **R1.** Every notification is assigned a unique, monotonically
  increasing integer id at creation.
- **R2.** When a single delivery carries several notifications, they
  appear in creation order.
- **R3.** Urgent notifications are always delivered immediately and
  are never suppressed, deferred or held back by any other mechanism.
- **R4.** Operations naming an unknown user id fail with an error;
  they never silently drop the request.
- **R5.** Quiet hours run 22:00-07:00 in the user's local time,
  derived from their `utc_offset_hours`. Non-urgent delivery is
  suppressed during quiet hours; suppressed deliveries are deferred,
  not dropped, and are delivered once quiet hours end.
- **R6.** Every send is recorded as a `Delivery` carrying the ids of
  all notifications it contains and its `kind`
  (e.g. `"immediate"`).
- **R7.** An unsubscribed user receives only notifications flagged
  `mandatory=True`; anything else addressed to them is suppressed.
- **R8.** Each user is limited to a fixed number of sends per UTC day
  (default 5). The throttle counts sends - delivery events - not the
  notifications contained in them.
- **R9.** Every delivery attempt appends exactly one audit log entry
  with a reason code: `delivered`, `suppressed_quiet_hours`,
  `suppressed_unsubscribed` or `throttled`. A successful send of any
  other delivery kind uses the reason `delivered_<kind>`.
- **R10.** No logic path reads the wall clock; `now` is always a
  parameter so behaviour is reproducible in tests. Only the CLI
  boundary may default to the current time.
