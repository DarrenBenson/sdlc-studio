<!--
Template: Test Strategy Document
File: sdlc-studio/tsd.md
Status values: See reference-outputs.md
Related: help/tsd.md, reference-testing.md
-->
# Test Strategy Document

> **Project:** {{project_name}}
> **Version:** {{version}}
> **Last Updated:** {{last_updated}}
> **Owner:** {{owner}}

## Overview

{{overview}}

## Test Objectives

- {{objective}}

## Scope

### In Scope

- {{in_scope_item}}

### Out of Scope

- {{out_of_scope_item}}

## Test Levels

### Coverage Targets

**Default: 90% line coverage**

| Level | Target | Rationale |
|-------|--------|-----------|
| Unit | 90% | Core business logic must be thoroughly tested |
| Integration | 85% | API and database interactions |
| E2E | 100% feature coverage | Every user-visible feature has at least one spec file |

**Why 90%?** AI-assisted development produces code faster than traditional development. Higher coverage gates ensure AI-generated code is correct and catches hallucinations early. This target has been proven achievable with AI assistance across multiple projects.

### Unit Testing

| Attribute | Value |
|-----------|-------|
| Coverage Target | 90% (see Coverage Targets above) |
| Framework | {{unit_framework}} |
| Responsibility | {{unit_responsibility}} |
| Execution | {{unit_execution}} |

### Integration Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{integration_scope}} |
| Framework | {{integration_framework}} |
| Responsibility | {{integration_responsibility}} |
| Execution | {{integration_execution}} |

### End-to-End Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{e2e_scope}} |
| Framework | {{e2e_framework}} |
| Responsibility | {{e2e_responsibility}} |
| Execution | {{e2e_execution}} |

### E2E Feature Coverage Matrix

**Target:** One spec file per user-visible feature area.

| Feature Area | Spec File | Test Count | Status |
|--------------|-----------|------------|--------|
| {{feature_area}} | {{spec_file}} | {{test_count}} | {{status}} |

**Naming convention:** `[feature].spec.ts` (or language equivalent)

**Minimum per feature:**
- Happy path scenario
- Key error states
- Authentication/authorisation checks (if applicable)

### API Contract Testing

**Purpose:** Bridge the gap between E2E tests (which mock APIs) and backend reality.

> **Critical insight:** E2E tests with mocked API data verify the frontend works correctly but do NOT catch backend bugs. If the backend omits a field from its response, E2E tests still pass because mocked data includes the field.

**Contract Test Pattern:**

For every field the frontend consumes:
1. Create real data via the API
2. Retrieve it via the endpoint being tested (no mocking)
3. Assert the expected field exists with correct type/value

**Multi-Language Examples:**

*Python (pytest):*
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

*TypeScript (vitest/jest):*
```typescript
it('includes uptime_seconds in server response', async () => {
  await createTestServer({ uptime_seconds: 86400 });
  const response = await request(app).get('/api/v1/servers/test');
  expect(response.body.metrics).toHaveProperty('uptime_seconds');
});
```

*Go:*
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

### Performance Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{performance_scope}} |
| Framework | {{performance_framework}} |
| Responsibility | {{performance_responsibility}} |
| Execution | {{performance_execution}} |

### Security Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{security_scope}} |
| Tools | {{security_tools}} |
| Responsibility | {{security_responsibility}} |
| Execution | {{security_execution}} |

## Test Environments

| Environment | Purpose | URL | Data |
|-------------|---------|-----|------|
| Local | Development | localhost | Mocked/Fixtures |
| {{env_name}} | {{env_purpose}} | {{env_url}} | {{env_data}} |

## Test Data Strategy

### Approach

{{test_data_approach}}

### Sensitive Data

{{sensitive_data_handling}}

### Data Reset

{{data_reset_strategy}}

## Automation Strategy

### Automation Candidates

{{automation_candidates}}

- All regression tests for stable features
- Happy path scenarios for all user stories
- Critical business flows
- API contract validation

### Manual Testing

{{manual_testing}}

- Exploratory testing
- Usability assessment
- Edge cases requiring human judgement

### Automation Framework Stack

| Layer | Tool | Language |
|-------|------|----------|
| E2E/UI | {{e2e_tool}} | {{e2e_language}} |
| API | {{api_tool}} | {{api_language}} |
| Unit | {{unit_tool}} | {{unit_language}} |
| BDD | {{bdd_tool}} | Gherkin |
| Performance | {{perf_tool}} | {{perf_language}} |

## CI/CD Integration

### Pipeline Stages

1. **Pre-commit:** Linting, unit tests
2. **PR:** Unit + integration tests
3. **Merge to main:** Full E2E suite
4. **Nightly:** Full regression + performance
5. **Pre-release:** Full suite + security scan

### Quality Gates

| Gate | Criteria | Blocking |
|------|----------|----------|
| Unit coverage | {{unit_gate_criteria}} | {{unit_gate_blocking}} |
| Integration tests | 100% pass | Yes |
| E2E critical path | 100% pass | Yes |
| E2E full suite | {{e2e_gate_criteria}} | No (alerts) |
| Performance | {{perf_gate_criteria}} | {{perf_gate_blocking}} |

## Defect Management

### Severity Definitions

| Severity | Definition | SLA |
|----------|------------|-----|
| Critical | System unusable, data loss | {{critical_sla}} |
| High | Major feature broken, no workaround | {{high_sla}} |
| Medium | Feature impaired, workaround exists | {{medium_sla}} |
| Low | Minor issue, cosmetic | Backlog |

### Defect Workflow

{{defect_workflow}}

## Reporting

### Metrics Tracked

- Test pass/fail rates by suite
- Code coverage trends
- Defect discovery rate
- Test execution time
- Flaky test percentage

### Reporting Cadence

- **Daily:** CI dashboard
- **Sprint:** Test summary in retrospective
- **Release:** Full test report

## Roles & Responsibilities

| Role | Responsibilities |
|------|------------------|
| Developers | Unit tests, integration tests, fixing bugs |
| QA Engineers | Test plans, E2E tests, exploratory testing |
| Tech Lead | Test strategy review, tooling decisions |
| Product Owner | Acceptance criteria validation, UAT |

## Tools & Infrastructure

| Purpose | Tool |
|---------|------|
| Test Management | {{test_management_tool}} |
| CI/CD | {{ci_cd_tool}} |
| Browser Automation | {{browser_automation_tool}} |
| API Testing | {{api_testing_tool}} |
| Mocking | {{mocking_tool}} |
| Coverage | {{coverage_tool}} |
| Reporting | {{reporting_tool}} |

### Coverage Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| Tool | {{coverage_tool}} | See language-specific tools below |
| Source | {{coverage_source}} | Package/source directory |
| Branch | {{coverage_branch}} | Yes for branch coverage |
| Threshold | 90% | Per Coverage Targets section |

**Language-Specific Configuration:**

| Language | Tool | Config File | Key Settings |
|----------|------|-------------|--------------|
| Python | pytest-cov | `pyproject.toml` | `concurrency = ["greenlet", "thread"]` for async |
| TypeScript | vitest/coverage-v8 or jest | `vitest.config.ts` / `jest.config.js` | `coverage.thresholds.lines: 90` |
| Go | `go test -cover` | N/A | `-coverprofile=coverage.out` |

**Async Framework Notes:**

*Python (FastAPI, Starlette, async frameworks):*
- Coverage.py requires `concurrency = ["greenlet", "thread"]`
- Without this, async route handlers may show 0% coverage despite tests passing
- Starlette's TestClient uses anyio which runs code in greenlets

*TypeScript (Node.js async):*
- V8 coverage handles async/await natively
- No special configuration needed for async code

*Go (goroutines):*
- Standard coverage handles goroutines automatically
- Use `-race` flag to detect race conditions in concurrent code

## Test Anti-Patterns

Document project-specific test pitfalls here as they are discovered.

### Conditional Assertion Anti-Pattern

**Problem:** Tests using `if result:` patterns silently pass when conditions aren't met.

```python
# BAD - silently passes if no data created
if results:
    assert results[0]["status"] == "success"

# GOOD - fails explicitly if precondition not met
assert len(results) > 0, "Results should not be empty"
assert results[0]["status"] == "success"
```

**Rule:** Never use `if` to guard test assertions. Use explicit assertions for preconditions.

### Silent Test Helpers

**Problem:** Helper functions missing required data fields for features to trigger.

**Rule:** When creating test helpers, trace the full code path to ensure all triggers are satisfied.

### Integration Test Dependency Chains

**Problem:** Testing feature A without understanding it depends on feature B being triggered first.

**Checklist before writing integration tests:**
1. Read the endpoint/function source code
2. Identify all conditional branches (`if` statements)
3. Trace what data triggers each branch
4. Ensure test data satisfies all required conditions

### Project-Specific Pitfalls

{{#if test_antipatterns}}
{{test_antipatterns}}
{{else}}
*Document project-specific pitfalls as they are discovered during development.*
{{/if}}

### Additional Anti-Patterns

**Mocking everything in E2E tests:**
- E2E tests should exercise real code paths where possible
- Use mocking at system boundaries (network, external services)
- Pair mocked E2E tests with contract tests for full coverage

**Skipping contract tests between layers:**
- Contract tests catch schema mismatches early
- Required when frontend mocks backend responses
- Write contract tests for every field the frontend consumes

## Test Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| Test Root | `tests/` | Project root-relative path |
| Organisation | By type | `unit/`, `integration/`, `api/`, `e2e/`, `contracts/` |

## Test Organisation (Unified Structure)

All tests reside in a unified `tests/` directory at the project root:

```
tests/
  unit/
    backend/          # Python/Go unit tests
    frontend/         # TypeScript unit tests
  integration/        # Cross-component tests
  api/               # API endpoint tests
  e2e/               # End-to-end browser tests
  contracts/         # API contract tests
  fixtures/          # Shared test data (JSON, YAML)
```

**Naming conventions:**

| Language | Pattern | Example |
|----------|---------|---------|
| Python | `test_*.py` | `tests/unit/backend/test_auth.py` |
| TypeScript | `*.test.ts` | `tests/unit/frontend/auth.test.ts` |
| E2E (any) | `*.spec.ts` | `tests/e2e/dashboard.spec.ts` |
| Go | `*_test.go` | `tests/unit/backend/auth_test.go` |

**Key principles:**
- Single `tests/` directory at project root
- Subdirectories by test type first, then by component
- Shared fixtures in `tests/fixtures/`

### Contract Tests

**Purpose:** Bridge the gap between E2E tests (which mock APIs) and backend reality.

Contract tests verify that the backend returns fields the frontend expects:
- Created when E2E tests mock API responses
- Assert actual API responses include expected fields
- Located in `tests/contracts/`

See `reference-test-e2e-guidelines.md` for contract test patterns.

## Related Specifications

- [Product Requirements Document](../prd.md)
- [User Personas](../personas.md)

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{revision_date}} | {{revision_author}} | {{revision_change}} |
