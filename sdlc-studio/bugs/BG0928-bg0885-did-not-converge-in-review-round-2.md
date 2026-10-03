# BG0928: BG0885 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_finding_escape.py, changelog.d/BG0885.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T03:29:31Z

## Summary

BG0885 was rejected at round 2, the review cap, by qa-seat-BG0885-r1, so it was carried as a known issue rather than reviewed again. The findings still open: [regression] low: the round-1 backslash loss survives in the sibling reader - \_supersede\_field (critic.py:860) now calls the span-blind \_unescape, so a supersession reason quoting a code span holding a typed backslash before a bracket after ] or ) (reason "span `a]\[b` here") reads back as `a][b` through critic.py supersede then read\_supersessions, byte-exact at 347b70f5^ (parse\_findings is span-aware and reads the same text exactly) - round-1 findings ruled: the parse\_findings backslash loss CLOSED, the unpinned ) branch CLOSED, the 1740 comment CLOSED; [pre-existing] low: split\_items (critic.py:1097) collapses a typed double backslash so a regex finding holding \\ reads back with one, identical at 347b70f5^; [pre-existing] low: the idempotent underscore writer (critic.py:156) stores a typed \_ and a bare \_ as the same bytes, so a typed \_ now reads back as \_ as AC1 requires and the changelog discloses; BLOCKING: [regression] low: a supersession reason holding a code span with a typed backslash before a bracket after ] or ) loses that backslash on read because \_supersede\_field uses the span-blind \_unescape (critic.py:860)

## Steps to Reproduce

1. Read the round 2 REJECT of BG0885 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0885 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: [regression] low: the round-1 backslash loss survives in the sibling reader - \_supersede\_field (critic.py:860) now calls the span-blind \_unescape, so a supersession reason quoting a code span holding a typed backslash before a bracket after ] or ) (reason "span `a]\[b` here") reads back as `a][b` through critic.py supersede then read\_supersessions, byte-exact at 347b70f5^ (parse\_findings is span-aware and reads the same text exactly) - round-1 findings ruled: the parse\_findings backslash loss CLOSED, the unpinned ) branch CLOSED, the 1740 comment CLOSED
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] low: split\_items (critic.py:1097) collapses a typed double backslash so a regex finding holding \ reads back with one, identical at 347b70f5^
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** The round 2 REJECT finding no longer holds: [pre-existing] low: the idempotent underscore writer (critic.py:156) stores a typed \_ and a bare \_ as the same bytes, so a typed \_ now reads back as \_ as AC1 requires and the changelog discloses
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC4** The round 2 REJECT finding no longer holds: BLOCKING: [regression] low: a supersession reason holding a code span with a typed backslash before a bracket after ] or ) loses that backslash on read because \_supersede\_field uses the span-blind \_unescape (critic.py:860)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC5** BG0885 AC1 still passes: Given a fixture bug briefed with `critic.py brief`, when `critic.py record ... --issues '[new] the shape [A-Z][A-Z_]{4,} matches UNKNOWN'` writes the verdict, then markdownlint with this repository's config reports no MD052 on `critic-verdicts.md`, and the ledger's reader (`critic.parse_findings` on the recorded row) returns the finding text exactly as given.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_finding_escape.py::VerdictFindingEscapeTests::test_a_bracketed_finding_lints_and_reads_back
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
