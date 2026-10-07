# BG0965: retro.py validate ignores '## Actions raised' in a Keep/Stop/Try retro, so it reports '0 findings, all dispositioned' over rows it never read

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro_three_line_actions.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, changelog.d/BG0965.md
> **Evidence:** Found running a consuming project on the installed skill 6.1.0, 2026-10-07; confirmed by reading the code at sdlc-studio main fb1ce886. Concrete: the consuming project's RETRO0006 (19-row Actions raised table).
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:36:26Z

## Summary

`validate` (retro.py ~696) short-circuits for a three-line retro: `if is_three_line(text): ... return {..., 'findings': [], 'filed': [], ...}`. It never calls `dispositions_in`, even when the retro also carries a `## Actions raised` table. So `retro.py validate` prints 'ok - N lesson(s), 0 finding(s) all dispositioned (0 filed, 0 fixed in-sprint, 0 declined)' and `retro.py dispose` prints 'no findings recorded under ## Actions raised' (exit 1) for a retro whose Actions raised table has 19 rows - `dispositions_in(text)` called directly returns all 19. An UNDECIDED row in that table therefore passes the content gate unseen: the gate is satisfied by the format choice, not by the dispositions (the 'a gate satisfied by touch' class).

## Steps to Reproduce

Write a retro with `## Keep` / `## Stop` / `## Try` plus a `## Actions raised` table holding one row whose disposition is blank. Run `retro.py validate --id <id>` -> ok, 0 findings. Run `retro.py dispose --id <id>` -> 'no findings recorded'.

## Proposed Fix

In the three-line branch, still read `## Actions raised` when present and apply the same undecided-row errors (or refuse the section in a three-line retro with a message saying where findings belong). Never print 'all dispositioned' over a section that was not read.

## Acceptance Criteria

- [ ] **AC1** A three-line retro whose Actions raised table holds an undecided row fails validate, naming the row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_three_line_actions.py -k undecided_row_fails
- [ ] **AC2** validate and dispose report the same findings for a three-line retro that carries an Actions raised table
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_three_line_actions.py -k validate_and_dispose_agree

## Triage

- Reproduced at 8b844a80 by the code path: `validate`'s three-line branch (retro.py:710) returns `findings: []` without reading `## Actions raised`. Already in the code since US0875 (31ffb8fc, 2026-09-23); not a regression. Medium holds: the gate is satisfied by the retro's format rather than its dispositions.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 8b844a80, not a regression, consuming-project name generalised for the neutrality lane; changelog fragment added to Affects |
