# US0587: An artefact changed in the run diff with no tool provenance is reported by name at the close

> **Status:** Draft
> **Delivers:** CR0515
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0196
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: an artefact changed with no tool provenance is named at the close

- **Given** a run in which one artefact was edited by hand and another through `transition.py`
- **When** the close composes its report
- **Then** it names the hand-edited artefact and not the other, derived from the run diff against the ledger rather than asked - because an agent that hand-rolls is exactly the one that would answer that it used the tools
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ToolUseTests::test_a_hand_edited_artefact_is_named

### AC2: the comparison is against the run's own diff

- **Given** artefacts changed before the run opened
- **When** the close composes its report
- **Then** they are not named, so the check reports this run's hand-work rather than the repository's history
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ToolUseTests::test_only_this_runs_changes_are_judged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
