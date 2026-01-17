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
/sdlc-studio code review                # Review next In Progress story
/sdlc-studio code review --story US0001 # Review specific story
/sdlc-studio code check                 # Run linters with auto-fix
/sdlc-studio code check --no-fix        # Check only, no changes
```

## Prerequisites

- For `plan`: Stories must exist in `sdlc-studio/stories/`
- For `implement`: Plan must exist with Planned story
- For `review`: Story must be In Progress status
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

Execute implementation plan with TDD support and documentation updates.

**What happens:**
1. Selects plan (by ID, story, or next available)
2. Validates plan and story status
3. Checks for unresolved open questions
4. Determines approach (TDD/Test-After from plan or flags)
5. Updates status: Plan → In Progress, Story → In Progress
6. Executes implementation steps
7. Updates documentation (if --docs, default: true)
8. Runs final checks (code check, tests)
9. Completes plan: Plan → Complete

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

### review

Review implementation against acceptance criteria.

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
## Code Review: US0001 - {title}

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

### code review

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

# Review implementation
/sdlc-studio code review

# Review specific story
/sdlc-studio code review --story US0001

# Run linters with auto-fix
/sdlc-studio code check

# Check without fixing
/sdlc-studio code check --no-fix
```

## Status Flow

```
Draft/Ready  ──[code plan]──▶  Planned
Planned      ──[code implement]──▶  In Progress
In Progress  ──[code review]──▶  Review (if AC met)
Review       ──[test passes]──▶  Done
```

## Next Steps

After plan created:
```
/sdlc-studio code implement        # Execute the plan
```

After implement completes:
```
/sdlc-studio code review           # Verify AC met
```

After code review passes:
```
/sdlc-studio test --story US0001   # Run tests for story
```

After tests pass:
```
Story status automatically updated: Review → Done
```

## See Also

- `/sdlc-studio story help` - Generate stories (prerequisite)
- `/sdlc-studio test help` - Run tests with traceability
- `reference-code.md` - Detailed workflows
