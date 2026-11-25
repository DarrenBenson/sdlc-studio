# BG1495: sprint plan warns a wave is not safely parallel when its units share no file, because the cluster joins them through a unit in a later wave

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/BG1495.md
> **Evidence:** EP0314 grooming, 2026-11-16: `sprint.py plan --worklist` over BG1487, BG1493, BG1494, US1170, US1171, US1172 and US1173
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T04:32:48Z

## Summary

`_render_clusters` warns that a wave is NOT safely parallel when two of its units are members of the same shared-file cluster. Clusters are built transitively, so units that share no file pairwise are joined through a third unit. Planning EP0314, wave 2 (US1170, US1171, US1172) shares no file pairwise: each shares a file only with US1173, which `Depends on:` already puts in wave 3. The plan still printed 'wave 2 is NOT safely parallel - US1170, US1171, US1172 touch README.md, docs/release-notes-v6.4.0.md' and advised declaring `Depends on:`, which the units already do. A groomer who follows the advice serialises a wave that is safe, and one who learns to ignore it misses a real collision. Related to BG1269 (one cluster hides a code collision); this is the wave warning's own false positive.

## Steps to Reproduce

Plan a worklist of three units A, B and C that each share one different file with a fourth unit D, where D declares `Depends on: A, B, C`. Run `python3 .claude/skills/sdlc-studio/scripts/sprint.py plan --worklist <file>`: wave 1 holds A, B and C, wave 2 holds D, and stderr warns that wave 1 is NOT safely parallel, naming files none of A, B and C share with each other.

## Proposed Fix

Judge a wave from the pairwise intersection of its own units' Affects, not from cluster membership: warn only when two units in the same wave declare a file in common, and name that pair and file.

## Acceptance Criteria

- [ ] **AC1** Given a wave whose units share no file pairwise, joined in one cluster only through a unit in a later wave, when `sprint plan` prints the waves, then it prints no NOT-safely-parallel warning for that wave. Fails on: the warning printed for EP0314's wave 2 shape.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::WaveClusterWarningTests::test_a_wave_joined_only_through_a_later_unit_is_not_warned
  - **Verified:** yes (2026-11-25)
- [ ] **AC2** Given a wave in which two units declare the same file, then the warning names those two units and that file. Fails on: a real same-wave collision left unwarned.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::WaveClusterWarningTests::test_a_same_wave_shared_file_is_warned_by_pair
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
| 2026-11-25 | orchestrator (delegate under D0545) | Affects widened for the SPB repair round: reference-sprint.md (about lines 305-307) still describes the wave warning's old rule, which this unit's change makes untrue |
