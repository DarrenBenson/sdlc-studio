# BG0615: an abandoned guided-onboarding marker outranks the whole hint ladder forever, so an established project is told to go and onboard itself

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Depends on:** BG0621
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py
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

- [ ] **AC1** Given an onboarding marker whose pending stage has its output already on disk, when the hint is computed, then that stage is not offered and the ordinary pipeline ladder answers - a marker must be falsifiable by the tree, and today no state of the tree can dislodge it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OnboardingHintTests::test_a_stage_whose_output_exists_does_not_hold_the_hint
- [ ] **AC2** Given an onboarding marker whose pending stage has NO output on disk, when the hint is computed, then it still points at `init guided` - the paired control, so making the marker falsifiable does not disable guided onboarding for the projects that are genuinely mid-way through it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OnboardingHintTests::test_a_genuinely_incomplete_stage_still_holds_the_hint
- [ ] **AC3** Given an onboarding marker every one of whose stages has its output on disk, when the hint is computed, then the marker is reported as SUPERSEDED by name rather than silently ignored - a stale file that is quietly skipped is one nobody ever cleans up
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OnboardingHintTests::test_a_fully_superseded_marker_is_named_not_silently_skipped

## Impact

`status` and `hint` are the orientation commands - AGENTS.md names `/sdlc-studio status` as step 2 of what every session runs, including after a context reset. A fresh agent in an established project is therefore told, as its first instruction, to go and re-onboard a project that has 218 epics. It is the worst possible place for an unfalsifiable claim, because it is read before the reader knows enough to doubt it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
