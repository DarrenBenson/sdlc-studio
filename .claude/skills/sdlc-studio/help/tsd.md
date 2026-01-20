<!--
Load: On /sdlc-studio tsd or /sdlc-studio tsd help
Dependencies: SKILL.md (always loaded first)
Related: reference-testing.md (deep workflow), templates/tsd-template.md
-->

# /sdlc-studio tsd - Test Strategy Document

## Quick Reference

```
/sdlc-studio tsd                     # Interactive creation
/sdlc-studio tsd generate            # Infer from codebase
/sdlc-studio tsd review              # Review and update strategy
```

## What is a Test Strategy Document?

A project-level document defining:
- **What** to test (scope, levels, types)
- **How** to test (frameworks, automation approach)
- **When** to test (CI/CD integration, quality gates)
- **Who** tests (roles and responsibilities)

One test strategy per project. Test Specs then apply it to specific Stories.

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
6. Writes to `sdlc-studio/tsd.md`

### generate
Analyse codebase testing patterns and infer strategy.

**What happens:**
1. Searches for test files and configurations
2. Identifies frameworks in use (Jest, Playwright, pytest, etc.)
3. Analyses CI/CD pipeline for test stages
4. Documents current coverage and gaps
5. Writes strategy with [INFERRED] markers

### review
Review strategy against codebase and update.

**What happens:**
1. Loads existing strategy
2. Compares against current codebase
3. Updates tool versions, quality gates
4. Adds new test levels if needed

## Output

**File:** `sdlc-studio/tsd.md`

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
/sdlc-studio tsd

# Infer from existing test setup
/sdlc-studio tsd generate

# Review after framework change
/sdlc-studio tsd review
```

## Quality Gates Example

| Gate | Criteria | Blocking |
|------|----------|----------|
| Unit coverage | >=80% | Yes |
| Integration tests | 100% pass | Yes |
| E2E critical path | 100% pass | Yes |
| Performance | p95 < 500ms | Yes |

## Next Steps

After creating Test Strategy:
```
/sdlc-studio test-spec            # Generate Test Specs from Stories
```

## See Also

- `/sdlc-studio test-spec help` - Test Specs apply strategy to Stories
- `/sdlc-studio prd help` - PRD provides context for strategy
- `reference-testing.md` - Detailed test strategy workflows
