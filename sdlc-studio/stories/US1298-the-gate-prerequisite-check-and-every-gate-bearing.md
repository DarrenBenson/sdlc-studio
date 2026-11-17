# US1298: The gate prerequisite check and every gate-bearing command exit non-zero when PyYAML is absent

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0731
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0368
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The gate prerequisite check and every gate-bearing command exit non-zero when PyYAML is absent
**So that** CR0731 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The gate refuses before any lane when PyYAML is absent

- **Given** a project with a `.config.yaml` that switches a gate on, and an interpreter that cannot import `yaml`
- **When** `gate.py` is run at the commit boundary and again at the push boundary
- **Then** each run exits non-zero from its prerequisite check before any lane starts, naming PyYAML and the command that installs it. Fails on: a gate that prints one warning and runs its lanes on the shipped defaults
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RequiredPyYamlTests::test_the_gate_refuses_before_any_lane_without_pyyaml

### AC2: The refusal does not depend on a project config being present

- **Given** a project with no `.config.yaml`, and the same missing import
- **When** `gate.py` is run
- **Then** it exits non-zero with the same refusal. Fails on: a requirement enforced only when a config file exists, so that PyYAML is still optional in practice
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RequiredPyYamlTests::test_the_gate_refuses_without_pyyaml_even_with_no_project_config

### AC3: The gate runs its lanes where PyYAML imports

- **Given** the same project where `yaml` imports
- **When** `gate.py` is run
- **Then** the prerequisite check passes silently, the lanes run, and the exit code is the lanes' own. Fails on: a prerequisite check that refuses every machine, or one that prints on a pass
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RequiredPyYamlTests::test_the_gate_runs_its_lanes_when_pyyaml_imports

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
