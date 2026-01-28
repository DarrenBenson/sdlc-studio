<!--
Load: On /sdlc-studio tsd or /sdlc-studio tsd help
Dependencies: SKILL.md (always loaded first)
Related: reference-tsd.md (deep workflow), templates/core/tsd.md
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

## Coverage Troubleshooting

### Async Code Shows 0% Coverage

**Symptom:** Tests pass but async route handlers show 0% or very low coverage.

**Cause:** Coverage.py doesn't track code in greenlets by default. FastAPI/Starlette TestClient uses anyio which executes requests in greenlets.

**Fix:** Add concurrency configuration:

```toml
# pyproject.toml
[tool.coverage.run]
concurrency = ["greenlet", "thread"]
```

**Verification:**
```bash
# Before fix - low coverage
pytest --cov --cov-report=term | grep "routes/agents"
# agents.py    127    81    28%

# After fix - accurate coverage
pytest --cov --cov-report=term | grep "routes/agents"
# agents.py    127     6    93%
```

### Tests Pass But Coverage Still Low

**Symptom:** All tests pass but coverage for a module remains low despite having tests for it.

**Common causes:**

1. **Conditional assertions hiding failures**
   ```python
   # BAD - silently passes if no alerts created
   if service_alerts:
       assert service_alerts[0]["status"] == "success"

   # GOOD - fails explicitly
   assert len(service_alerts) > 0, "Service alerts should exist"
   assert service_alerts[0]["status"] == "success"
   ```

2. **Test helpers missing required data**
   - Helper creates partial data that doesn't trigger the code path
   - Example: Service alerts only evaluated when `metrics` present in heartbeat
   - Fix: Trace the full code path and include all required fields

3. **Feature dependencies not satisfied**
   - Feature A only runs when Feature B provides certain data
   - Fix: Read the source to understand triggering conditions

**Debugging steps:**
1. Add `print()` statements in the code being tested
2. Run test with `-s` flag to see output: `pytest -s test_file.py`
3. If no output appears, the code path isn't being reached
4. Trace backwards to find what condition isn't being met

**See also:** Test Anti-Patterns section in TSD template

## Next Steps

After creating Test Strategy:
```
/sdlc-studio test-spec            # Generate Test Specs from Stories
```

## See Also

**REQUIRED for this workflow:**
- `reference-tsd.md` - Test strategy workflow details

**Recommended:**
- `/sdlc-studio prd help` - Product requirements (context)
- `/sdlc-studio trd help` - Technical requirements (context)
- `/sdlc-studio test-spec help` - Test specifications (downstream)

**Optional (deep dives):**
- `reference-test-best-practices.md` - Testing guidelines
- `reference-outputs.md` - Output formats reference
