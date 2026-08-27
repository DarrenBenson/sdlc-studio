# BG0615: an abandoned guided-onboarding marker outranks the whole hint ladder forever, so an established project is told to go and onboard itself

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional [[derived: criteria 5; plan rows 5; executed 5; killed 5; survived 0; not-run 0; entry point 2 of 5 criteria through the shipped CLI, 3 in-process | fp 6723aa54a7d9 ]] (three criteria over the onboarding hint, each with its own mutant executed and killed: the tree check dropped, every stage claimed done, and the supersession report emptied. FIXTURE reproductions throughout - the stale marker was moved out of this tree the day the bug was filed, so re-running against the tree as it stands would prove only that somebody tidied up)
> **Points:** 3
> **Depends on:** BG0621
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py, .claude/skills/sdlc-studio/help/hint.md
> **Evidence:** Found by running `/sdlc-studio hint` on 2026-08-26. THE SYMPTOM IS NO LONGER IN THIS TREE: the stale marker was moved out of `sdlc-studio/.local/` once the defect was filed, so closing evidence must be a FIXTURE reproduction - restore a marker into a temp fixture and assert the hint flips - never a re-run against the tree as it stands. A symptom that disappeared because somebody tidied it away is not a fixed defect. Marker dated 2026-08-14 02:47 with 7/7 stages pending; each stage's output verified present on disk by a scan before filing. Gate behaviour quoted from source at status.py:490-492 and init.py:311-314 per D0151.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`status._compute_hint_rung` calls `_onboarding_hint` FIRST and returns its answer whenever any stage is pending (status.py:490-492), and `init.first_incomplete` decides that purely from the marker's own `status` field (init.py:311-314). Neither asks whether the stage's output already exists. So a `sdlc-studio/.local/onboarding.json` written once and abandoned outranks the pipeline ladder permanently, and no state of the tree can dislodge it. Measured in THIS repository on 2026-08-26: the marker was written 2026-08-14, carries all seven stages `pending`, and every one of those stages' outputs is already on disk - AGENTS.md and CLAUDE.md, prd.md, trd.md, tsd.md, personas.md, 218 epics and 109 retros. `status.py hint` answers `/sdlc-studio init guided (guided onboarding in progress - next stage: agents)` and suppresses the real next step entirely. Population: any project holding an onboarding marker with a pending stage, which includes every project where someone started `init guided` and stopped.

## Steps to Reproduce

1. Run `init guided` in an established project and abandon it after the first prompt, leaving `.local/onboarding.json` with pending stages. 2. Run `/sdlc-studio hint` or `status`. 3. The headline is `init guided`, whatever the project contains. Measured here with 218 epics and a complete PRD/TRD/TSD/personas set on disk. The marker had sat for 12 days across dozens of sprint closes and nothing reported it.

## Proposed Fix

Make the onboarding hint FALSIFIABLE by the tree. `first_incomplete` should skip a stage whose artefact already exists - init already knows each stage's output, since it is what the stage writes - so a marker can only point at work genuinely outstanding. Two smaller guards are worth having beside it: report the marker's AGE at the hint so an abandoned one is visible rather than silent, and have the onboarding hint state what it is superseding so an operator can see the ladder it displaced. A hint nothing can contradict is not a hint.

## Acceptance Criteria

- [x] **AC1** Given an onboarding marker whose pending stage has its output already on disk, when the hint is computed, then that stage is not offered and the ordinary pipeline ladder answers - a marker must be falsifiable by the tree, and today no state of the tree can dislodge it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OnboardingHintFalsifiabilityTests::test_a_stage_whose_output_exists_does_not_hold_the_hint
  - **Verified:** yes (2026-08-26)
- [x] **AC2** Given an onboarding marker whose pending stage has NO output on disk, when the hint is computed, then it still points at `init guided` - the paired control, so making the marker falsifiable does not disable guided onboarding for the projects that are genuinely mid-way through it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OnboardingHintFalsifiabilityTests::test_a_genuinely_incomplete_stage_still_holds_the_hint
  - **Verified:** yes (2026-08-26)
- [x] **AC3** Given an onboarding marker every one of whose stages has its output on disk, when the hint is computed, then the marker is reported as SUPERSEDED by name rather than silently ignored - a stale file that is quietly skipped is one nobody ever cleans up
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OnboardingHintFalsifiabilityTests::test_a_fully_superseded_marker_is_named_not_silently_skipped
  - **Verified:** yes (2026-08-26)
- [x] **AC4** Given a fully superseded marker, when `/sdlc-studio hint` is run - the SHIPPED command, not the function behind it - then it exits 0, prints the pipeline ladder's own answer, and names the stale marker beside it. The first cut returned a dict with no `reason` key and `cmd_hint` raised a KeyError on exactly this input, turning the orientation command into a traceback and losing every advisory with it - a wrong answer replaced by no answer at all
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OnboardingHintFalsifiabilityTests::test_the_shipped_hint_command_survives_a_superseded_marker
  - **Verified:** yes (2026-08-27)
- [x] **AC5** Given a stage whose output is only PARTLY present - AGENTS.md without CLAUDE.md, or epics without stories - when the hint is computed, then that stage still holds it. Making the marker falsifiable opened the opposite failure: a stage declared done on half its output is one the operator is never walked through
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OnboardingHintFalsifiabilityTests::test_a_partly_complete_stage_still_holds_the_hint
  - **Verified:** yes (2026-08-27)

## Impact

`status` and `hint` are the orientation commands - AGENTS.md names `/sdlc-studio status` as step 2 of what every session runs, including after a context reset. A fresh agent in an established project is therefore told, as its first instruction, to go and re-onboard a project that has 218 epics. It is the worst possible place for an unfalsifiable claim, because it is read before the reader knows enough to doubt it.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `init.py`, drop the `stage_output_exists` check from `first_incomplete`, deciding from the marker's own `status` field alone | Given an onboarding marker whose pending stage has its output already on disk, when the hint is computed, then that stage is not offered and the ordinary pipeline ladder answers - a marker must be falsifiable by the tree, and today no state of the tree can dislodge it |
| AC2 | in `init.py`, return True from `stage_output_exists` for every stage, so a genuinely incomplete one stops holding the hint | Given an onboarding marker whose pending stage has NO output on disk, when the hint is computed, then it still points at `init guided` - the paired control, so making the marker falsifiable does not disable guided onboarding for the projects that are genuinely mid-way through it |
| AC3 | in `init.py`, delete the body of `superseded_stages` and return an empty list, so a stale marker is stepped over without a word | Given an onboarding marker every one of whose stages has its output on disk, when the hint is computed, then the marker is reported as SUPERSEDED by name rather than silently ignored - a stale file that is quietly skipped is one nobody ever cleans up |
| AC4 | in `status.py`, return the supersession note from `_onboarding_hint` as a dict carrying no `reason` key, instead of leaving the ladder to answer | Given a fully superseded marker, when `/sdlc-studio hint` is run - the SHIPPED command, not the function behind it - then it exits 0, prints the pipeline ladder's own answer, and names the stale marker beside it. The first cut returned a dict with no `reason` key and `cmd_hint` raised a KeyError on exactly this input, turning the orientation command into a traceback and losing every advisory with it - a wrong answer replaced by no answer at all |
| AC5 | in `init.py`, replace the all-files test for agents with `AGENTS.md` alone, and the epics-and-stories test for decompose with epics alone | Given a stage whose output is only PARTLY present - AGENTS.md without CLAUDE.md, or epics without stories - when the hint is computed, then that stage still holds it. Making the marker falsifiable opened the opposite failure: a stage declared done on half its output is one the operator is never walked through |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
