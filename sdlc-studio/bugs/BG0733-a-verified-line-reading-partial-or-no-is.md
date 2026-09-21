# BG0733: a Verified line reading PARTIAL or no is treated exactly like yes, so an honest self-report of a miss is laundered into a green

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Verification depth:** functional
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

- [ ] **AC1: a `Verified:` line that is not `yes` reports the criterion NOT satisfied, whatever its selector did.**
  - **Given** a story whose criterion carries a green `Verify:` selector and a `Verified:` line reading `PARTIAL`
  - **When** `verify_ac.py run --story <id>` runs
  - **Then** that criterion counts as failing, and the run's summary counts it in `fail`, not in `pass`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_a_partial_verified_line_fails_a_green_selector
- [ ] **AC2: the recorded reason travels with the verdict.**
  - **Given** the same criterion, whose `Verified:` line names why it is partial
  - **When** the run reports it
  - **Then** the reason appears against that criterion in the run's report, so a reader is told WHICH part is unmet rather than only that something is
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_the_recorded_reason_is_carried_into_the_report
- [ ] **AC3: a `Verified:` line reading `yes` over a green selector still passes.**
  - **Given** a criterion whose selector is green and whose `Verified:` line reads `yes`
  - **When** the run reports it
  - **Then** it passes - the discriminating half, because a check that fails every criterion carrying the field is not reading the field, it is refusing it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_a_yes_verified_line_over_a_green_selector_still_passes
- [ ] **AC4: a criterion carrying NO `Verified:` line is unaffected.**
  - **Given** a criterion with a green selector and no `Verified:` line at all, which is the shape of most criteria in this corpus
  - **When** the run reports it
  - **Then** it passes exactly as before - an absent field is not a denial, and treating it as one would redden the entire backlog at once
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_an_absent_verified_line_is_not_a_denial

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `verify_ac.py`, keep deriving the criterion's verdict from the selector's exit code alone, ignoring the parsed `Verified:` value - the shipped behaviour | a PARTIAL line fails a green selector |
| AC2 | in `verify_ac.py`, drop the recorded reason when building the per-criterion result, so the verdict flips but nothing says why | the reason travels with the verdict |
| AC3 | in `verify_ac.py`, treat ANY present `Verified:` line as a denial rather than comparing it to `yes` | a yes line still passes |
| AC4 | in `verify_ac.py`, default a missing `Verified:` value to a non-`yes` sentinel instead of leaving the criterion's verdict to its selector | an absent line is not a denial |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
