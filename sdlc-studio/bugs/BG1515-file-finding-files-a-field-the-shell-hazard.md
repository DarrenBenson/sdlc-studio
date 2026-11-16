# BG1515: file_finding files a field the shell-hazard sweep refuses, so the refusal arrives at the push gate's full suite instead of at filing

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T20:30:46Z

## Summary

BG1507's Steps carried a `$(` command substitution and BG1514's Summary a quoted assertion with a space before a colon. `file_finding.py` filed both from a --fields-file, the commit's selected lanes passed them, and the push gate's full suite refused main on `test_shell_hazard_rate`'s legitimate-field sweep, 14 minutes later.

## Steps to Reproduce

1. File a bug whose steps field holds a dollar sign and an opening parenthesis, with --fields-file.
2. Commit it: the commit passes.
3. Push: the push gate's full suite reds `test_shell_hazard_rate.`

## Proposed Fix

Run the same shell-hazard detector over each field at filing and refuse, naming the field and the hazard, as the sweep would.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1507's Steps carried a `$(` command substitution and BG1514's Summary a quoted assertion with a space before a colon.
- [ ] **AC2** The proposed fix lands, pinned by a test: Run the same shell-hazard detector over each field at filing and refuse, naming the field and the hazard, as the sweep would.

## Impact

One push-gate cycle per hazardous phrase in a filed finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
