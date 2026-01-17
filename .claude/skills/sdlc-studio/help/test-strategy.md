# /sdlc-studio test-strategy - Test Strategy

## Quick Reference

```
/sdlc-studio test-strategy          # Interactive creation
/sdlc-studio test-strategy generate # Infer from codebase
/sdlc-studio test-strategy update   # Update strategy
```

## What is a Test Strategy?

A project-level document defining:
- **What** to test (scope, levels, types)
- **How** to test (frameworks, automation approach)
- **When** to test (CI/CD integration, quality gates)
- **Who** tests (roles and responsibilities)

One test strategy per project. Test Plans then apply it to specific Epics.

## Prerequisites

- PRD should exist at `sdlc-studio/prd.md` (provides context)

## Actions

### create (default)
Guided conversation to define test strategy.

**What happens:**
1. Claude asks about testing objectives and priorities
2. Discusses test levels (unit, integration, E2E)
3. Asks about framework preferences
4. Documents automation approach
5. Defines quality gates for CI/CD
6. Writes to `sdlc-studio/testing/strategy.md`

### generate
Analyse codebase testing patterns and infer strategy.

**What happens:**
1. Searches for test files and configurations
2. Identifies frameworks in use (Jest, Playwright, pytest, etc.)
3. Analyses CI/CD pipeline for test stages
4. Documents current coverage and gaps
5. Writes strategy with [INFERRED] markers

### update
Update strategy based on changes.

**What happens:**
1. Loads existing strategy
2. Compares against current codebase
3. Updates tool versions, quality gates
4. Adds new test levels if needed

## Output

**File:** `sdlc-studio/testing/strategy.md`

**Key sections:**
- Overview & Objectives
- Test Scope (in/out)
- Test Levels (unit, integration, E2E, performance, security)
- Test Environments
- Test Data Strategy
- Automation Strategy
- CI/CD Integration & Quality Gates
- Defect Management
- Roles & Responsibilities
- Tools & Infrastructure

## Examples

```
# Interactive strategy creation
/sdlc-studio test-strategy

# Infer from existing test setup
/sdlc-studio test-strategy generate

# Update after framework change
/sdlc-studio test-strategy update
```

## Quality Gates Example

| Gate | Criteria | Blocking |
|------|----------|----------|
| Unit coverage | ≥80% | Yes |
| Integration tests | 100% pass | Yes |
| E2E critical path | 100% pass | Yes |
| Performance | p95 < 500ms | Yes |

## Next Steps

After creating Test Strategy:
```
/sdlc-studio test-plan            # Generate Test Plans for Epics
```

## See Also

- `/sdlc-studio test-plan help` - Test Plans apply strategy to Epics
- `/sdlc-studio prd help` - PRD provides context for strategy
