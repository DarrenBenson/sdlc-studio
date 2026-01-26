<!--
Load: On /sdlc-studio code or /sdlc-studio code help
Dependencies: SKILL.md (always loaded first)
Related: reference-code.md (deep workflow), reference-test-best-practices.md (TDD mode)
-->

# /sdlc-studio code - Implementation & Quality

## Quick Reference

```
/sdlc-studio code plan                  # Plan next incomplete story
/sdlc-studio code plan --story US0001   # Plan specific story
/sdlc-studio code plan --epic EP0001    # Plan next story in epic
/sdlc-studio code implement             # Implement next planned story
/sdlc-studio code implement --plan PL0001  # Implement specific plan
/sdlc-studio code implement --story US0001 # Implement by story
/sdlc-studio code implement --tdd       # Force TDD mode
/sdlc-studio code implement --no-docs   # Skip doc updates
/sdlc-studio code test                  # Run all tests
/sdlc-studio code test --story US0001   # Run tests for story
/sdlc-studio code test --type unit      # Run only unit tests
/sdlc-studio code verify                # Verify next In Progress story
/sdlc-studio code verify --story US0001 # Verify specific story
/sdlc-studio code check                 # Run linters with auto-fix
/sdlc-studio code check --no-fix        # Check only, no changes
```

## Prerequisites

- For `plan`: Stories must exist in `sdlc-studio/stories/`
- For `implement`: Plan must exist with Planned story
- For `verify`: Story must be In Progress status
- Run `/sdlc-studio story` first if no stories exist

## Actions

### plan

Create detailed implementation plan for a User Story.

**What happens:**
1. Selects next incomplete story (or specified story)
2. Parses acceptance criteria, technical notes, edge cases
3. Detects project language and framework
4. Loads relevant best practices
5. Explores codebase for patterns and context
6. Generates implementation plan using sequential thinking
7. Writes plan file and updates index
8. Updates story status to Planned

**Selection logic:**
- `--story US0001`: Use specified story
- `--epic EP0001`: Find next Draft/Ready story in epic
- (none): Find next Draft/Ready story globally

### implement

**CRITICAL: Complete ALL plan phases.** Do NOT pause mid-implementation to ask questions. Execute every phase from the plan (backend, frontend, integration, etc.) before marking complete. If unsure about a detail, make a reasonable choice and continue.

Execute implementation plan with TDD support and documentation updates.

**What happens:**
1. Selects plan (by ID, story, or next available)
2. Validates plan and story status
3. Checks for unresolved open questions (blocks if critical)
4. Determines approach (TDD/Test-After from plan or flags)
5. Updates status: Plan → In Progress, Story → In Progress
6. Executes ALL implementation phases from plan sequentially
7. Updates documentation (if --docs, default: true)
8. Runs final checks (code check, tests)
9. Validates ALL plan phases are complete
10. Completes plan: Plan → Complete

**Completion criteria:**
- Every implementation phase in the plan is executed
- All acceptance criteria have implementing code
- Tests pass (or are created for Test-After)
- Quality checks pass

**Selection logic:**
- `--plan PL0001`: Use specified plan
- `--story US0001`: Find plan linked to story
- (none): Find next plan for Planned story

**TDD Mode (--tdd):**
For each acceptance criterion:
1. Write failing test
2. Run test to verify failure
3. Implement code to pass
4. Run test to verify pass
5. Refactor if needed

**Flags:**
| Flag | Effect |
|------|--------|
| `--tdd` | Force TDD approach |
| `--no-tdd` | Force Test-After approach |
| `--docs` | Update documentation (default) |
| `--no-docs` | Skip documentation updates |

### verify

Verify implementation against acceptance criteria.

**What happens:**
1. Selects next In Progress story (or specified story)
2. Parses all acceptance criteria
3. Explores codebase for implementation evidence
4. Verifies each AC with file:line references
5. Checks edge cases are handled
6. Audits best practices compliance
7. Generates pass/fail report
8. Updates status to Review if all AC met

**Output format:**
```
## Code Verification: US0001 - {title}

### Acceptance Criteria
| AC | Status | Evidence |
|----|--------|----------|
| AC1 | PASSED | src/auth.ts:45-67 |
| AC2 | FAILED | Not found |

### Summary
- Passed: 5/6 criteria
- Recommendation: Address failed AC
```

### check

Run linters and best practice checks.

**What happens:**
1. Detects project language
2. Runs appropriate linter with auto-fix (unless `--no-fix`)
3. Checks for anti-patterns
4. Reports findings and fixes

**Language detection:**
| File | Language | Linter |
|------|----------|--------|
| `pyproject.toml` | Python | ruff |
| `package.json` | TypeScript | eslint |
| `go.mod` | Go | go fmt + go vet |
| `Cargo.toml` | Rust | cargo clippy |

**Output format:**
```
## Code Quality Check

### Linter Results
| Type | Count | Auto-fixed |
|------|-------|------------|
| Errors | 3 | 2 |
| Warnings | 7 | 5 |

### Remaining Issues
1. src/api.ts:45 - Unused variable
```

### test

Run tests with optional filtering and story traceability.

**What happens:**
1. Detects test framework
2. If filtered, builds traceability map from test specs
3. Runs matching tests
4. Parses results and maps to stories
5. Reports coverage by story
6. Updates story status (Review → Done) if tests pass

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--epic EP0001` | Filter by epic | all |
| `--story US0001` | Filter by story | all |
| `--spec TS0001` | Filter by test spec | all |
| `--type unit` | Filter by test type (unit, integration, api, e2e) | all |
| `--verbose` | Show detailed test output | false |

**Framework detection:**
| File | Framework | Command |
|------|-----------|---------|
| `pyproject.toml` | pytest | `pytest -v` |
| `package.json` + vitest | Vitest | `npx vitest run` |
| `package.json` | Jest | `npx jest` |
| `go.mod` | Go testing | `go test -v` |

**Output format:**
```
## Test Results

### Summary
| Metric | Value |
|--------|-------|
| Total | 45 |
| Passed | 42 |
| Failed | 2 |

### By Story
| Story | Tests | Passed | Failed |
|-------|-------|--------|--------|
| US0001 | 12 | 12 | 0 |
| US0002 | 8 | 6 | 2 |
```

## Output

### code plan

**Files:**
- `sdlc-studio/plans/PL{NNNN}-{slug}.md` - Implementation plan
- `sdlc-studio/plans/_index.md` - Plans registry

**Plan sections:**
- Overview
- Acceptance Criteria Summary
- Technical Context (language, framework, best practices)
- Implementation Steps (phased with tasks)
- Recommended Approach (TDD/Test-After/Hybrid)
- Documentation Updates Required
- Edge Cases
- Risks & Mitigations
- Dependencies
- Definition of Done Checklist

**Status update:** Story → "Planned"

### code implement

**Files:**
- Source code (as specified in plan)
- Test files (unit, integration as needed)
- Documentation updates (if --docs enabled)

**Console output:**
- Implementation summary
- Files created/modified count
- Tests added count
- AC implementation status
- Next steps

**Status update:** Plan → "Complete", Story → "In Progress"

### code verify

**Output:** Console report only (no files created)

**Status update:** Story → "Review" (if all AC passed)

### code check

**Output:** Console report only

**Files modified:** Source files (if auto-fix enabled)

## Examples

```
# Plan implementation for next story
/sdlc-studio code plan

# Plan specific story
/sdlc-studio code plan --story US0003

# Plan next story in an epic
/sdlc-studio code plan --epic EP0002

# Implement next planned story
/sdlc-studio code implement

# Implement specific plan
/sdlc-studio code implement --plan PL0001

# Implement by story
/sdlc-studio code implement --story US0003

# Implement with TDD
/sdlc-studio code implement --tdd

# Implement without documentation updates
/sdlc-studio code implement --no-docs

# Verify implementation
/sdlc-studio code verify

# Verify specific story
/sdlc-studio code verify --story US0001

# Run linters with auto-fix
/sdlc-studio code check

# Check without fixing
/sdlc-studio code check --no-fix
```

## TDD vs Test-After: Per-Story Choice

Choose **per story** whether to use TDD (test-first) or Test-After (code-first).

> **Decision tree:** `reference-decisions.md` → TDD vs Test-After Decision Tree

**Quick guide:**
- **Prefer TDD**: API stories, >5 edge cases, clear AC, complex business rules
- **Prefer Test-After**: Exploratory, UI-heavy, prototype, evolving AC

Both paths produce the same artifacts, just in different order.

## Status Flow

```
Draft/Ready  ──[code plan]──▶  Planned
Planned      ──[code implement]──▶  In Progress
In Progress  ──[test passes]──▶  In Progress
In Progress  ──[code verify]──▶  Review (if AC met)
Review       ──[code check]──▶  Done
```

## Next Steps

After plan created:
```
/sdlc-studio code implement        # Execute the plan
```

After implement completes:
```
/sdlc-studio code test --story US0001   # Run tests for story
```

After tests pass:
```
/sdlc-studio code verify           # Verify AC met
```

After code verify passes:
```
/sdlc-studio code check            # Run quality checks
```

After all checks pass:
```
Story status updated: Review → Done
```

## See Also

**REQUIRED for this workflow:**
- `reference-code.md` - Code workflow details
- `reference-decisions.md#story-ready` - Ready status criteria

**Recommended:**
- `/sdlc-studio story help` - User Stories (upstream)
- `/sdlc-studio test-spec help` - Test specifications (parallel)

**Optional (deep dives):**
- `reference-test-best-practices.md` - Testing guidelines
- `reference-outputs.md` - Output formats reference
