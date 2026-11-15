# BG1475: sprint close --dry-run takes about half an hour and prints nothing until it ends, mostly one git log per artefact in the review-current check

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py, changelog.d/BG1475.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run thirteen (RUN-01M7EYR3) close and dry runs, 2026-11-15; interrupt traceback in scratch close-dry2.txt.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T20:40:21Z

## Summary

On run thirteen, `sprint.py close --dry-run` ran 1,730 seconds with no output before its verdict, and the real close took 1,869 seconds. An interrupt showed the time in gate.py's review-current lane, where `review_prep.staleness` runs `git log -1 --format=%cI -- <path>` once per artefact (with a 10-second timeout each), and the close's preflight runs that lane again. An operator who cannot see progress cannot tell a slow close from a hung one; the first dry run here was killed by a 15-minute timeout with nothing printed.

## Steps to Reproduce

1. In this repository with an open run, run `sprint.py close --dry-run` and time it.
2. See no output for about half an hour.
3. Interrupt it: the traceback is in `review_prep._git_iso` under `gate._review_current.`

## Proposed Fix

Read every artefact's last commit time in one `git log --name-only --format=%cI` pass (or one `git log` per directory) and reuse the result for both gate runs, and print each close step as it starts.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: On run thirteen, `sprint.py close --dry-run` ran 1,730 seconds with no output before its verdict, and the real close took 1,869 seconds.
- [ ] **AC2** The proposed fix lands, pinned by a test: Read every artefact's last commit time in one `git log --name-only --format=%cI` pass (or one `git log` per directory) and reuse the result for both gate runs...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
