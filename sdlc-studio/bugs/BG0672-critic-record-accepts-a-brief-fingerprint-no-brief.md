# BG0672: critic record accepts a --brief fingerprint no brief produced, recording the row as briefed with only a stderr note

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** backlog sweep 2026-09-15; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`critic.py record --brief <12 hex>` refuses an ABSENT fingerprint, but accepts any 12-hex string: a value no brief rendered prints a stderr NOTE (critic.py ~4220-4226, 'matches no brief this repo can currently produce') and the verdict row is written with that fingerprint in its Brief column, indistinguishable from a briefed one. AGENTS.md's refusal table says `critic record` refuses a verdict carrying no brief provenance; that holds for an absent value and not for an invented one. The note exists rather than a refusal because the matcher has false negatives (CR0511 findings #14 and #46: a tier-mismatched or first-round light brief matches no re-render), so refusing today would refuse honest verdicts. Reproduced in a throwaway fixture by the 2026-09-15 backlog sweep.

## Steps to Reproduce

1. In a throwaway workspace with one story, run `critic.py record --unit <id> --verdict APPROVE --reviewer r --author a --tier full --brief 0123456789ab`.
2. Observe exit 0, a stderr note that the fingerprint matches no brief, and a ledger row carrying `0123456789ab` in its Brief column with nothing marking it unmatched.

## Proposed Fix

Record the match result on the row itself (mark an unmatched fingerprint in the ledger) so every reader that counts a verdict as briefed can tell the difference, and have those readers not count an unmatched row as briefed. Once CR0511 #14/#46 close the matcher's false negatives, turn the note into a refusal.

## Acceptance Criteria

- [ ] **AC1** A verdict recorded with a fingerprint no brief produced carries an unmatched marker in the ledger row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::UnmatchedBriefFingerprintTests::test_an_invented_fingerprint_is_marked_on_the_row
- [ ] **AC2** A reader that counts a verdict as briefed does not count a row carrying the unmatched marker
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::UnmatchedBriefFingerprintTests::test_a_marked_row_is_not_counted_as_briefed
- [ ] **AC3** A verdict recorded with the fingerprint the brief verb printed carries no marker - the paired control
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::UnmatchedBriefFingerprintTests::test_a_real_fingerprint_is_unmarked

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | backlog sweep 2026-09-15 | Filed |
