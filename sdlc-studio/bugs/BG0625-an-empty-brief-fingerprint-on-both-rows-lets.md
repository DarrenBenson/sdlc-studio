# BG0625: an empty brief fingerprint on both rows lets a different seat's APPROVE retire a REJECT, which is the defect BG0607 exists to close

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Adversarial review of BG0607, wave 3 of RUN-01M0YXN3, 2026-08-26, finding 6. Reproduced by the reviewer in an isolated copy and reported as latent rather than live.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_unanswered_rejects` (critic.py:528-530) retires a REJECT when a later APPROVE carries the SAME brief fingerprint. An empty string equals an empty string, so two rows that both lack a brief match each other and a cross-seat approval retires the rejection - exactly the behaviour BG0607 replaced. Reproduced in isolation: REJECT by `engineering` with an empty brief, then APPROVE by `product` with an empty brief, and the standing verdict is APPROVE. LATENT today: 0 of 854 delivery rows carry an empty brief, because `critic record` refuses a verdict with no `--brief` provenance. It is reachable because AGENTS.md documents a recorded config decision that stands that requirement down, and any project taking it re-opens the hole.

## Steps to Reproduce

1. Record a REJECT with an empty brief from one seat. 2. Record an APPROVE with an empty brief from a DIFFERENT seat. 3. `critic.py show --unit <id>` prints APPROVE. Reproduced 2026-08-26 in an isolated fixture during the BG0607 review.

## Proposed Fix

Treat an absent fingerprint as matching NOTHING, not as matching every other absent one: `if not fp: out.append(r); continue` in `_unanswered_rejects`. That is the fail-closed direction - an unbriefed rejection stands until somebody answers it deliberately, which is what a missing provenance should cost.

## Acceptance Criteria

- [ ] **AC1** Given a REJECT and a later APPROVE that BOTH carry an empty brief, when the standing verdict is read, then it is the REJECT - an absent fingerprint matches NOTHING, which is the fail-closed direction a missing provenance should cost
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_an_absent_fingerprint_matches_nothing
- [ ] **AC2** Given a REJECT and a later APPROVE carrying the SAME non-empty brief, when the standing verdict is read, then it is the APPROVE - the paired control, so a seat can still retire its own rejection
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_a_matching_fingerprint_still_retires
- [ ] **AC3** Given this repository's corpus, when the change lands, then the conformance lane reports ZERO non-conformant units and the same conformant count as at run-open - no row carries an empty brief today, so a correct fix moves nothing. The count is read rather than assumed: a bare exit code cannot see the ratio move, and the figure this bug was filed with (608/690) was already stale by the time the batch was planned, because refining the discovery backlog added 124 units
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/conformance.py check | grep -qE '[0-9]+/[0-9]+ conformant.*, 0 not'

## Impact

It is the whole of BG0607, re-armed by a config decision the project explicitly offers. A consuming project that stands `--brief` down gets the last-row-wins behaviour back with no sign that anything changed, and BG0607's own criteria would still pass because every row in THIS corpus has a brief.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
