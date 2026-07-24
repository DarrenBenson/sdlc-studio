# US0345: rename audit.py and audit_check.py, update call sites in gate and sprint

> **Status:** Draft
> **Delivers:** CR0254
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0116
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/audit.py, .claude/skills/sdlc-studio/scripts/audit_check.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: audit.py and audit_check.py are renamed and nothing imports the old names

- **Given** a tree where `audit.py` and `audit_check.py` have been renamed to `readiness.py` and `schema_check.py`
- **When** the shipped scripts directory is swept for the old module names
- **Then** neither `audit.py` nor `audit_check.py` exists, and no shipped file imports or invokes either name - a rename that leaves a caller behind is a rename that has not happened
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::RenameTests::test_no_shipped_file_references_the_old_module_names

### AC2: gate.py and sprint.py call the renamed modules

- **Given** gate.py's readiness lane and sprint.py's pre-flight, both of which imported `audit`
- **When** each is invoked
- **Then** it resolves `readiness` and `schema_check`, and the behaviour is byte-identical to the pre-rename output for the same input - a rename must change no verdict
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::RenameTests::test_gate_and_sprint_call_sites_resolve_and_behave_identically

### AC3: the user-facing `audit` command is untouched

- **Given** the adversarial `audit` command RFC0033 frees the verb for
- **When** `audit --profile repo` is run
- **Then** it still resolves and runs - this rename is internal only, and the public surface must not move
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::RenameTests::test_the_public_audit_command_is_unchanged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
