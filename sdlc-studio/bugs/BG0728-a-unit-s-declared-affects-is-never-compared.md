# BG0728: a unit's declared Affects is never compared with the files its delivering commit changed

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, tools/check_spec_claims.py, tools/tests/test_check_spec_claims.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0463 claim 20, still true, with a live instance: commit eacd23a3 `fix(US0455)` changed `sdlc-studio/personas.md`, and US0455's Affects names prd, tsd, trd, decisions and a test file - not personas.md. Affects drives the plan's collision analysis, the engagement floor and the gate's changed-surface pass, so an understated one mis-groups the unit everywhere at once. Nothing compares the declaration against the delivery, so the error is invisible from the moment it is made.

## Steps to Reproduce

1. `git show --stat eacd23a3` -> touches sdlc-studio/personas.md. 2. Read US0455's Affects -> personas.md absent. 3. Nothing in the tree reports the disagreement.

## Proposed Fix

At the terminal transition, compare the unit's Affects with the files of the commits naming it and report the difference - advisory first, since a legitimate late addition exists. Fix US0455's Affects as the instance. The general form is cheap because both halves are already available: `gitutil` can list a commit's files and Affects is already parsed.

## Acceptance Criteria

### AC1: a unit whose delivering commit touches a file its Affects does not name is reported

- **Given** US0455, whose Affects omits `sdlc-studio/personas.md` while commit eacd23a3 `fix(US0455)` changed it
- **When** the comparison runs at the unit's terminal transition
- **Then** the difference is reported with both lists named, advisory rather than blocking, because a legitimate late addition exists; and US0455's Affects is corrected as the instance
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/verify_ac.py`, compare only the declared Affects against itself - the declaration is then never joined to the delivery, and an understated footprint stays invisible from the moment it is made
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::AffectsVersusCommitTests::test_a_file_changed_by_the_delivering_commit_and_not_declared_is_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
