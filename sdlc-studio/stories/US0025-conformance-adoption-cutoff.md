# US0025: conformance adoption cutoff

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Autosprint (CR0027)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** operator turning the conformance gate on partway through a project
**I want** an adoption cutoff
**So that** legacy stories are reported, not permanently counted non-conformant - the
discipline applies forward, not retroactively (agent-crew: ~414 permanent findings).

## Acceptance Criteria

### AC1: Pre-cutoff stories are exempt

- **Given** `.config.yaml` `conformance.adopt_after: US0005` and a non-conformant US0001
- **When** `detect_conformance` runs
- **Then** US0001 is `exempt`, `conformant` true, `missing` empty, and not counted in `nonconformant`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::AdoptCutoffTests::test_pre_cutoff_story_is_exempt
- **Verified:** yes (2026-06-20)

### AC2: At/after the cutoff is still judged

- **Given** the same cutoff and a non-conformant US0010
- **When** the check runs
- **Then** US0010 is not exempt and is reported non-conformant (the cutoff is exclusive)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::AdoptCutoffTests::test_pre_cutoff_story_is_exempt
- **Verified:** yes (2026-06-20)

### AC3: cmd exits 0 when all failing units are exempt

- **Given** every non-conformant story is below the cutoff
- **When** `conformance check` runs
- **Then** it exits 0 (no judged-and-failing unit)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::AdoptCutoffTests::test_cmd_check_exits_zero_when_all_nonconformant_are_exempt
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/conformance.py`: read `conformance.adopt_after` via `sdlc_md.project_override`,
compare `sdlc_md.id_number(rid)` against the cutoff; exempt units carry `exempt: true`,
drop from `nonconformant`, and add an `exempt` summary key.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0027) | Decomposed from CR0027; critic APPROVE |
