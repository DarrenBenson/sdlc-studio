# US0026: complexity computation (cognitive + cyclomatic)

> **Status:** Done
> **Epic:** [EP0008: Tooling & Scripts](../epics/EP0008-tooling-scripts.md)
> **Owner:** Autosprint (CR0028, RFC0009)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As a** planner
**I want** a deterministic per-function complexity signal
**So that** estimation, refactor-first and test risk can reason about the difficulty
of the code a change touches, not just the story shape (RFC0009 WS1).

## Acceptance Criteria

### AC1: Cognitive complexity matches the SonarSource spec

- **Given** functions with nesting, elif chains, else-nested-ifs, boolean alternation, nested ternaries, comprehension filters and match guards
- **When** `cognitive_complexity` runs
- **Then** the scores match hand-computed SonarSource values (elif flat, else nests, comprehension filter +1, nested ternary nests)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_complexity.py::CognitiveSpecEdgeTests
- **Verified:** yes (2026-06-20)

### AC2: Cyclomatic + base cognitive cases

- **Given** flat ifs, nesting, elif chains, ternaries and nested functions
- **When** the scorers run
- **Then** cyclomatic = 1 + decision points and nested defs are scored separately
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_complexity.py::CognitiveTests
- **Verified:** yes (2026-06-20)

### AC3: File analysis + lizard degradation

- **Given** a Python file, a syntax-error file, and a non-Python file with no lizard installed
- **When** `analyse_file` runs
- **Then** Python is scored, bad/unsupported inputs return [] (never raise)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_complexity.py::FileAndDegradationTests
- **Verified:** yes (2026-06-20)

### AC4: repo_map emits per-function complexity

- **Given** a Python source parsed by repo_map
- **When** `parse_python` runs
- **Then** each function symbol carries `cognitive` and `cyclomatic`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_map.py::ParserTests::test_python_function_symbols_carry_complexity
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/complexity.py`: `cognitive_complexity`/`cyclomatic_complexity`, `analyse_source`/
`analyse_file` (lizard soft-dep), `scan` CLI, `cognitive_high` config. `repo_map.parse_python`
attaches complexity to function symbols.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0028) | Decomposed from CR0028 / RFC0009 WS1; critic APPROVE after spec fixes |
