# US0908: The skill's scripts run on the Python 3.10 it declares

> **Status:** In Progress
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, tools/tests/test_test_noise.py, .github/workflows/lint.yml, tools/tests/test_lean_python_floor.py
> **Epic:** EP0262
> **Points:** 2
> **Persona:** Jonah Reyes

## User Story

**As a** team lead adopting the skill on the team's existing Python 3.10 toolchain
**I want** the close and the sprint report to run on the Python version the skill says it supports
**So that** the team adopts the skill without upgrading every machine first, and the declared floor stays true without adding a commit lane

## Acceptance Criteria

- **AC1:** Given a Python 3.10 interpreter (`python3.10` on PATH or `uv run --python 3.10`), when every tracked .py file is compiled with it, then all compile, `sprint_report.py` and tools/tests/`test_test_noise.py` included; the check runs the real 3.10 interpreter, because `ast.parse(..., feature_version=(3, 10))` under a newer Python accepts `sprint_report.py`:425 today, and with no 3.10 interpreter it skips naming why, except under CI where it fails
  - **Verify:** pytest tools/tests/test_lean_python_floor.py::PythonFloorTests::test_every_tracked_file_compiles_under_3_10
- **AC2:** Given Python 3.10, when each shipped script under `scripts/` runs `--help`, then each exits 0 - `sprint_report.py`, whose import today fails, included
  - **Verify:** pytest tools/tests/test_lean_python_floor.py::PythonFloorTests::test_every_shipped_script_starts_under_3_10
- **AC3:** Given .github/workflows/lint.yml, then CI runs that compile check once under Python 3.10 on each push as a workflow step, not a pre-commit lane; its place is earned by measured yield (two consumer-breaking parse failures) and it replaces the floor-checker lane US0811 proposed
  - **Verify:** pytest tools/tests/test_lean_python_floor.py::PythonFloorTests::test_ci_runs_the_floor_check_once_under_3_10

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
