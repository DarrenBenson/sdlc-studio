<!--
Load: On /sdlc-studio test-automation or /sdlc-studio test-automation help
Dependencies: SKILL.md (always loaded first)
Related: reference-testing.md (deep workflow), reference-test-best-practices.md, reference-test-e2e-guidelines.md
-->

# /sdlc-studio test-automation

Generates executable test code from test specifications. Supports multiple languages and frameworks with automatic detection.

## Usage

```bash
# Generate all pending tests
/sdlc-studio test-automation

# Generate for specific spec
/sdlc-studio test-automation --spec TS0001

# Filter by test type
/sdlc-studio test-automation --type unit
/sdlc-studio test-automation --type integration
/sdlc-studio test-automation --type api
/sdlc-studio test-automation --type e2e

# Override framework detection
/sdlc-studio test-automation --framework pytest
/sdlc-studio test-automation --framework jest
/sdlc-studio test-automation --framework vitest
/sdlc-studio test-automation --framework go
```

## Language Detection

The skill automatically detects the project language:

| File Found | Language | Default Framework |
|------------|----------|-------------------|
| `pyproject.toml`, `setup.py` | Python | pytest |
| `package.json` + vitest | TypeScript | Vitest |
| `package.json` | TypeScript | Jest |
| `go.mod` | Go | testing |
| `Cargo.toml` | Rust | cargo test |

## Framework Conventions

| Framework | Test Location | Naming Pattern |
|-----------|---------------|----------------|
| pytest | `tests/` | `test_*.py` |
| Jest | `__tests__/` | `*.test.ts` |
| Vitest | `src/__tests__/` | `*.test.ts` |
| Go | same package | `*_test.go` |

## Output Structure

Tests are organised by type:

```
tests/
  unit/
    test_authentication.py
    test_validation.py
  integration/
    test_api_auth.py
  e2e/
    test_login_flow.py
```

## Generation Process

1. Parse TS file and extract test cases
2. Detect language and framework
3. **Implementation Discovery (CRITICAL for E2E/Integration)**
   - Examine services being tested for enum definitions
   - Extract dataclass/model structures and their attributes
   - Identify singleton patterns for correct mocking strategy
   - Check API request schemas for required fields
4. Group cases by type (unit, integration, api, e2e)
5. For each group:
   - Select appropriate template
   - Generate mock helper functions from discovered dataclasses
   - Extract fixtures from spec
   - Generate test functions with correct enum values
   - Write to correct location
6. Update TS file with "Automated: Yes" and file paths

## Pre-Generation Checklist

Before generating E2E or integration tests, verify:

| Check | Why | How to Find |
|-------|-----|-------------|
| Enum values | Tests fail with invalid enum values | `grep "class.*Enum" api/services/*.py` |
| Dataclass fields | Mock attributes must match | `grep "@dataclass" api/services/*.py` |
| Singleton patterns | Mocking getter vs global | Look for `_var = None` patterns |
| Factory functions | Patch factory, not class | Look for `def get_*():` and `Depends(get_*)` |
| API status codes | Don't assume REST conventions | Read route handler return statements |
| Schema version | Validation uses current schema | Check `REQUIRED_TOP_LEVEL` in validation.py |
| Required request fields | API calls fail with missing fields | Check route handler + Pydantic models |

## Common Pitfalls

Brief summary - see `reference-test-best-practices.md` and `reference-test-e2e-guidelines.md` for detailed patterns and examples.

- **Wrong enum values** - Extract from implementation, don't assume from spec
- **MagicMock attribute access** - Set attributes explicitly (`.confidence = 0.8`), not as MagicMock
- **Singleton mocking** - Patch the global directly, not the getter function
- **Factory function mocking** - Patch `get_*()` factory, not the class being returned
- **API status codes** - FastAPI defaults to 200, check actual route handler
- **Outdated schema fields** - Verify current schema version before writing validation tests

## Generated Test Structure

Each generated test includes:

- **Docstring** with TC ID and story reference
- **Given/When/Then** comments from spec
- **Fixtures** extracted from spec data
- **Assertions** based on expected outcomes

## Example Output (pytest)

```python
class TestAuthentication:
    """TS0001: Authentication Tests"""

    def test_valid_login_succeeds(self, client, valid_user):
        """TC001: Valid login succeeds

        Story: US0001
        Priority: Critical
        """
        # Given: valid user credentials
        credentials = {"email": valid_user.email, "password": "secret"}

        # When: user attempts login
        response = client.post("/login", json=credentials)

        # Then: login succeeds with token
        assert response.status_code == 200
        assert "token" in response.json()
```

## Prerequisites

- Test specs must exist in `sdlc-studio/test-specs/`
- Run `/sdlc-studio test-spec` first if specs don't exist

## Options

| Option | Description |
|--------|-------------|
| `--spec TS0001` | Generate for specific spec only |
| `--type unit` | Only generate unit tests |
| `--type integration` | Only generate integration tests |
| `--type api` | Only generate API tests |
| `--type e2e` | Only generate E2E tests |
| `--framework pytest` | Override framework detection |

## Post-Generation (REQUIRED)

After generating tests:

1. **Run tests immediately** - Execute generated tests before marking complete
2. Fix any failures:
   - Mock patch paths (factory functions vs classes)
   - API status codes (verify against actual handlers)
   - Schema field mismatches
3. Add any complex setup not captured in specs
4. Only update specs after tests pass: `/sdlc-studio test-spec review`

**Tests must pass before automation is considered complete.**

## See Also

- `/sdlc-studio test-spec` - Generate test specifications first
- `/sdlc-studio status` - Check automation coverage
- `reference-test-best-practices.md` - Test writing guidelines, validation steps
- `reference-test-e2e-guidelines.md` - E2E mocking patterns, API contract tests
