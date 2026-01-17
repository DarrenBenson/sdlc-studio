# /sdlc-studio test-automation

Generates executable test code from test specifications. Supports multiple languages and frameworks with automatic detection.

## Usage

```bash
# Generate all pending tests
/sdlc-studio test-automation

# Generate for specific spec
/sdlc-studio test-automation --spec TSP0001

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

1. Parse TSP file and extract test cases
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
6. Update TSP file with "Automated: Yes" and file paths

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

### 1. Wrong Enum Values
```python
# WRONG: Assumed from spec description
{"phase": "greeting"}

# RIGHT: Actual enum value from implementation
{"phase": "identification"}
```

### 2. MagicMock Attribute Access
```python
# WRONG: Causes TypeError when comparing
state.field = MagicMock(value="x")  # field.confidence is MagicMock

# RIGHT: Set attributes explicitly
mock = MagicMock()
mock.value = "x"
mock.confidence = 0.8  # Actual float
```

### 3. Singleton Mocking (Globals)
```python
# WRONG: Doesn't work if global already cached
with patch('module.get_engine'):
    ...

# RIGHT: Patch the global directly
module._engine = mock_engine
```

### 4. Factory Function Mocking (Dependency Injection)
```python
# WRONG: Patching the class when route uses factory
with patch('api.routes.jobs.JobService') as Mock:
    ...  # Route calls get_job_service(), not JobService()!

# RIGHT: Patch the factory function
with patch('api.routes.jobs.get_job_service') as mock_get:
    mock_service = MagicMock()
    mock_service.get_job = AsyncMock(return_value=job)
    mock_get.return_value = mock_service
```

### 5. API Status Code Assumptions
```python
# WRONG: Assumed REST conventions
assert response.status_code == 201  # POST should return 201?

# RIGHT: Check actual route handler - FastAPI defaults to 200
assert response.status_code == 200
```

### 6. Outdated Schema Fields
```python
# WRONG: Used old V1 schema fields
{"name": "Test", "core_identity": {...}}

# RIGHT: Check current REQUIRED_TOP_LEVEL in validation.py
{"schema_version": "2.3.0", "identity_and_background": {...}}
```

## Generated Test Structure

Each generated test includes:

- **Docstring** with TC ID and story reference
- **Given/When/Then** comments from spec
- **Fixtures** extracted from spec data
- **Assertions** based on expected outcomes

## Example Output (pytest)

```python
class TestAuthentication:
    """TSP0001: Authentication Tests"""

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

- Test specs must exist in `sdlc-studio/testing/specs/`
- Run `/sdlc-studio test-spec` first if specs don't exist

## Options

| Option | Description |
|--------|-------------|
| `--spec TSP0001` | Generate for specific spec only |
| `--type unit` | Only generate unit tests |
| `--type integration` | Only generate integration tests |
| `--type api` | Only generate API tests |
| `--type e2e` | Only generate E2E tests |
| `--framework pytest` | Override framework detection |
| `--dry-run` | Show what would be generated |

## Post-Generation (REQUIRED)

After generating tests:

1. **Run tests immediately** - Execute generated tests before marking complete
2. Fix any failures:
   - Mock patch paths (factory functions vs classes)
   - API status codes (verify against actual handlers)
   - Schema field mismatches
3. Add any complex setup not captured in specs
4. Only update specs after tests pass: `/sdlc-studio test-spec update`

**Tests must pass before automation is considered complete.**

## See Also

- `/sdlc-studio test-spec` - Generate test specifications first
- `/sdlc-studio status` - Check automation coverage
- `/sdlc-studio migrate` - Migrate from old format
