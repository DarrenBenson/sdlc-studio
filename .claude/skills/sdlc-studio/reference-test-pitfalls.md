# Test Pitfalls and Anti-Patterns Reference

Reusable guidance for avoiding common test failures that cause tests to pass while actual coverage remains low.

## Anti-Pattern: Conditional Assertions

Tests using `if` to guard assertions silently pass when conditions aren't met.

```python
# NEVER DO THIS - silently passes if result is empty
if result:
    assert result.status == "success"

# ALWAYS DO THIS - fails explicitly if precondition not met
assert result is not None, "Result should not be None"
assert result.status == "success"

# NEVER DO THIS - silently passes if list is empty
if service_alerts:
    alert_id = service_alerts[0]["id"]
    response = client.post(f"/api/v1/alerts/{alert_id}/acknowledge")
    assert response.status_code == 400

# ALWAYS DO THIS - fails explicitly
assert len(service_alerts) > 0, "Service alerts should be created"
alert_id = service_alerts[0]["id"]
response = client.post(f"/api/v1/alerts/{alert_id}/acknowledge")
assert response.status_code == 400
```

**Rule:** Never use `if` to guard test assertions. Use explicit assertions for preconditions.

## Anti-Pattern: Silent Test Helpers

Helper functions that don't include all required data for features to trigger.

### Example: Missing Required Fields

```python
# BAD - Service alerts only evaluated when metrics present
def _create_service_down_alert(client, auth_headers, server_id, service_name):
    client.post("/api/v1/agents/heartbeat", json={
        "server_id": server_id,
        "services": [{"name": service_name, "status": "stopped"}],
    }, headers=auth_headers)
    # Service alerts never created because evaluate_services()
    # is inside `if heartbeat.metrics:` block

# GOOD - Includes metrics to trigger service evaluation
def _create_service_down_alert(client, auth_headers, server_id, service_name):
    client.post("/api/v1/agents/heartbeat", json={
        "server_id": server_id,
        "metrics": {"cpu_percent": 10.0, "memory_percent": 30.0, "disk_percent": 50.0},
        "services": [{"name": service_name, "status": "stopped"}],
    }, headers=auth_headers)
```

### How to Verify Helpers Work

1. Add debug output during development
2. Run with `pytest -s` to see output
3. If expected behaviour doesn't occur, trace the code path

```python
def _create_service_down_alert(client, auth_headers, server_id, service_name):
    response = client.post("/api/v1/agents/heartbeat", json={...}, headers=auth_headers)

    # Debug: verify alert was created
    alerts = client.get(f"/api/v1/alerts?server_id={server_id}", headers=auth_headers)
    print(f"DEBUG: Created {len(alerts.json()['alerts'])} alerts")

    # Remove debug code after confirming it works
```

## Integration Test Dependency Checklist

Before writing an integration test:

- [ ] **Read the endpoint source code** being tested
- [ ] **Identify all `if` conditions** in the code path
- [ ] **List what data triggers** each condition
- [ ] **Ensure test data satisfies ALL conditions**
- [ ] **Add explicit assertions** for preconditions

### Common Hidden Dependencies

| Feature | Hidden Dependency |
|---------|------------------|
| Service alerts | Requires `metrics` in heartbeat payload |
| Alert acknowledgement | Requires service status to be "running" |
| Threshold evaluation | Requires `notifications` config |
| Metrics storage | Requires server to be registered first |
| Remediation actions | Requires action to be approved |

## Debugging Low Coverage

When tests pass but coverage remains low:

### Step 1: Add Debug Prints

```python
# In the code being tested (temporarily)
async def some_endpoint():
    print("DEBUG: Entered endpoint")
    if condition:
        print("DEBUG: Condition met")
        # ... code that should be tested
```

### Step 2: Run with Output Visible

```bash
pytest -s tests/test_file.py::TestClass::test_method
```

### Step 3: Analyse Output

- If "Entered endpoint" appears but "Condition met" doesn't, the condition isn't being satisfied
- If neither appears, the endpoint isn't being called correctly

### Step 4: Trace Backwards

Find what condition isn't being met and update test data.

## Test Review Checklist

When reviewing tests, check for:

1. **No conditional assertions** - All `if` guards should be explicit assertions
2. **Complete test data** - Helpers include all required fields
3. **Precondition assertions** - Tests assert setup worked before testing behaviour
4. **Coverage verification** - Run with `--cov` to verify code paths hit

```bash
# Verify specific test coverage
pytest tests/test_file.py --cov=module --cov-report=term-missing
```

## Related

- TSD template: `templates/tsd-template.md` (Test Anti-Patterns section)
- TSD help: `help/tsd.md` (Coverage Troubleshooting section)
- Test best practices: `reference-test-best-practices.md`
