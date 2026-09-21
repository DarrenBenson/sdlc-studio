# BG0733: a Verified line reading PARTIAL or no is treated exactly like yes, so an honest self-report of a miss is laundered into a green

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A criterion's `Verified:` line is PROSE. Nothing reads it: the verdict comes solely from the `Verify:` selector's exit code. So a delivery that discovers a criterion is unmet, and says so on the artefact in the field that exists for exactly that purpose, changes nothing the machinery sees - the unit still reports pass, the close still counts it covered, and the report of record still prints it as satisfied. The honest disclosure is silently converted into a claim of success, which is worse than not writing it, because a later reader sees the word PARTIAL beside a green verdict and cannot tell which the tooling believed. Found in RUN-01M306PY by an independent delivery reviewer who approved a PARTIAL disposition and then warned, in the same breath, that the disposition only means anything if the gate reads it - and it does not. Verified immediately: US0853 read `ac=2 pass=2 fail=0` with one criterion's `Verified:` line reading PARTIAL and naming exactly which two of fifteen cases failed.

## Steps to Reproduce

1. Take any story whose criteria pass their selectors. 2. Change one criterion's `Verified:` line from `yes` to `PARTIAL` or to `no`, with a reason. 3. Run `verify_ac.py run --story <id>`. 4. It still reports that criterion as passing, and the close still counts the unit as covered. Observed on US0853 on 2026-09-21.

## Proposed Fix

Read the field. The cheapest honest form: a criterion whose `Verified:` line is anything other than `yes` is reported as NOT satisfied regardless of its selector's exit code, and the report of record renders it with the recorded reason beside it. That makes the field load-bearing rather than decorative and gives a delivery a way to record a miss that the machinery respects. Note the interaction with this project's own scar about fields nobody reads - BG0463 claim 15 is the `authority` field, the same defect in a different structure. The deeper fix, if it is wanted, is that a criterion's verifier should test what the criterion CLAIMS, so the prose and the exit code cannot disagree; US0853's own AC2 was repaired that way in the same run, and it then correctly went red.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: A criterion's `Verified:` line is PROSE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
