# BG0525: US0629 AC2 asks derive to detect a polarity-flipped restatement, which is not mechanically decidable as written

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/stories/US0629-a-test-plan-is-derived-from-the-unit.md
> **Evidence:** Independent test-plan review at RUN-01KZ79C1, before implementation. The seat verified the parser behaviour by executing verify_ac.parse_story and sdlc_md.count_acs over constructed fixtures, and produced the defeating mutant concretely rather than as a hypothetical.
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

AC2 requires `derive` to refuse a mutant field that is "that criterion's own text with the polarity flipped". No implementation can decide that. Any attempt reduces it to a proxy - token overlap against the `Then` clause above some threshold, or a negation-word rule - and a threshold needs boundary rows on both sides to be testable at all.

Found by an independent seat reviewing the TEST PLAN before any code was written, which is US0631's mechanism performed by hand. The seat constructed a mutant that satisfies AC2's wording and defeats the obvious implementation: a field reading "in `verify_ac.py`, make it so the plan does not have exactly one row per criterion" names a real file, names an edit, AND is the criterion restated with its polarity flipped. A rule checking for a path-shaped token accepts it.

This is US0633's business - a criterion whose mutant cannot be named is refused at grooming - and it is the first live instance of exactly the class US0633 exists to catch.

## Steps to Reproduce

1. Read US0629 AC2.
2. Attempt to state, without writing code, the predicate that separates a legitimate mutant from a polarity-flipped restatement.
3. Observe that every candidate is a proxy requiring a tuned threshold, and that a restatement naming a real file defeats the path-presence proxy.

## Proposed Fix

Restate AC2 in decidable terms before implementing it. The seat's proposal, which is testable: the mutant must name a path listed in the unit's own `Affects:` AND carry an edit verb, AND must not exceed a stated overlap threshold against the criterion text - with a NEAR-MISS row named as its own case, so a legitimate mutant that happens to share the criterion's vocabulary is still accepted. House precedent for the shape is `_reason_substance` in `verify_ac.py`, which measures substance after filler is stripped and carries the scar of a one-character `-` passing a non-blank check.

## Acceptance Criteria

- [ ] The behaviour described is corrected: AC2 requires `derive` to refuse a mutant field that is "that criterion's own text with the polarity flipped".
- [ ] The proposed fix lands, pinned by a test: Restate AC2 in decidable terms before implementing it.

## Impact

As written, AC2 cannot be honestly ticked: any implementation satisfies its words while failing its intent, and the verifier would pin the proxy rather than the property. Ticking it would produce exactly the defect BG0523 records - a criterion marked Verified against evidence that cannot fail on what it claims.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Filed |
