# US0495: A full-suite run happens only at a boundary - push, release and sprint close - and the policy is stated where an operator reads it

> **Status:** Ready
> **Delivers:** CR0451
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/../help/gate.md
> **Epic:** EP0177
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator deciding when the expensive answer is worth having
**I want** full-suite runs confined to push, release and sprint close
**So that** the whole suite runs when a wrong answer is expensive, and not on every keystroke-sized commit

## Acceptance Criteria

### AC1: a per-commit run is selective and a boundary run is full

- **Given** the same tree at a commit and at a push
- **When** the gate runs at each
- **Then** the commit runs the selected set and the push runs everything, and each says which mode it used
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::BoundaryPolicyTests::test_commit_is_selective_and_boundary_is_full

### AC2: the policy is documented where an operator reads it

- **Given** help/gate.md
- **When** it is read
- **Then** it states which moments run the full suite and which run a selection, so the behaviour is discoverable without reading the hook
- **Verify:** pytest tools/tests/test_help_coverage.py::GatePolicyDocsTests::test_the_boundary_policy_is_documented

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the operator's two policy rules |
