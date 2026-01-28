<!--
Module: Contract Test Patterns
Extends: templates/core/tsd.md
Section: After API Contract Testing
Load: tsd create, test-spec (when E2E tests mock APIs)
-->

## Contract Test Implementation

### Purpose

Bridge the gap between E2E tests (which mock APIs) and backend reality.

> **Critical insight:** E2E tests with mocked API data verify the frontend works correctly but do NOT catch backend bugs. If the backend omits a field from its response, E2E tests still pass because mocked data includes the field.

### Contract Test Pattern

For every field the frontend consumes:
1. Create real data via the API
2. Retrieve it via the endpoint being tested (no mocking)
3. Assert the expected field exists with correct type/value

### Multi-Language Examples

**Python (pytest):**
```python
def test_server_response_includes_uptime(client, auth_headers):
    """Contract: Frontend expects uptime_seconds field."""
    # Create real data
    client.post("/api/v1/heartbeat", json={"uptime_seconds": 86400}, headers=auth_headers)
    # Retrieve via API (no mocking)
    response = client.get("/api/v1/servers/test", headers=auth_headers)
    # Assert contract
    assert "uptime_seconds" in response.json()["metrics"]
```

**TypeScript (vitest/jest):**
```typescript
it('includes uptime_seconds in server response', async () => {
  await createTestServer({ uptime_seconds: 86400 });
  const response = await request(app).get('/api/v1/servers/test');
  expect(response.body.metrics).toHaveProperty('uptime_seconds');
});
```

**Go:**
```go
func TestServerResponseIncludesUptime(t *testing.T) {
    createTestServer(t, map[string]any{"uptime_seconds": 86400})
    resp := httptest.NewRecorder()
    router.ServeHTTP(resp, httptest.NewRequest("GET", "/api/v1/servers/test", nil))
    var result ServerResponse
    json.Unmarshal(resp.Body.Bytes(), &result)
    if result.Metrics.UptimeSeconds == 0 {
        t.Error("uptime_seconds missing from response")
    }
}
```

### Contract Test Checklist

- [ ] Every mocked field in E2E tests has a contract test
- [ ] Contract tests use real API calls (no mocking)
- [ ] Contract tests run in CI before E2E tests
- [ ] Contract test failures block E2E test execution
