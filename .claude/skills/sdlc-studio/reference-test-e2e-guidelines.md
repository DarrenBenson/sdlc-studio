# E2E Test Generation Guidelines

<!--
Load: On test-automation, test-spec, or when generating integration/E2E tests
Dependencies: reference-testing.md (main workflow)
Related: reference-test-best-practices.md (validation steps)
-->

E2E tests have unique requirements that differ from unit/integration tests. This guide covers patterns applicable across languages, then provides language-specific guidance.

## Related References

| Document | Content |
|----------|---------|
| `reference-testing.md` | Main test workflows (tsd, test-spec, test-automation) |
| `reference-test-best-practices.md` | Pre-generation checklist, validation steps, test writing guidelines |

---

# Language-Agnostic Patterns

These patterns apply regardless of your technology stack.

## Critical: E2E Mocking Blindspot

**E2E tests with mocked API data verify the frontend works correctly but do NOT catch backend bugs.**

When E2E tests mock API responses (Playwright route interception, MSW, etc.), they test the frontend's ability to render data correctly. However, if the backend omits a field from its response, E2E tests still pass because mocked data includes the field.

**Example:** Frontend expects `latest_metrics.uptime_seconds`. E2E test mocks API with `uptime_seconds: 86400`. Test passes. But backend doesn't return `uptime_seconds` in actual response. Production shows "--" instead of value.

**Solution:** Pair E2E tests with backend contract tests. Neither alone is sufficient.

---

## The API Contract Test Pattern

For every field the frontend consumes, write a backend contract test that:

1. Creates real data via the API
2. Retrieves it via the endpoint being tested (no mocking)
3. Asserts the expected field exists with correct type/value

This catches schema mismatches between frontend expectations and backend responses.

---

## Mock Boundary Principles

### Mock at System Boundaries, Not Internal Libraries

**Boundaries to mock:**
- Network (HTTP requests, WebSocket connections)
- Filesystem (file reads/writes)
- Time (clocks, timers)
- External services (databases, message queues)

**Do NOT mock:**
- Internal libraries or utilities
- HTTP client classes (mock the network instead)
- Internal service classes (let real code run)

---

## Status Code Verification

**Never assume REST conventions.** Always verify by reading the route handler:

- POST doesn't always return 201 (many frameworks default to 200)
- DELETE doesn't always return 204
- PATCH doesn't always return 200

Read the actual handler implementation to confirm expected status codes.

---

# Python/FastAPI Patterns

## Contract Test Example

```python
# tests/test_api_response_schema.py
class TestLatestMetricsResponseSchema:
    """Verify API response matches frontend TypeScript types."""

    def test_latest_metrics_includes_uptime_seconds(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Catches bugs where data is stored but not returned."""
        # Create real data via API
        heartbeat = {"server_id": "test", "metrics": {"uptime_seconds": 86400}, ...}
        client.post("/api/v1/agents/heartbeat", json=heartbeat, headers=auth_headers)

        # Retrieve via API being tested (no mocking!)
        response = client.get("/api/v1/servers/test", headers=auth_headers)
        metrics = response.json()["latest_metrics"]

        # Assert field present with expected value
        assert "uptime_seconds" in metrics, "uptime_seconds missing from response"
        assert metrics["uptime_seconds"] == 86400
```

## Mocking Singletons (Global Variables)

When services use singleton patterns with global caching:

```python
# BAD: Patching the getter doesn't work if global is already set
with patch('api.routes.intents.get_discovery_engine') as mock:
    # Global _discovery_engine may already be cached!
    ...

# GOOD: Patch the global directly
import api.routes.intents as intents_module
original = intents_module._discovery_engine
intents_module._discovery_engine = mock_engine
yield mock_engine
intents_module._discovery_engine = original  # Restore
```

## Mocking Factory Functions (Dependency Injection)

When routes use FastAPI's `Depends()` with factory functions:

```python
# Route pattern:
#   def get_job_service() -> JobService:
#       return JobService(...)
#
#   @router.get("/{job_id}")
#   async def get_job(service: JobService = Depends(get_job_service)):
#       return await service.get_job(job_id)

# BAD: Patching the class doesn't work - route calls the factory
with patch('api.routes.jobs.JobService') as MockService:
    ...

# GOOD: Patch the factory function to return your mock
with patch('api.routes.jobs.get_job_service') as mock_get_service:
    mock_service = MagicMock()
    mock_service.get_job = AsyncMock(return_value=mock_job)
    mock_get_service.return_value = mock_service

    response = await client.get(f"/api/v1/jobs/{job_id}")
```

**Detection:** Look for `Depends(get_something)` in route handlers.

## Mock Objects with Attributes

When code accesses attributes on objects (e.g., `field.confidence > 0.4`):

```python
# BAD: Plain dict doesn't have .confidence
state.intent_fields = {"name": {"value": "Ada", "confidence": 0.9}}

# BAD: Basic MagicMock attributes are MagicMock, not floats
state.intent_fields = {"name": MagicMock(value="Ada")}
# fv.confidence > 0.4 fails: MagicMock > float is TypeError

# GOOD: Explicitly set attributes with correct types
def make_field_value(value, confidence=0.8):
    mock = MagicMock()
    mock.value = value
    mock.confidence = confidence  # Float, not MagicMock
    return mock

state.intent_fields = {"name": make_field_value("Ada", 0.9)}
```

## Schema Version Verification

For validation tests, check current schema version:

```python
# BAD: Used outdated schema fields from old specs
valid_engram = {
    "name": "Test",           # Old V1 field
    "core_identity": {...},   # Old V1 field
}

# GOOD: Check api/services/validation.py for REQUIRED_TOP_LEVEL
valid_engram = {
    "schema_version": "2.3.0",
    "id": "test-001",
    "slug": "test",
    "identity_and_background": {...},  # V2.3.0 structure
}
```

---

# TypeScript/Node.js Patterns

## Contract Test Example

```typescript
// tests/api/contracts/server.contract.test.ts
describe('Server API Contract', () => {
  it('should include uptime_seconds in server response', async () => {
    // Create real data
    await createTestServerWithMetrics({ uptime_seconds: 86400 });

    // Call actual API (no MSW mocking!)
    const response = await request(app).get('/api/v1/servers/test-server');

    // Assert contract
    expect(response.status).toBe(200);
    expect(response.body.latest_metrics).toHaveProperty('uptime_seconds');
    expect(response.body.latest_metrics.uptime_seconds).toBe(86400);
  });
});
```

## E2E with Playwright and MSW

```typescript
// tests/e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';
import { setupMSWHandlers } from '../mocks/handlers';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // MSW intercepts network requests
    await setupMSWHandlers(page, {
      servers: [
        { id: 'srv1', latest_metrics: { uptime_seconds: 86400 } }
      ]
    });
  });

  test('displays server uptime', async ({ page }) => {
    await page.goto('/dashboard');
    // This only tests: "given mocked data, does UI render it?"
    // Does NOT test: "does backend actually return this data?"
    await expect(page.getByTestId('uptime-display')).toContainText('1 day');
  });
});

// PAIR WITH: Backend contract test for uptime_seconds field
```

## Mocking with Jest/Vitest

```typescript
// GOOD: Mock at module boundary
vi.mock('../services/apiClient', () => ({
  fetchServers: vi.fn().mockResolvedValue([{ id: 'test' }])
}));

// BAD: Mocking internal implementation details
vi.mock('../utils/calculateUptime', () => ({
  calculateUptime: vi.fn().mockReturnValue(86400)
}));
```

## Status Code Verification

```typescript
// Check actual Express/Fastify route handler:
// router.post('/items', async (req, res) => {
//   const item = await createItem(req.body);
//   res.json(item);  // Returns 200 by default!
// });

// GOOD: Use actual status from route
expect(response.status).toBe(200);

// BAD: Assume REST conventions
expect(response.status).toBe(201);  // May not be true!
```

---

# Go Patterns

## Contract Test Example

```go
func TestServerResponseIncludesUptimeSeconds(t *testing.T) {
    // Create real server with metrics
    server := createTestServerWithMetrics(t, map[string]interface{}{
        "uptime_seconds": 86400,
    })

    // Call actual API
    req := httptest.NewRequest("GET", "/api/v1/servers/"+server.ID, nil)
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    // Assert contract
    if w.Code != http.StatusOK {
        t.Fatalf("expected 200, got %d", w.Code)
    }

    var resp ServerResponse
    json.Unmarshal(w.Body.Bytes(), &resp)

    if resp.LatestMetrics.UptimeSeconds != 86400 {
        t.Errorf("uptime_seconds = %d; want 86400", resp.LatestMetrics.UptimeSeconds)
    }
}
```

## Mocking External Services

```go
// Use interfaces for dependency injection
type MetricsStore interface {
    Get(serverID string) (*Metrics, error)
}

// In tests, provide mock implementation
type mockMetricsStore struct {
    metrics map[string]*Metrics
}

func (m *mockMetricsStore) Get(serverID string) (*Metrics, error) {
    return m.metrics[serverID], nil
}

func TestHandler(t *testing.T) {
    store := &mockMetricsStore{
        metrics: map[string]*Metrics{
            "test": {UptimeSeconds: 86400},
        },
    }
    handler := NewHandler(store)
    // Test handler with mock store
}
```

## Time Mocking with Clockwork

```go
import "github.com/jonboulle/clockwork"

type Service struct {
    clock clockwork.Clock
}

func (s *Service) IsExpired(createdAt time.Time) bool {
    return s.clock.Now().Sub(createdAt) > 24*time.Hour
}

// In tests:
func TestIsExpired(t *testing.T) {
    fakeClock := clockwork.NewFakeClock()
    svc := &Service{clock: fakeClock}

    createdAt := fakeClock.Now()
    fakeClock.Advance(25 * time.Hour)

    if !svc.IsExpired(createdAt) {
        t.Error("expected expired")
    }
}
```

---

# Summary: Full-Stack Test Strategy

For comprehensive coverage, use this three-layer approach:

| Layer | What It Tests | Mocking Level |
|-------|---------------|---------------|
| Unit tests | Individual functions/classes | Mock dependencies |
| Contract tests | API returns expected fields | No mocking - real backend |
| E2E tests | UI renders correctly | Mock network/API responses |

**Contract tests bridge the gap** between E2E tests (which mock APIs) and backend reality. Without them, schema changes in the backend won't be caught until production.
