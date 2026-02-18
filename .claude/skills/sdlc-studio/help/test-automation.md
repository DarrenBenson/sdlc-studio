<!--
Load: On /sdlc-studio test-automation or /sdlc-studio test-automation help
Dependencies: SKILL.md (always loaded first)
Related: reference-test-automation.md (deep workflow), reference-test-best-practices.md, reference-test-e2e-guidelines.md
-->

# /sdlc-studio test-automation

> **Source of truth:** `reference-test-automation.md` - Detailed workflow steps

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

## Coverage Targets

| Level | Target |
|-------|--------|
| Unit | 90% line coverage |
| Integration | 85% line coverage |
| E2E | 100% feature coverage |

**Why 90%?** AI-assisted development requires higher quality gates. This target has been proven achievable.

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

All frameworks use a unified `tests/` directory at project root with consistent naming:

| Language | Pattern | Example Path |
|----------|---------|--------------|
| Python | `test_*.py` | `tests/unit/backend/test_auth.py` |
| TypeScript | `*.test.ts` | `tests/unit/frontend/auth.test.ts` |
| E2E (any) | `*.spec.ts` | `tests/e2e/dashboard.spec.ts` |
| Go | `*_test.go` | `tests/unit/backend/auth_test.go` |

## Output Structure

Tests are organised in a unified `tests/` directory at project root:

```
tests/
  unit/
    backend/
      test_authentication.py
      test_validation.py
    frontend/
      auth.test.ts
      validation.test.ts
  integration/
    test_api_database.py
  api/
    test_endpoints.py
  e2e/
    dashboard.spec.ts
    login.spec.ts
  contracts/
    test_frontend_expects.py
  fixtures/
    users.json
    servers.json
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

> **Source of truth:** `reference-test-best-practices.md` - detailed patterns for edge case coverage and common pitfalls.

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

## Contract Test Pattern

**Critical:** E2E tests with mocked APIs don't catch backend bugs. Pair them with contract tests.

For every field the frontend consumes, write a backend test:

```python
# Python
def test_response_includes_uptime(client):
    response = client.get('/api/servers/test')
    assert 'uptime_seconds' in response.json()['metrics']
```

```typescript
// TypeScript
it('includes uptime_seconds', async () => {
  const response = await request(app).get('/api/servers/test');
  expect(response.body.metrics).toHaveProperty('uptime_seconds');
});
```

```go
// Go
func TestResponseIncludesUptime(t *testing.T) {
    resp := httptest.NewRecorder()
    router.ServeHTTP(resp, httptest.NewRequest("GET", "/api/servers/test", nil))
    var result ServerResponse
    json.Unmarshal(resp.Body.Bytes(), &result)
    if result.Metrics.UptimeSeconds == 0 {
        t.Error("uptime_seconds missing")
    }
}
```

## Language-Agnostic Runner Commands

| Language | Run Tests | With Coverage |
|----------|-----------|---------------|
| Python (pytest-cov) | `pytest` | `pytest --cov --cov-report=term-missing` |
| Python (coverage.py) | `pytest` | `coverage run -m pytest && coverage report` |
| TypeScript (vitest) | `npm test` | `npm run test:coverage` |
| TypeScript (jest) | `npm test` | `npm test -- --coverage` |
| Go | `go test ./...` | `go test -cover ./...` |

**Note:** Check project's `pyproject.toml` for which coverage tool is configured. If `[tool.coverage.run]` exists, use coverage.py directly.

## See Also

**REQUIRED for this workflow:**
- `reference-test-automation.md` - Test automation workflow details
- `reference-test-best-practices.md` - Test writing guidelines and pitfalls
- `reference-test-validation.md` - Validation steps and post-generation checklist

**Recommended:**
- `/sdlc-studio test-spec help` - Test specifications (upstream)

**Optional (deep dives):**
- `reference-test-e2e-guidelines.md` - E2E patterns and guidelines
- `reference-outputs.md` - Output formats reference
