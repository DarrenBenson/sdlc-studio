# BG1585: The pre-commit gate lane passes the whole reconcile detect JSON through one environment variable, so on a large corpus it dies with Argument list too long and never prints the drift detail

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .githooks/pre-commit, tools/tests/test_lean_precommit_parallel.py, changelog.d/BG1585.md
> **Evidence:** Run sixteen paperwork commit, 2026-11-18, .local/run16/commit-paper3.log line 23.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T08:36:10Z

## Summary

When the artefact gate fails, the pre-commit gate lane runs reconcile detect --format json and hands the output to a python3 -c reader through the `DRIFT_JSON` environment variable. The JSON now runs to about 143 KB, past Linux's 128 KB limit on a single argument or environment string (`MAX_ARG_STRLEN)`, so exec fails with 'python3: Argument list too long' and the self-diagnosing per-item drift list is lost. Met in run sixteen when CR0729 drifted: the commit was blocked with only '1 drift item(s)' and no item named.

## Steps to Reproduce

With the corpus at HEAD (reconcile detect --format json | wc -c prints about 142769), make one drift item, for example a CR whose children are all resolved, and commit. The gate lane prints '.githooks/pre-commit: line 358: /usr/bin/python3: Argument list too long' and no '- drift detail -' block.

## Proposed Fix

Pipe the JSON to the reader on stdin (or have reconcile detect print the drift lines itself) instead of passing it in an environment variable; add a test with a detect output larger than 128 KB.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: When the artefact gate fails, the pre-commit gate lane runs reconcile detect --format json and hands the output to a python3 -c reader through the `DRIFT_JSON`...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: With the corpus at HEAD (reconcile detect --format json | wc -c prints about 142769), make one drift item, for example a CR whose children are all resolved...
- [ ] **AC3** The proposed fix lands, pinned by a test: Pipe the JSON to the reader on stdin (or have reconcile detect print the drift lines itself) instead of passing it in an environment variable; add a test with...

## Impact

A blocked commit no longer names its drift, so the author has to run reconcile detect by hand and read through hundreds of advisory lines to find it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
