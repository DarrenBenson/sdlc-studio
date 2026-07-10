# US0113: Detect a disabled commit gate in gate and status

> **Status:** Done
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio new
> **Epic:** EP0026
> **Persona:** repo maintainer (dogfooding operator)
> **CR:** CR0202

## User Story

**As a** repo maintainer
**I want** gate and status to tell me when the tracked pre-commit hook is not enabled in my clone
**So that** the guard chain cannot silently degrade to nothing again (six unchecked commits reached main that way)

## Context

RV0007: hook enablement is opt-in per clone (`tools/enable-hooks.sh`) and nothing verified it -
this clone ran unhooked for 65 commits. The check must fire ONLY where it means something: a
tree that ships `.githooks/pre-commit` (this repo), never a consuming project (which has no
`.githooks`), and never a non-git directory.

## Acceptance Criteria

### AC1: gate warns when the hook exists but is not enabled

- **Given** a git work tree containing `.githooks/pre-commit` with `core.hooksPath` unset or not `.githooks`
- **When** `gate.py --root .` runs
- **Then** an advisory `hook-enabled` lane reports the gap and names the fix command (`bash tools/enable-hooks.sh`), without failing the gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py -k HookEnabled
- **Verified:** yes (2026-07-10)

### AC2: silent where it means nothing

- **Given** (a) a tree with the hook enabled, (b) a tree with no `.githooks/pre-commit`, (c) a non-git directory
- **When** the `hook-enabled` lane runs
- **Then** it reports clean (count 0) in all three cases - no standing advisory noise
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py -k HookEnabled
- **Verified:** yes (2026-07-10)

### AC3: status surfaces the same warning

- **Given** the AC1 state
- **When** `status.py pillars --root .` runs
- **Then** the dashboard includes a one-line hook warning naming the fix command
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py -k hook
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | sdlc | Created via `new` (deterministic) |
| 2026-07-10 | sprint (CR0202 decomposition) | ACs authored from CR0202; scoped to fire only where .githooks ships |
