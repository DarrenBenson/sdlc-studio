# BG0444: the PRE_GATE independence hole was closed in sprint.py only, so conformance.py still clears a unit on the migration sentinel

> **Status:** Open
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

- [ ] The behaviour described is corrected: `sprint.review_coverage` ANDs `critic.is_independent` onto `critic.sprint_covers_independently`, with a comment explaining why: the latter tests only...
- [ ] The proposed fix lands, pinned by a test: One seam, not a second conjunction.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | engineering amigo seat (independent, isolated worktree) | Filed |
