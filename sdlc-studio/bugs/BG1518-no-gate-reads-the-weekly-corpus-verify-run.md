# BG1518: No gate reads the weekly corpus-verify run, the only automated run of every Verify line

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .githooks/pre-push, sdlc-studio/tsd.md, tools/tests/test_pre_push_hook.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, tsd lens, survived 3 of 3 refute votes; observed at .githooks/pre-push lines 135-146 (read_ci: `gh run list --workflow Lint --branch main --event push`); sdlc-studio/tsd.md Pipeline Stages item 6 (line 664) and the CI jobs table (line 685); .github/workflows/lint.yml job `corpus-verify` (lines 145-234)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:21:42Z

## Summary

The TSD names the scheduled `corpus-verify` job in the Lint workflow as the automated run of every Verify line, standing in for a release gate at each tag. The job runs and can fail, but nothing consumes its conclusion: the red-main read in `.githooks/pre-push` filters to push-triggered runs and its comment says it never reads a scheduled corpus run, and neither `release_cut.py`, `status.py` nor any other hook or workflow step names the scheduled run. The scheduled run failed in five of the six weeks to 2026-11-16, including the day v6.4.0 was tagged, and each red was noticed only because someone opened the Actions tab and filed it by hand. That is the failure the red-main read was written to end for push runs, and the TSD gives this gate no row saying who reads it.

## Steps to Reproduce

1. Read `read_ci` in .githooks/pre-push (about lines 135 to 146): the forge query is limited to the push event and the comment excludes a scheduled corpus run.
2. Read sdlc-studio/tsd.md Pipeline Stages item 6 (about line 664) and the CI jobs table: the weekly job is called the automated run of every Verify line, with no reader named.
3. Search `release_cut.py`, status.py, the three hooks and tools/`known_issues.py` for schedule and corpus-verify: the only hit is the pre-push comment that excludes scheduled runs.
4. List the last six scheduled runs of the Lint workflow with the gh CLI: five of six conclude failure, each with the corpus-verify job red.

## Proposed Fix

Give the scheduled conclusion a reader in the command people run. Extend the pre-push red-main read to ask the forge for the latest completed scheduled Lint run on main as well, and refuse on any conclusion but success until that run's id is acknowledged once per clone, reusing the existing acknowledgement file and keeping the offline behaviour unchanged. Add a row to the TSD quality-gate table naming that reader. Pin both the refusal and a green positive control in the pre-push hook test with a stubbed gh.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The TSD names the scheduled `corpus-verify` job in the Lint workflow as the automated run of every Verify line, standing in for a release gate at each tag.
- [ ] **AC2** The proposed fix lands, pinned by a test: Give the scheduled conclusion a reader in the command people run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
