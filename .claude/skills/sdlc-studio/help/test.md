# /sdlc-studio test - Run Tests with Traceability

## Quick Reference

```
/sdlc-studio test                       # Run all tests
/sdlc-studio test --epic EP0001         # Run tests for epic
/sdlc-studio test --story US0001        # Run tests for story
/sdlc-studio test --spec TSP0001        # Run tests for spec
/sdlc-studio test --type unit           # Run only unit tests
/sdlc-studio test --verbose             # Detailed output
```

## Prerequisites

- Tests must exist in project
- For filtering by story/epic: Test specs must exist in `sdlc-studio/testing/specs/`
- Run `/sdlc-studio test-spec` first to establish traceability

## Actions

### (default)

Run tests with optional filtering and story traceability.

**What happens:**
1. Detects test framework
2. If filtered, builds traceability map from test specs
3. Runs matching tests
4. Parses results
5. Maps results to stories
6. Reports coverage by story
7. Updates story status (Review → Done) if tests pass

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--epic EP0001` | Filter by epic | all |
| `--story US0001` | Filter by story | all |
| `--spec TSP0001` | Filter by test spec | all |
| `--type unit` | Filter by test type (unit, integration, api, e2e) | all |
| `--verbose` | Show detailed test output | false |

## Framework Detection

| File | Framework | Command |
|------|-----------|---------|
| `pyproject.toml` | pytest | `pytest -v` |
| `package.json` + vitest | Vitest | `npx vitest run` |
| `package.json` | Jest | `npx jest` |
| `go.mod` | Go testing | `go test -v` |
| `Cargo.toml` | Rust | `cargo test` |

## Output

**Console report:**
```
## Test Results

### Summary
| Metric | Value |
|--------|-------|
| Total | 45 |
| Passed | 42 |
| Failed | 2 |
| Skipped | 1 |

### By Story
| Story | Tests | Passed | Failed |
|-------|-------|--------|--------|
| US0001 | 12 | 12 | 0 |
| US0002 | 8 | 6 | 2 |

### Failed Tests
1. test_user_login_invalid_password
   - Story: US0002
   - Error: AssertionError: Expected 401, got 500
```

**Status update:** Story → "Done" (if was Review and all tests pass)

## Examples

```
# Run all tests
/sdlc-studio test

# Run tests for specific epic
/sdlc-studio test --epic EP0001

# Run tests for specific story
/sdlc-studio test --story US0003

# Run tests for specific test spec
/sdlc-studio test --spec TSP0002

# Run only unit tests
/sdlc-studio test --type unit

# Run only integration tests
/sdlc-studio test --type integration

# Run e2e tests with verbose output
/sdlc-studio test --type e2e --verbose

# Combine filters
/sdlc-studio test --epic EP0001 --type unit
```

## Traceability

Tests are linked to stories through test specifications:
1. Test specs (`TSP*.md`) reference stories in their traceability section
2. Test cases within specs have unique IDs (TC0001, TC0002)
3. Running with `--story` filter uses this mapping to select tests

## Status Flow

```
Review  ──[test passes]──▶  Done
```

A story's status automatically updates to Done when:
- Story was in Review status
- All associated tests pass

## Test Type Mapping

| Type | Description | Typical Location |
|------|-------------|------------------|
| unit | Isolated function tests | `tests/unit/` |
| integration | Component interaction tests | `tests/integration/` |
| api | API endpoint tests | `tests/api/` |
| e2e | End-to-end user flows | `tests/e2e/` |

## Next Steps

After tests pass:
- Story status automatically updated to Done
- Run `/sdlc-studio status` to see overall progress

If tests fail:
```
/sdlc-studio code review --story US0001  # Re-review after fixes
/sdlc-studio test --story US0001         # Re-run tests
```

## See Also

- `/sdlc-studio code help` - Implementation and review commands
- `/sdlc-studio test-spec help` - Generate test specifications
- `/sdlc-studio test-automation help` - Generate test code
- `reference-code.md` - Detailed test workflows
