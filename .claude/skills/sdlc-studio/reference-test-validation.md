# Test Validation and Advanced Practices

Detailed validation workflows, contract testing, and advanced testing patterns.

## Related References {#test-validation-related-references}

| Document | Content |
|----------|---------|
| `reference-test-best-practices.md` | Core practices, checklists, warnings, coverage targets |
| `reference-tsd.md`, `reference-test-spec.md`, `reference-test-automation.md` | Test workflows |
| `reference-test-e2e-guidelines.md` | E2E mocking patterns, singleton/factory mocking, API contract tests |

---

## Validation Steps {#validation-steps}

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

## E2E Tests and the API Mock Gap {#e2e-api-mock-gap}

### The Problem {#mock-gap-problem}

E2E tests with mocked API data verify frontend rendering but do NOT catch backend bugs.

**Example scenario:**

- Frontend expects `latest_metrics.uptime_seconds`
- E2E test mocks API with `{ uptime_seconds: 86400 }` - test passes
- Backend Pydantic schema doesn't include `uptime_seconds` - BUG not caught
- Production frontend shows "--" because field is missing

### The Solution: API Contract Tests {#mock-gap-solution}

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

### Recommendation {#mock-gap-recommendation}

Pair E2E tests (UI works with mocked data) with contract tests (backend returns expected fields). Neither alone is sufficient for full-stack coverage.

---

## Parameterised Testing {#parameterised-testing}

Use parameterised tests for data-driven scenarios. This reduces duplication and makes it easy to add new test cases.

### Python (pytest) {#parameterised-python}

```python
import pytest

@pytest.mark.parametrize("input_value,expected", [
    ("", False),
    ("short", False),
    ("validpassword123", True),
    ("no_numbers", False),
])
def test_password_validation(input_value, expected):
    assert validate_password(input_value) == expected
```

### TypeScript (vitest/jest) {#parameterised-typescript}

```typescript
it.each([
  ['', false],
  ['short', false],
  ['validpassword123', true],
  ['no_numbers', false],
])('validates password "%s" as %s', (input, expected) => {
  expect(validatePassword(input)).toBe(expected);
});
```

### Go (table-driven) {#parameterised-go}

```go
func TestPasswordValidation(t *testing.T) {
    tests := []struct {
        name     string
        input    string
        expected bool
    }{
        {"empty", "", false},
        {"short", "short", false},
        {"valid", "validpassword123", true},
        {"no_numbers", "no_numbers", false},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := ValidatePassword(tt.input); got != tt.expected {
                t.Errorf("ValidatePassword(%q) = %v, want %v", tt.input, got, tt.expected)
            }
        })
    }
}
```

---

## Test Data Management {#test-data-management}

### Unified Fixtures Directory {#unified-fixtures-directory}

All test fixtures reside in `tests/fixtures/`:

```text

tests/fixtures/
  users.json           # User test data
  servers.json         # Server configurations
  api-responses/       # Mock API response payloads
    auth-success.json
    auth-failure.json
  db-seeds/            # Database seed data
    users.sql
    servers.sql
```

### Factory Functions vs Fixture Files {#factory-vs-fixture-files}

| Approach | Use When | Example |
|----------|----------|---------|
| Fixture files (JSON/YAML) | Static data, API mocks, seed data | `users.json` |
| Factory functions | Dynamic data, randomised values, relationships | `create_user(role="admin")` |

**Python factory example:**

```python
def create_test_user(
    name: str = "Test User",
    email: str | None = None,
    role: str = "user"
) -> User:
    """Factory for test users with sensible defaults."""
    return User(
        id=str(uuid4()),
        name=name,
        email=email or f"test-{uuid4().hex[:8]}@example.com",
        role=role,
        created_at=datetime.now(UTC),
    )
```

**TypeScript factory example:**

```typescript
function createTestUser(overrides: Partial<User> = {}): User {
  return {
    id: crypto.randomUUID(),
    name: 'Test User',
    email: `test-${Date.now()}@example.com`,
    role: 'user',
    createdAt: new Date(),
    ...overrides,
  };
}
```

### Sensitive Data Handling {#sensitive-data-handling}

- **Never commit real credentials** - Use environment variables or test-specific secrets
- **Use obviously fake data** - `test@example.com`, `password123`, `sk_test_*`
- **Sanitise CI logs** - Mask any dynamic secrets in test output
- **Gitignore test artifacts** - `.env.test.local`, `coverage/`, `test-results/`

---

## Flakiness Prevention {#flakiness-prevention}

Flaky tests undermine confidence and slow development. Apply these patterns to prevent flakiness.

### Test Isolation {#test-isolation}

Each test must be independent and repeatable:

```python
# BAD: Tests depend on execution order
class TestUserService:
    user_id = None  # Shared state between tests!

    def test_create_user(self):
        TestUserService.user_id = create_user().id

    def test_get_user(self):
        get_user(TestUserService.user_id)  # Fails if test_create_user didn't run first

# GOOD: Each test creates its own data
class TestUserService:
    def test_create_user(self):
        user = create_user()
        assert user.id is not None

    def test_get_user(self):
        user = create_user()  # Create fresh user for this test
        fetched = get_user(user.id)
        assert fetched.name == user.name
```

### Database Cleanup {#database-cleanup}

Reset database state between tests:

**pytest (transactions):**

```python
@pytest.fixture
def db_session():
    """Provide transactional rollback between tests."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()  # Undo all changes
    connection.close()
```

**vitest (truncate):**

```typescript
beforeEach(async () => {
  await db.execute(sql`TRUNCATE users, servers, logs CASCADE`);
});
```

### Retry Strategies {#retry-strategies}

Use retries sparingly and only for inherently non-deterministic operations:

```python
# pytest-rerunfailures for genuinely flaky external dependencies
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_external_api_integration():
    """Test external API - may have transient failures."""
    response = call_external_api()
    assert response.status == 200
```

**Rule:** Fix the root cause first. Retries mask underlying issues.

### Parallel Test Execution {#parallel-test-execution}

When running tests in parallel, ensure:

- No shared filesystem state (use temp directories)
- No shared database state (use transactions or isolated schemas)
- No port conflicts (use dynamic port allocation)

```python
# pytest-xdist parallel configuration
# pytest -n auto  # Use all CPU cores

@pytest.fixture
def isolated_db():
    """Create isolated schema for parallel test."""
    schema = f"test_{uuid4().hex[:8]}"
    engine.execute(f"CREATE SCHEMA {schema}")
    yield schema
    engine.execute(f"DROP SCHEMA {schema} CASCADE")
```

---

## Test Performance {#test-performance}

### Unit Test Speed {#unit-test-speed}

Unit tests should be fast enough to run on every save:

| Target | Acceptable | Action Needed |
|--------|------------|---------------|
| < 10ms | Ideal | - |
| 10-100ms | Acceptable | Consider optimisation |
| > 100ms | Slow | Mock external calls, review setup |

**Common slowdowns:**

| Cause | Fix |
|-------|-----|
| Database setup | Use in-memory SQLite or mock repository |
| File I/O | Use `io.StringIO` or temp files |
| Network calls | Mock at boundary |
| Heavy fixtures | Lazy-load or scope to session |

### Integration Test Batching {#integration-test-batching}

Group integration tests to share expensive setup:

```python
@pytest.fixture(scope="module")
def database_with_seed_data():
    """Expensive setup - share across module."""
    db = create_database()
    seed_data(db)
    yield db
    db.drop()

class TestUserQueries:
    def test_find_by_email(self, database_with_seed_data):
        # Uses shared database
        pass

    def test_find_by_role(self, database_with_seed_data):
        # Uses same shared database
        pass
```

### Selective Test Running {#selective-test-running}

Run only relevant tests during development:

```bash
# By path
pytest tests/unit/backend/test_auth.py

# By marker
pytest -m "not slow"

# By keyword
pytest -k "login"

# Changed files only (pytest-picked)
pytest --picked

# Watch mode (pytest-watch)
ptw tests/unit/
```

---

## Property-Based Testing {#property-based-testing}

Property-based testing generates random inputs to find edge cases you didn't think of.

### When to Use {#property-when-to-use}

- Parsing/serialisation (round-trip property)
- Mathematical operations (commutativity, associativity)
- Data validation (valid inputs pass, invalid fail)
- State machines (operations leave valid state)

### Python (Hypothesis) {#property-python}

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_encode_decode_roundtrip(text):
    """Encoding then decoding returns original."""
    assert decode(encode(text)) == text

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    """a + b == b + a for all integers."""
    assert a + b == b + a
```

### TypeScript (fast-check) {#property-typescript}

```typescript
import * as fc from 'fast-check';

test('encode/decode roundtrip', () => {
  fc.assert(
    fc.property(fc.string(), (text) => {
      expect(decode(encode(text))).toBe(text);
    })
  );
});
```

---

## Snapshot Testing {#snapshot-testing}

Snapshot testing captures output and compares against stored "golden" files.

### When to Use {#snapshot-when-to-use}

| Good For | Avoid For |
|----------|-----------|
| UI component HTML/JSX | Timestamps, UUIDs |
| CLI output formatting | User-specific data |
| API response structure | Frequently changing content |
| Error message formatting | Large binary files |

### Python (pytest-snapshot) {#snapshot-python}

```python
def test_error_message_format(snapshot):
    error = format_validation_error({"email": "invalid"})
    assert error == snapshot
```

### TypeScript (vitest/jest) {#snapshot-typescript}

```typescript
it('renders login form correctly', () => {
  const { container } = render(<LoginForm />);
  expect(container).toMatchSnapshot();
});
```

### Snapshot Best Practices {#snapshot-best-practices}

1. **Review snapshot changes carefully** - Don't blindly update
2. **Keep snapshots small** - Test specific parts, not entire pages
3. **Use inline snapshots for small outputs** - Easier to review in PRs
4. **Exclude dynamic data** - Mock timestamps, IDs before snapshotting

```typescript
// BAD: Includes timestamp
expect(response).toMatchSnapshot();

// GOOD: Exclude dynamic fields
expect({
  ...response,
  createdAt: '[TIMESTAMP]',
  id: '[UUID]',
}).toMatchSnapshot();
```

---

## Navigation {#navigation}

| Document | Purpose |
|----------|---------|
| `reference-test-best-practices.md` | Core testing practices and checklist |
| `reference-tsd.md`, `reference-test-spec.md`, `reference-test-automation.md` | Test workflows |
| `reference-test-e2e-guidelines.md` | E2E patterns and mocking strategies |
| `reference-test-pitfalls.md` | Common testing mistakes to avoid |
