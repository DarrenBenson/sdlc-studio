# BG1235: Run six's round-2 and lane accept follow-ups: an unfailing help pin, unpinned counts, and accept's late refusals

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .githooks/pre-commit, changelog.d/BG1226.md, .claude/skills/sdlc-studio/scripts/tests/test_run_six_round_two_followups.py, changelog.d/BG1235.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** scratchpad run6/US1120-verdict-r2.txt, BG1224-verdict-r2.txt, BG1226-verdict-r2.txt, US1119-verdict-r1.txt
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T16:07:07Z

## Summary

2026-11-05, run six's round-2 reviews and US1119's round-1 review. US1120: the lane --help pin added in round 2 cannot fail, because that help prints only under the top-level sprint.py --help, so the round-2 commit's 'Both have a test' over-claims; 'not below 100k' survives AC3's test. BG1224: 'same five' has no pin. BG1226: the surface-page skip has no test in the unit's own suite, the skip note overstates when the other checks still run, and changelog.d/BG1226.md was not updated for round 2. US1119: a malformed --proof or --gap is refused only by lane return, after the unit is Done; the brief note's explicit-tier flag is dropped; a brief made with --rejoinder is refused because it is fingerprinted the wrong way, and the suggested fix records against a brief the reviewer never saw; three documented paths are untested.

## Steps to Reproduce

See the summary; each item was reproduced by its reviewer.

## Proposed Fix

Pin each, correct the over-claimed sentence and the BG1226 fragment, validate accept's pass-through flags before recording, and fingerprint a rejoinder brief as critic.py brief does.

## Acceptance Criteria

- [ ] **AC1** The lane help pin fails when the help line reverts; a malformed --proof is refused before the verdict is recorded; a rejoinder brief is accepted against its own fingerprint.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_six_round_two_followups.py

## Impact

Low: pins that cannot fail and late refusals.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
