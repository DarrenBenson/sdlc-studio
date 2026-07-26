# Reviews - LATEST (anchor)

> **CR0421 delivered (EP0162, US0433-US0436) - closing review [RV0017](RV0017-cr0421-delivery-closing-review-ep0162-four-units-one.md).**
> One independent adversarial wave (fresh context, RFC0051/D0059): **APPROVE**, no MAJOR. MINOR-2 fixed in-sprint (e0529b51); three residual findings declined with reasons (RETRO0074). Reviewer-of-record sign-off is OWED and is the operator's - the two-role gate holds Done until it lands.

## What shipped

- **US0433** - `sprint batch drop/add` mutate an open run's approved batch; drop releases the done-gate, distinct from Deferred.
- **US0434** - the sprint close's conformance lane is scoped to its batch; out-of-batch debt no longer blocks an in-batch close; `--release` still judges everything.
- **US0435** - a growing outstanding set names the way out honestly: file-and-close for deferrable items, "clear the lanes" for hard blockers.
- **US0436** - review currency judged by the review RECORD, not the anchor's commit time; the byte-identical re-stamp trap is closed; the invariant is stated in `reference-sprint.md`.

## Currency

This anchor is current with the batch as of the close. Currency is judged by the review record (`.local/review-state.json`), per US0436.
