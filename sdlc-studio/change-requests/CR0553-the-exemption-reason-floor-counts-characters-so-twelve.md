# CR-0553: The exemption reason floor counts characters, so twelve junk characters buy a blanket revert-check exemption

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M0JD1W delivery review, 2026-08-21: `zzzzzzzzzzzz` executed as a reason and admitted, reported [pre-existing] against `_reason_substance` (a8ebe550).
> **Date:** 2026-08-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_reason_substance` decides whether a declared exemption carries a real reason by measuring the LENGTH of its meaning-bearing tokens - twelve characters or more passes. Twelve characters of anything passes: an independent reviewer executed `zzzzzzzzzzzz` and it was admitted.

The predicate predates this work and is used by the `unnameable` plan-row marker. RUN-01M0JD1W extended it to `Revert-check-exempt`, which is a materially more consequential gate: an `unnameable` row exempts one criterion from one mutation row, while a `Revert-check-exempt` field naming several ids exempts them from the check that asks whether the unit's tests reach its production change at all.

## Impact

Every project using the exemption markers. The design intent is stated in the code itself - a state that costs nothing to enter is the state every awkward criterion chooses - and a character count is very nearly nothing. The cost is not that somebody types twelve z's on purpose; it is that a hurried, contentless reason ('see above', repeated to length) passes the same check a considered one does, so the marker stops discriminating and the reviewer reading it cannot tell which kind they are looking at.

## Acceptance Criteria

- [ ] Given a declared exemption reason of twelve or more characters carrying no distinct meaning-bearing tokens, when the exemption is read, then it is REFUSED - the paired control being a short but genuine reason, which must still pass
- [ ] Given a reason that is mostly the criterion's own words returned to it, when the exemption is read, then it is refused as a restatement, on the same overlap test the test-plan rows already use
- [ ] Given one reason repeated verbatim across several criterion ids, when the exemption is read, then it is refused, because that is the shape an author reaches for when exempting a batch wholesale
- [ ] Given the existing corpus, when the tightened floor runs over it, then the number of exemptions it newly refuses is REPORTED before the check is allowed to block, so the change earns its place on a measurement rather than on assertion

## Recommendation

Do not raise the number - a longer string of junk is still junk, and a higher floor mostly trains authors to pad. Ask for something a checker can verify instead: distinct meaning-bearing tokens rather than characters, a refusal of a reason that is mostly the criterion's own words back (the overlap test `testplan_row_faults` already applies to mutant prose), and a refusal of a reason repeated verbatim across several ids, which is the shape an author reaches for when exempting a batch wholesale.

Filed rather than repaired in place because it is `[pre-existing]` by execution - `git log -S` puts `_reason_substance` at a8ebe550, before this batch - and a review scope rule this repository enforces says a pre-existing defect is reported with its id and does not hold the gate. Related: BG0600, on `testplan_derive` refusing well-formed exemptions.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Raised |
