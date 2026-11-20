# BG1658: The goal brief's no-current-batch answer names a goal-review flag that does not exist, and two of US1036's framing branches have no test

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_per_seat.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T07:37:22Z

## Summary

US1036's engineering second seat (verdict sdlc-studio/reviews/verdicts/US1036/dcfb579577ef-5f9f68ae.txt, RUN-01M7VNR0). The NO CURRENT BATCH TO BRIEF answer (sprint.py:13034) tells the operator to run goal-review brief --worklist, but goal-review accepts only --brief-worklist, so following the advice is an argparse error. The text dates from BG0277. Also unpinned: a seat brief must open with its seat framing (a mutant moving the framing to the end survives), and an unknown seat with no plan written (a mutant there survives). The US1036 commit message overstates what the no-PRD test asserts.

## Steps to Reproduce

With a stale plan, run sprint.py goal-review brief: the answer says goal-review brief --worklist <file>. Run that: argparse refuses --worklist. Run goal-review --help: only --brief-worklist is listed.

## Proposed Fix

Name --brief-worklist in the answer and pin it with a test that runs the named command; add tests that the framing opens a seat brief and that an unknown seat is refused with no plan written.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1036's engineering second seat (verdict sdlc-studio/reviews/verdicts/US1036/dcfb579577ef-5f9f68ae.txt, RUN-01M7VNR0).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: With a stale plan, run sprint.py goal-review brief: the answer says goal-review brief --worklist <file>.
- [ ] **AC3** The proposed fix lands, pinned by a test: Name --brief-worklist in the answer and pin it with a test that runs the named command; add tests that the framing opens a seat brief and that an unknown seat...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
