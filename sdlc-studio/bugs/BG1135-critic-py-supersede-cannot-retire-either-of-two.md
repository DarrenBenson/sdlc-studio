# BG1135: critic.py supersede cannot retire either of two delivery rows that share a unit, date, reviewer and verdict

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Depends on:** BG1109
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_supersede_by_brief.py, .claude/skills/sdlc-studio/help/review.md, changelog.d/BG1135.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md rows for BG0962 dated 2026-10-07; the refusal above, on 2026-10-27 at 135dc388.
> **Created:** 2026-10-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-27T22:52:46Z

## Summary

BG0962 holds two REJECT rows from qa-seat-BG0962-r1 dated 2026-10-07, which differ only in their brief fingerprints (9ef645b3012d and 2fe801ee8a2a). `critic.py supersede` narrows a match only by --reviewer and --verdict, so it refuses both rows as ambiguous, and an operator-authorised supersession under D0349 cannot be recorded. BG0962 left RUN-01M5EM9N only through a round-2 rejoinder review recorded under the round-one seat id, which cost a further review at the close.

## Steps to Reproduce

Run `critic.py supersede --unit BG0962 --date 2026-10-07 --verdict REJECT --reason ... --authorised-by 'Darren Benson (operator)' --boundary 'operator console'`. It prints `supersede refused: 2 delivery verdict rows match BG0962 dated 2026-10-07 - narrow it with --reviewer and/or --verdict`, though both are already given and nothing else can narrow it.

## Proposed Fix

Let supersede narrow by the row's brief fingerprint (`--brief <fingerprint>`), and name each matching row's fingerprint in the refusal so the operator can pick one.

## Acceptance Criteria

- [ ] **AC1** critic.py supersede --brief <fingerprint> retires exactly the one row with that fingerprint when several share unit, date, reviewer and verdict, and the refusal for an ambiguous match names each candidate's fingerprint.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_supersede_by_brief.py
  - **Verified:** yes (2026-11-01)

## Impact

A standing REJECT recorded twice in one round can never be retired, so its unit cannot be covered in a later run without recording an APPROVE under the original reviewer's id.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-27 | sdlc-studio | Filed |
| 2026-10-31 | Claude Opus 5.5 | Run-four plan (D0392): depends on BG1109, which shares a file this unit declares |
