# BG0444: the PRE_GATE independence hole was closed in sprint.py only, so conformance.py still clears a unit on the migration sentinel

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; the caller sweep found four hand-rolled sites neither report named)
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** engineering amigo seat (independent, isolated worktree); human; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`sprint.review_coverage` ANDs `critic.is_independent` onto `critic.sprint_covers_independently`, with a comment explaining why: the latter tests only non-empty-and-distinct, so the `PRE_GATE` migration sentinel cleared the gate. `conformance.py:311` still calls `sprint_covers_independently` alone and never applies the second predicate. The defect was MOVED, not closed - it survives in the module that actually gates Done.

## Steps to Reproduce

Executed at d7a1ad8f, 2026-07-30. For the row `{'verdict':'APPROVE','reviewer':'bob','author':critic.PRE_GATE}`:

```text
`sprint_covers_independently` -> True
`is_independent`            -> False
```

`sprint.py:4456-4461` applies both and correctly refuses. `conformance.py:311` applies the first only and accepts. Found by the engineering amigo seat during the close of RUN-01KYPZ1G.

This is the second instance in one batch of one rule living in two implementations that disagree (see also the `review_coverage` / conformance disagreement filed separately), which is the shared-field divergence class CR0504 names.

## Proposed Fix

One seam, not a second conjunction. There are currently FOUR independence predicates - `is_independent`, `sprint_covers_independently`, `is_independent_signoff`, and a hand-rolled fourth inline in `sprint.py` reaching into `critic._id`, a private name in a sibling module. Correctness depends on each caller remembering which combination to AND, and nothing checks that the four agree. Collapse them to one authority that answers the whole question, and add a test asserting every caller routes through it. Adding the missing AND to conformance.py fixes this instance and leaves the shape that produced it.

## Acceptance Criteria

### AC1: the PRE_GATE sentinel is refused by EVERY predicate, not just one

- **Given** a row whose author is the `PRE_GATE` migration sentinel
- **When** each independence predicate judges it
- **Then** all refuse - `sprint_covers_independently` tested only non-empty-and-distinct, so `sprint.review_coverage` compensated by AND-ing a second predicate on and `conformance.py` did not. The same row cleared Done in one module and was refused in the other
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::OneIndependenceAuthorityTests::test_the_PRE_GATE_sentinel_is_refused_by_EVERY_predicate
- **Verified:** yes (2026-07-30)

### AC2: the predicates AGREE across every pair of identities

- **Given** empty, floored, self-reviewing, escaped and sentinel identities
- **When** the authority and each predicate judge the same pair
- **Then** they return the same answer for every case - the property the four never had. A caller can no longer be wrong by picking one, which is the shape that produced this bug rather than the instance
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::OneIndependenceAuthorityTests::test_the_predicates_AGREE_across_every_pair
- **Verified:** yes (2026-07-30)

### AC3: no module rebuilds the test from the authority's private parts

- **Given** every shipped script
- **When** the sweep runs
- **Then** none hand-rolls the comparison. Adding the missing AND to `conformance.py` would have fixed this instance and left the shape; there is now ONE authority, `critic.independence`, returning the reason as well as the verdict, plus a public `same_identity` for the callers asking a different question
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::OneIndependenceAuthorityTests::test_NO_module_hand_rolls_the_independence_comparison
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | engineering amigo seat (independent, isolated worktree) | Filed |
