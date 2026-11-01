# BG1140: readiness.py tells a carried unit whose verifiers pass to close rather than be batched, but transition refuses its Done until the reviewer who rejected it approves

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_readiness.py, changelog.d/BG1140.md, .claude/skills/sdlc-studio/reference-scripts-review.md
> **Evidence:** 2026-10-31: `readiness.py check` over the run-four worklist, 24/25 ready, NOT READY US1076 (In Progress): already-satisfied; `transition.py set --id US1076 --status Done --dry-run` blocked on qa-seat-US1076-r1's REJECTs of 2026-10-19.
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-31T21:32:43Z

## Summary

US1076 was carried at the review cap in RUN-01M4R168. Its follow-up bug BG1078 is Fixed and its criteria now pass. `readiness.py check` marks it NOT READY (already-satisfied), with the guidance 'close it (do not re-build) rather than carrying it in the batch'. `transition.py set --status Done` refuses it on qa-seat-US1076-r1's unanswered REJECTs, and the review doctrine says a carried unit is delivered again in a later run and reaches Done only on that reviewer's APPROVE. Following the guidance leads to a refusal, and keeping the unit out of the batch leaves no run in which the APPROVE can be given.

## Steps to Reproduce

1. `readiness.py check --id US1076` prints NOT READY: already-satisfied, close it rather than carry it.
2. `transition.py set --id US1076 --status Done --dry-run` prints blocked: an unanswered delivery REJECT.
3. Expected: readiness names the carry, the reviewer id that can discharge it, and the rejoinder route (`critic.py brief --rejoinder` after a self-check), and does not mark the unit not-ready for the batch.

## Proposed Fix

In readiness, check for an unanswered delivery REJECT (the rule transition applies) before flagging already-satisfied. For a carried unit, report `carried: re-review by <reviewer id>` as a note, not an issue.

## Acceptance Criteria

- [ ] **AC1** A unit holding an unanswered delivery REJECT whose verifiers pass is not flagged already-satisfied. readiness names the carry and the reviewer id that can discharge it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py
- [ ] **AC2** A unit with no standing REJECT whose verifiers pass is still flagged already-satisfied (the positive control).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py

## Impact

Every carried unit whose follow-up bug was fixed elsewhere is stranded: told to close, refused Done, kept out of the batch. US1076 and US1086 have sat In Progress since 2026-10-19, holding EP0290 and CR0644 open.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | claude | Filed |
| 2026-11-01 | Claude Opus 5.5 | In flight: Affects widened to reference-scripts-review.md - its readiness row (:77) still calls already-satisfied a close-candidate with no carry exception, found by the builder |
