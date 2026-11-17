# US1197: Sprint drive runs a wave's independent units in parallel and stops at a warning, a conflict or the wave end

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0672
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/drive.py, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_wave.py
> **Epic:** EP0326
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Sprint drive runs a wave's independent units in parallel and stops at a warning, a conflict or the wave end
**So that** CR0672 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Independent units build in parallel and a unit sharing a file waits

- **Given** a wave of three units, two with disjoint Affects and a third sharing a file with the first, and a stub harness that records when each build starts and ends
- **When** `sprint.py drive` is run
- **Then** the two disjoint units' builds overlap in time, the third starts only after the first has landed, and all three land on the root's branch. Fails on: builds run one after another, or two units that share a file built at once
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_wave.py::SprintDriveWaveTests::test_disjoint_units_build_together_and_a_shared_file_waits

### AC2: A warning from a step that exited 0 stops that unit

- **Given** a wave in which one unit's `lane accept` exits 0 and prints a WARNING line on stderr (BG1235's self-reviewed unit)
- **When** `sprint.py drive` is run
- **Then** drive runs no further step for that unit, exits non-zero and its decision record quotes the warning line and names the unit and the step; the wave's other unit is not left half landed. Fails on: a warning carried forward unread while the unit's paperwork is committed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_wave.py::SprintDriveWaveTests::test_a_warning_on_a_green_step_stops_the_unit

### AC3: A rebase conflict stops the wave and leaves the first landing standing

- **Given** a wave of two units whose staged changes conflict when the second is rebased onto the first's landing
- **When** `sprint.py drive` is run
- **Then** the first unit's landing stands, the root's branch is as that landing left it, the second unit's lane stays in its worktree, and the decision record names the conflicting files; drive retries nothing and forces nothing. Fails on: a conflict resolved or retried by the loop, or a root branch left mid-rebase
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_wave.py::SprintDriveWaveTests::test_a_rebase_conflict_stops_the_wave_and_keeps_the_first_landing

### AC4: Drive stops at the wave end, and the doctrine says when the model is woken

- **Given** a run of two waves whose first wave completes cleanly, and `reference-doctrine.md`
- **When** `sprint.py drive` is run, and the doctrine is read
- **Then** drive exits after the first wave with a decision record naming the wave end and each unit's state, having started no unit of the second wave; the doctrine names the same stops the record can carry (a refusal, a warning, a REJECT, a conflict, a wave end) as the only points the model is woken. Fails on: drive running on into the next wave, or a doctrine listing a stop the loop does not make
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_wave.py::SprintDriveWaveTests::test_the_wave_end_stops_drive_and_the_doctrine_names_the_stops

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
