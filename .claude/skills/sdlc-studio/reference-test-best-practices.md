# Test Generation Best Practices

Guidelines addressing common pitfalls discovered during test automation runs.

## Related References

| Document | Content |
|----------|---------|
| `reference-testing.md` | Main test workflows (tsd, test-spec, test-automation) |
| `reference-test-e2e-guidelines.md` | E2E mocking patterns, singleton/factory mocking, API contract tests |

---

## Pre-Generation Analysis Checklist

Before writing any test code, complete this checklist:

- [ ] **Verify import paths**: Grep for actual class/model names in implementation
  ```bash
  grep -r "class.*Model\|@dataclass" api/models.py api/services/
  ```

- [ ] **Check required fields**: Read model definitions for required vs optional fields
  ```bash
  grep -A 20 "class Job\|class StageResult" api/models.py
  ```

- [ ] **Verify field types**: Check if status fields are strings or enums
  ```python
  # Is it an enum?
  class StageStatus(str, Enum):
      COMPLETE = "complete"

  # Or just a string?
  status: str  # "pending", "running", "complete", "failed"
  ```

- [ ] **Read output templates**: Get exact section/header names from templates
  ```bash
  grep "^##\|^###" prompts/user-manual-template.md
  ```

- [ ] **Create verified import block FIRST**: Write and test imports before test code
  ```python
  # Test this imports correctly before proceeding
  from api.models import Job, StageResult, HeadshotStatus
  from api.services.headshot import HeadshotService, HeadshotResult
  ```

---

## Validation Steps

After generating each test file, validate before running the full suite:

1. **Syntax check** (catches encoding issues, unclosed strings):
   ```bash
   python -m py_compile tests/unit/test_new_feature.py
   ```

2. **Import check** (catches wrong class names, missing modules):
   ```bash
   python -c "from tests.unit.test_new_feature import *"
   ```

3. **Run single file with warnings as errors** (faster feedback than full suite):
   ```bash
   pytest tests/unit/test_new_feature.py -v -W error --tb=short
   ```

4. **Run full suite with warnings as errors**:
   ```bash
   pytest -W error
   ```

5. **Only proceed** when ALL tests pass with ZERO warnings.

---

## Warning Policy

**Warnings are errors.** Do not dismiss them as "benign" - they indicate real quality issues.

### Why Warnings Matter

- **Resource leaks**: Unclosed connections, file handles, async tasks
- **Deprecated APIs**: Code that will break in future library versions
- **Async lifecycle issues**: Event loops closing before cleanup, thread communication failures
- **Flaky tests**: Race conditions that occasionally fail in CI

### Common Warning Types and Fixes

| Warning | Root Cause | Fix |
|---------|------------|-----|
| `PytestUnhandledThreadExceptionWarning` | Thread/async cleanup failed | Ensure proper disposal in fixtures |
| `DeprecationWarning` | Using outdated API | Update to current API pattern |
| `RuntimeWarning: coroutine never awaited` | Missing await | Add await or ensure proper async handling |
| `ResourceWarning: unclosed file` | File not closed | Use context manager (`with open(...)`) |
| `Event loop is closed` (aiosqlite) | DB connections outlive event loop | Dispose engine before event loop closes |

### Async/Database Test Fixture Pattern

When testing async code with databases, use test-specific app configuration:

```python
@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Test client with clean async lifecycle."""
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def test_lifespan(app):
        """Test lifespan WITHOUT background schedulers."""
        await init_database()
        yield
        await dispose_engine()  # Clean disposal before event loop closes

    # Create test-specific app without background tasks
    test_app = create_app_without_scheduler(lifespan=test_lifespan)
    with TestClient(test_app) as test_client:
        yield test_client
```

**Key insight**: Background schedulers (APScheduler, Celery beat, etc.) create async tasks that may outlive the test. Create test-specific app configurations that skip background task initialisation.

### Running Tests

Always use warning flags:

```bash
# Strict mode - fail on any warning
pytest -W error

# Specific warning types (if library generates unavoidable warnings)
pytest -W error::pytest.PytestUnhandledThreadExceptionWarning

# Full suite verification
pytest -W error --tb=short -q
```

---

## Test Writing Guidelines

### Unicode and Encoding

When testing unicode handling functions:

```python
# BAD: Literal unicode can break Python parsing
text = "It's a "test" string"  # Smart quotes break the file!

# GOOD: Use escape sequences
text = "It\u2019s a \u201ctest\u201d string"
```

### Assertion Patterns

Prefer structural assertions over content matching:

```python
# BAD: Assumes exact section name
assert "Psychological Profile" in manual  # May be "Profile Foundation"

# GOOD: Check for structural elements that won't change
assert "## " in manual  # Has markdown headers
assert len(manual) > 100  # Has substantial content
assert name in manual  # Subject name appears
```

For behavioural tests, use broad phrase lists:

```python
# BAD: Too specific
assert "I maintain my boundaries" in response

# GOOD: Accept multiple valid phrasings
boundary_phrases = [
    "maintain", "boundaries", "privacy", "personal",
    "prefer not to", "cannot share"
]
assert any(phrase in response.lower() for phrase in boundary_phrases)
```

### Model Instantiation

Always verify required fields before creating test objects:

```python
# BAD: Missing required 'name' field
job = Job(id="test-1", slug="test")  # ValidationError!

# GOOD: Include all required fields
job = Job(
    id="test-1",
    name="Test Job",  # Required!
    slug="test",
    stages=[],
)
```

### Enum vs String

Check implementation before using status values:

```python
# If StageResult.status is a string (not enum):
stage = StageResult(stage=0, name="Stage 0", status="complete")

# If using an actual enum:
from api.models import StageStatus
stage = StageResult(stage=0, name="Stage 0", status=StageStatus.COMPLETE)
```

---

## Coverage Verification

After generating tests, verify coverage:

1. **Count tests vs spec TCs**:
   ```bash
   # Count test functions
   grep -c "def test_\|async def test_" tests/unit/test_feature.py

   # Count TCs in spec (can be fewer - multiple tests per TC is fine)
   grep -c "^### TC" sdlc-studio/test-specs/TS0004*.md
   ```

2. **Verify TC IDs in docstrings**:
   ```bash
   # Each test should reference its TC
   grep "TC0" tests/unit/test_feature.py
   ```

3. **Update automation summary**:
   - Edit `sdlc-studio/test-specs/_index.md`
   - Update Automated count and Coverage percentage
   - Change Status from "Draft" to "Complete"

---

## Test Anti-Patterns to Avoid

Common mistakes that cause test failures, false positives, or maintenance burden.

### 1. Over-Mocking (Mocking at Wrong Boundary)

**Bad:**
```python
# Mocks the HTTP client - test passes even if webhook code is broken
with patch("myapp.routes.httpx.AsyncClient") as mock_client:
    mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
```

**Good:**
```python
# Mock at network boundary using responses library
import responses

@responses.activate
def test_webhook_sends_correctly():
    responses.add(responses.POST, "https://hooks.slack.com/...", json={"ok": True})
    # Actual HTTP client code runs, only network is mocked
```

**Rule:** Mock at system boundaries (network, filesystem, time), not internal libraries.

### 2. Framework Testing

**Bad:**
```python
def test_cors_headers_present():
    # Tests FastAPI's CORS middleware, not your application
    assert "access-control-allow-origin" in response.headers
```

**Good:**
- One smoke test to verify CORS is configured correctly
- Focus tests on your business logic, not framework behaviour

### 3. Time-Dependent Tests Without Mocking

**Bad:**
```python
def test_server_offline_after_180_seconds():
    # Uses real time - flaky if system is slow
    server.last_seen = datetime.now() - timedelta(seconds=200)
    assert is_offline(server)
```

**Good:**
```python
from freezegun import freeze_time

@freeze_time("2026-01-20 12:00:00")
def test_server_offline_after_180_seconds():
    server.last_seen = datetime(2026, 1, 20, 11, 57, 0)  # 180s ago
    assert is_offline(server)
```

**Time mocking libraries:**
- Python: freezegun, time-machine
- TypeScript: Sinon.useFakeTimers(), jest.useFakeTimers()
- Go: clockwork

### 4. Tests That Always Pass

**Symptom:** Test mocks return exactly what the code expects.

**Example:**
```python
# This test will ALWAYS pass, even if implementation is broken
def test_calculate_total():
    with patch("myapp.calculate") as mock_calc:
        mock_calc.return_value = 100  # We dictate the answer
        result = get_order_total(items)
        assert result == 100  # Of course it equals what we told it to return!
```

**Check:** Would this test fail if the implementation was completely wrong?

**Rule:** Mocks should simulate external behaviour, not dictate internal expectations.

---

## E2E Tests and the API Mock Gap

### The Problem

E2E tests with mocked API data verify frontend rendering but do NOT catch backend bugs.

**Example scenario:**
- Frontend expects `latest_metrics.uptime_seconds`
- E2E test mocks API with `{ uptime_seconds: 86400 }` - test passes
- Backend Pydantic schema doesn't include `uptime_seconds` - BUG not caught
- Production frontend shows "--" because field is missing

### The Solution: API Contract Tests

For every field the frontend consumes, write a contract test that:

1. Creates real data via the API
2. Retrieves it via the endpoint being tested (no mocking)
3. Asserts the expected field exists with correct type/value

**Python example:**
```python
async def test_server_response_includes_uptime_seconds():
    """Contract test: Frontend expects uptime_seconds field."""
    # Create real server with heartbeat data
    await create_test_server_with_metrics()

    # Call actual API (no mocking!)
    response = await client.get("/api/v1/servers/test-server")

    # Assert contract field exists
    assert "uptime_seconds" in response.json()["latest_metrics"]
```

**TypeScript example:**
```typescript
it('should include uptime_seconds in server response', async () => {
  // Create real data
  await createTestServerWithMetrics();

  // Call actual API
  const response = await request(app).get('/api/v1/servers/test-server');

  // Assert contract
  expect(response.body.latest_metrics).toHaveProperty('uptime_seconds');
});
```

### Recommendation

Pair E2E tests (UI works with mocked data) with contract tests (backend returns expected fields). Neither alone is sufficient for full-stack coverage.
