# EP0232: An uncovered production hunk is found by reverting it, not by reading it

> **Status:** Draft
> **Derived Point Total:** 16
> **Parent:** CR0533
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0533. Delivers the work CR0533 requested.

## Story Breakdown

- [ ] [US0754: The check reverts each hunk of a unit's declared Affects in turn and reports GREEN as uncovered](../stories/US0754-the-check-reverts-each-hunk-of-a-unit.md)
- [ ] [US0755: All five measured instances from RUN-01KZ9315 are reported - the named regression corpus](../stories/US0755-all-five-measured-instances-from-run-01kz9315-are.md)
- [ ] [US0756: A legitimately uncovered hunk is ANSWERABLE and the answer is recorded rather than assumed](../stories/US0756-a-legitimately-uncovered-hunk-is-answerable-and-the.md)
- [ ] [US0757: It runs at the BATCH BOUNDARY, and the placement is a recorded decision](../stories/US0757-it-runs-at-the-batch-boundary-and-the.md)
- [ ] [US0758: An uncovered hunk is distinguished from one whose verifiers could not RUN](../stories/US0758-an-uncovered-hunk-is-distinguished-from-one-whose.md)

## Acceptance Criteria (Epic Level)

- [ ] The check exists as a command and reports per hunk: given a unit and a base ref, it reverts each hunk of the unit's declared Affects in turn and reports GREEN (uncovered) or RED (covered), naming the hunk and the criterion whose Verify line should have covered it. Mutant: report per FILE rather than per hunk - a file with one covered hunk reads as covered, which is the granularity the five findings would each have slipped through.
- [ ] Every one of the five measured instances from RUN-01KZ9315 is reported by it. This is the regression corpus and it is named on the criterion, not chosen at implementation time: `sprint_report._sprint_cost_line`, critic `record_signoff`'s disjointness raise, critic `_ensure_trailing_column`'s pad, critic `cmd_record`'s tier arguments, `sprint_report.operator_summary`'s carried and filed. Mutant: implement against a fixture instead - the corpus rows go unreported.
- [ ] A hunk that is legitimately uncovered is ANSWERABLE, and the answer is recorded rather than assumed. A comment-only or logging hunk is not a defect, so the check reports and the answer is a decision somebody made; only an UNANSWERED report blocks. Mutant: refuse blindly - the check is switched off within a day, which is what happened to the gate budget ceiling twice.
- [ ] It runs at the BATCH BOUNDARY, not per commit, and the placement is a recorded decision. The commit gate is already over its 380s budget on every commit of the sprint that produced this evidence; per-hunk reversion multiplies the suite cost by the hunk count. Mutant: wire it into pre-commit - measure the gate before and after and watch it exceed its ceiling.
- [ ] The report distinguishes an uncovered hunk from a hunk whose verifiers could not RUN. A verifier that errors is not evidence of coverage and must never be reported as RED. Mutant: treat a non-zero exit as covered - a broken verifier certifies the hunk it could not judge, which is this project's recurring false-green class.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
