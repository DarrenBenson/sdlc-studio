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
/sdlc-studio code refactor              # Guided refactoring
/sdlc-studio code refactor --type extract-method  # Specific refactoring
/sdlc-studio code refactor --story US0001  # Refactor story code
/sdlc-studio code review                # Design pattern review
/sdlc-studio code review --story US0001 # Review story implementation
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

### refactor

Guided refactoring with pattern selection.

**What happens:** Validates tests → Identifies candidates → Previews → Applies → Verifies tests pass.

**Types:** `extract-method`, `extract-variable`, `rename`, `inline`, `move`

**Flags:** `--type`, `--story`, `--file`, `--dry-run`

> **Full details:** See `reference-refactor.md` for workflows and `/sdlc-studio refactor help` for quick reference.

### review

Design pattern and quality review.

**What happens:** Loads AC → Explores code → Checks patterns → Generates report with file:line references.

**Focus areas:** `patterns`, `security`, `performance`, `testing`, `all` (default)

**Flags:** `--story`, `--file`, `--focus`, `--severity`

> **Full details:** See `reference-refactor.md#code-review-workflow` and `/sdlc-studio review help`.

### verify

Verify implementation against acceptance criteria.

**What happens:** Parses AC → Finds implementation evidence → Generates pass/fail report with file:line refs → Updates status to Review if all AC met.

**Output:** Table showing each AC with status and code evidence locations.

### check

Run linters and best practice checks.

**What happens:** Detects language → Runs linter with auto-fix → Reports findings.

**Linters:** Python (ruff), TypeScript (eslint), Go (fmt + vet), Rust (clippy)

### test

Run tests with optional filtering and story traceability.

**What happens:** Detects framework → Runs tests → Maps results to stories → Updates status if pass.

**Filters:** `--epic`, `--story`, `--spec`, `--type` (unit/integration/api/e2e), `--verbose`

**Frameworks:** pytest, Vitest, Jest, Go testing (auto-detected)

## Output

| Command | Files | Status Update |
|---------|-------|---------------|
| `plan` | `sdlc-studio/plans/PL{NNNN}-{slug}.md` | Story → Planned |
| `implement` | Source + test files | Story → In Progress |
| `verify` | Console report only | Story → Review (if AC met) |
| `check` | Modified source (if auto-fix) | None |

## Examples

```
/sdlc-studio code plan --story US0003    # Plan specific story
/sdlc-studio code implement --tdd         # Implement with TDD
/sdlc-studio code verify --story US0001   # Verify specific story
/sdlc-studio code check                   # Run linters with auto-fix
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
Ready → [plan] → Planned → [implement] → In Progress → [verify] → Review → [check] → Done
```

## Next Steps

After each command: `plan` → `implement` → `test` → `verify` → `check`

## See Also

**REQUIRED for this workflow:**
- `reference-code.md` - Code workflow details
- `reference-decisions.md#story-ready` - Ready status criteria
- `reference-refactor.md` - Refactoring and review workflows

**Recommended:**
- `/sdlc-studio story help` - User Stories (upstream)
- `/sdlc-studio test-spec help` - Test specifications (parallel)
- `/sdlc-studio code refactor help` - Guided refactoring
- `/sdlc-studio code review help` - Code review

**Optional (deep dives):**
- `reference-test-best-practices.md` - Testing guidelines
- `reference-outputs.md` - Output formats reference
- `best-practices/{language}.md` - Language-specific guidelines
