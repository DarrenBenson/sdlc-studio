# US0943: `sprint plan` in a consuming project prints the skill's toolchain runbook

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_runbook_path.py, changelog.d/US0943.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0265
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer running the lean loop in her own project
**I want** the plan to print the toolchain runbook's steps, found beside the installed skill
**So that** the plan stops telling her the runbook is MISSING when the skill is installed under ~/.claude/skills and not inside her project

## Acceptance Criteria

- **AC1:** Given a fresh project with the skill installed outside it, when `sprint.py plan` runs, then the output carries the runbook's step headings, resolved from the skill root, and no `TOOLCHAIN RUNBOOK MISSING` line. Fails on: HEAD, where `render_runbook_pointer` joins `RUNBOOK_REL` to the project root (sprint.py:2446-2451; reproduced in a fresh `init` fixture)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_runbook_path.py::RunbookTests::test_consuming_project_finds_runbook
- **AC2:** Given a skill tree with no reference-sprint-toolchain.md, when the plan runs, then it still prints the MISSING line. Fails on: a fix that drops the absence report to make AC1 pass
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_runbook_path.py::RunbookTests::test_absent_runbook_still_reported

## Notes

Merged with the product seat's U9 (same defect, same test names). Resolve from `Path(__file__).resolve().parent.parent`, as `known_skill_root`-style readers elsewhere do; keep the printed path relative to the skill so the text is stable across installs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (N3) |
