# CR-0237: verify_ac conflates an omitted Verify line with a declared manual one

> **Status:** Complete
> **Size:** M
> **Target:** v4.1
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson; persona; v1

## Summary

Surfaced by the CR0233 review (2026-07-13) as a non-blocking residual, with a working reproduction. `verify_ac.verify_story` (~L554) counts both 'this AC has no Verify: line at all' and 'this AC is explicitly Verify: manual' into the same report.manual counter. The two are completely different claims: one is an omission, the other is a declared judgement call. Because the lane cannot tell them apart, CR0233's new vacuity guard had to be repo-wide rather than per-story - one executable AC anywhere in the story set lets every unverified story ride along. Under `conformance.adopt_after` grandfathering that story is also exempt from conformance, so neither lane that polices the AC layer examines it, and DELETING a rotted Verify line (rather than fixing it) still reaches a green release gate. Reproduced: a workspace with `adopt_after` 82, one grandfathered story with two verifier-less ACs plus one story with a green executable AC, gives 'conformance: 1 exempt' and 'verify: 1/3 executable AC(s) green' and gate --release PASS, exit 0.

## Impact

This is the last remaining route by which a rotted Verify layer reaches a tag - the exact class that produced BG0104. CR0233 closed the degenerate whole-repo case; this closes the per-story one.

**Effort:** M

## Acceptance Criteria

- [ ] `verify_ac` distinguishes a declared 'Verify: manual' AC from an AC with no Verify line at all, reporting them as separate counts (declared-manual vs unspecified)
- [ ] The gate's vacuity guard becomes per-story rather than repo-wide: a story with unspecified ACs is named, and a story whose ACs are all declared-manual is not over-fired on
- [ ] A regression test proves a grandfathered story with a deleted Verify line can no longer reach a green release gate, and that a legitimately all-manual story still can

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | audit | Raised |
