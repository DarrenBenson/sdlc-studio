# BG0971: sprint close --dry-run reports later chain steps in the past tense ('lessons lifted', 'summary regenerated', 'anchor refreshed') although nothing was written

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_close_dry_run_wording.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0971.md
> **Evidence:** Found running a consuming project on the installed skill 6.1.0, 2026-10-07; confirmed by reading the code at sdlc-studio main fb1ce886. a consuming project's RUN-01M4APNQ: dry-run printed 'ok retro-extract: lessons lifted into the lessons stores', 'LC-002 graduating -> CR0555', 'ok lessons-summary: lessons summary regenerated', 'ok review-anchor: review anchor refreshed'; git status afterwards showed no change.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:37:11Z

## Summary

BG0593 made the dry run preview against a scratch tree, which is right, but the step lines keep the real close's wording. An operator reading 'lessons lifted' and 'CR0555 graduating' believes CRs were created and stores written, and may look for them or avoid re-running the close.

## Steps to Reproduce

`sprint.py close --retro <id> --dry-run` on a run whose retro is valid; read the ok lines; check `git status` - nothing changed.

## Proposed Fix

Render dry-run step results conditionally: 'would lift N lessons', 'would graduate LC-002 to a new CR', 'would regenerate', 'would refresh'.

## Acceptance Criteria

- [ ] **AC1** Every dry-run step line that the real close would write is worded as a preview, not a past action
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_dry_run_wording.py -k dry_run_lines_are_conditional

## Triage

- Reproduced at 8b844a80 by the code path: the step functions return fixed past-tense messages (sprint.py:4735, 4778) and the dry run reuses them. Since US0887 (2026-09-24). Reconcile's BG0557 advisory dismissed: BG0557 fixed a dry-run STOP the real close did not raise, not this wording.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 8b844a80, not a regression, consuming-project name generalised for the neutrality lane; changelog fragment added to Affects |
