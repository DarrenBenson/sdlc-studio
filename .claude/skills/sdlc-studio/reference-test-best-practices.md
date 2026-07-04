# Test Generation Best Practices

<!-- Load when: writing or reviewing tests, choosing verification depth, tuning timeouts -->

## Contents

- [Related References](#test-bp-related-references)
- [Anti-pattern: smoke → "fixed"](#smoke-fix-anti-pattern)
- [How to use the tiers in artefacts](#using-tiers)
- [Assertion Integrity: a test that cannot fail is not a test](#assertion-integrity)
- [Anti-patterns](#timeout-anti-patterns)
- [When the bump is legitimate](#timeout-bump-legitimate)
- [Why Higher Coverage Matters for AI Code](#why-higher-coverage-for-ai)
- [Complexity/churn-weighted test risk](#complexity-test-risk)
- [Review Patterns for AI Tests](#review-patterns-for-ai-tests)
- [Pre-Generation Analysis Checklist](#pre-generation-checklist)
- [Warning Policy](#warning-policy)
- [Test Writing Guidelines](#test-writing-guidelines)
- [Frontend Testing Patterns (Vitest + React)](#frontend-testing-patterns)
- [Coverage Verification](#coverage-verification)
- [Test Anti-Patterns to Avoid](#test-anti-patterns)
- [See Also](#see-also)

Guidelines addressing common pitfalls discovered during test automation runs.

## Related References {#test-bp-related-references}

| Document | Content |
|----------|---------|
| `reference-tsd.md`, `reference-test-spec.md`, `reference-test-automation.md` | Test workflows |
| `reference-test-validation.md` | Validation workflows, contract testing, advanced practices |
| `reference-test-e2e-guidelines.md` | E2E mocking patterns, singleton/factory mocking, API contract tests |

---

# Verification Depth Tiers {#verification-depth-tiers}

Pick the lowest tier sufficient for the claim. Inflating the tier wastes time; deflating it ships claims you can't back up.

| Tier | Means | Time to acquire | When sufficient |
|---|---|---|---|
| **smoke** | Compiles + handshake (one-shot ping) | seconds | "Service starts and the endpoint exists." Never sufficient for a fix-claim. |
| **functional** | Single round-trip exercises the feature path | tens of seconds | "Happy-path API behaviour works once." Sufficient for unit/integration claims and most non-runtime story AC. |
| **conversational** | Multi-turn / multi-step session continuity validated | minutes | "The feature retains state across interactions." Required for any claim involving sessions, transactions, or multi-step flows. |
| **soak** | Behaves under live traffic over a defined window (default 7 days) | days | "It still works after sustained real use." Required to close any production-affecting bug fix. |
| **live** | Operator-confirmed in production for the soak window with no rollback | days, then sealed | "It is in production and stable." Required to mark a feature Done in a deployed system. |

## Anti-pattern: smoke → "fixed" {#smoke-fix-anti-pattern}

The most common verification mistake is closing a bug after a smoke ping passes. Smoke proves the service starts and the endpoint exists. It does not prove the bug is fixed. A bug fix-claim **always** requires at least functional verification, and most production-affecting bugs require conversational + soak.

Symptoms of this anti-pattern in commit messages and bug records:

- "Fixed in v3.X.Y; smoke green on both boxes."
- "Health check passes after rollout."
- "All endpoints respond with 200."

None of these are evidence of a fix. They are evidence the deploy didn't break the handshake. Re-grade the verification by running the multi-turn / multi-step path the bug originally exercised.

## How to use the tiers in artefacts {#using-tiers}

| Artefact | Field | Default | Required to escalate |
|---|---|---|---|
| Bug | `Verification depth:` | `smoke` (initial) | Must be `functional` or higher to mark Fixed; `soak` or higher to Close |
| Story AC | `Verification target:` per AC | `functional` | `conversational` for end-to-end AC; `soak` for production-affecting AC; `live` for AC that ship behind a feature flag awaiting promotion |
| CR / Epic | Inherited from highest-tier child story AC | n/a | n/a |
| `/sdlc-studio code verify` | Reports current verified-depth per AC | based on test types run | n/a |

Cross-reference: `templates/core/bug.md`, `templates/core/story.md`, `reference-bug.md`, `reference-story.md`.

---

# Assertion Integrity: a test that cannot fail is not a test {#assertion-integrity}

Verification depth (above) answers *how far* you exercised the feature. Assertion integrity answers a prior question the depth tiers assume but do not enforce: **would this test go red if the feature were broken?** A green suite over a dead feature is worse than no suite - it manufactures false confidence and lets a non-functional surface ship as "Done". Two failure modes recur, both of which produce a permanently-green test:

## 1. The vacuous / tautological assertion {#vacuous-assertion}

An assertion that is true by construction, or a control-flow shape where the only reachable branch trivially passes and the failure branch silently skips.

**Bad - derived-from-the-same-source (cannot disagree):**
```ts
// data-wired and data-pending are both computed from `edge.bridgeWired`.
// Asserting one against the other can never fail - they are the same boolean.
const wired = page.locator('[data-bridge-wired]')
const pending = page.locator('[data-edge-pending]')
if (await pending.count() === 0) expect(await wired.count()).toBe(edgeCount) // tautology
```

**Bad - the failure branch skips instead of failing, and the pass branch is trivial:**
```ts
const count = await provCells.count()
if (count > 0) { /* ...assert... */ }
else expect(count).toBe(0)   // only reached when count===0 → expect(0).toBe(0), always green
```
Read immediately after a `goto` with no wait for content, `count` is 0 on any slow render, so the vacuous `else` is the branch that actually runs. **The test passes even if the whole feature is deleted.**

**Good - assert the rendered outcome on a known input, so a broken feature is red:**
```ts
// Seed/point at a state where the feature MUST produce specific output, then assert that output.
await gotoAgentGovernance(page, quarantinedConstructId)
await expect(page.getByText('Quarantined')).toBeVisible()            // the state the feature exists to show
await expect(page.getByRole('button', { name: /re-attest/i })).toBeVisible()
```

**Rule:** an assertion must compare the feature's output against a value derived *independently* of that output (a fixture, a seeded state, a literal expected string) - never against another expression computed from the same source. A `skip` is a legitimate outcome only when it is **visible as a skip** (`test.skip(cond, 'reason')`), never disguised as a pass inside an `if/else`.

## 2. The injected-data unit test that bypasses the real wiring {#injected-data-bypass}

A component/unit test that hands the component its data directly proves the component *renders* given data - it says nothing about whether the **data path that feeds it in production** actually delivers that data. The two most expensive bugs hide in exactly that gap: the field the enrichment/loader forgot to copy, the prop the page never threads.

**The trap:** `render(<Panel agent={{ reAttestation: { verdict: 'fail', quarantined: true } }} />)` passes forever, while in production the loader drops `reAttestation` and the panel receives `undefined` - so the real surface is dead and the suite is green.

**Rule:** for any feature whose value depends on a loader/enrichment/adapter delivering a field to a render site, at least one test must exercise the **real path from the boundary** (the fetch/parse/enrichment → the render), not a hand-built props object. In a deployed system this is the **`live` tier on the real data** (the mandated e2e-vs-live run for navigable surfaces): point the surface at a real backing state and assert the operator-visible outcome. Unit tests with injected props are necessary but **never sufficient** to claim the wiring works.

## The mutation check - the cheap proof your test can fail {#mutation-check}

Before trusting a new test (especially e2e), **break the feature on purpose and confirm the test goes red.** Delete the field the loader copies, unset the prop, revert the component to a stub - run the test - it must fail. Restore. A test you have never seen fail is a test you cannot trust. Record it in the AC / bug: `Mutation-checked: unsetting <X> turns <test> red.` This one habit is what separates a `live`-tier claim that means something from one that doesn't, and it is a `templates/core/{story,bug}.md` field + a `templates/workflows/release-gate.md` gate.

**This discipline is executable, not only prose:** `scripts/mutation.py run` applies the
declared fault classes to the changed surface and re-runs the mapped tests per mutation -
a mutation the tests do not kill is reported as a **survivor** finding, and the gate's
`mutation` lane surfaces the report (advisory). See `reference-scripts.md` and
`help/mutation.md`.

Cross-reference: `#test-anti-patterns` (over-mocking is the same disease at the unit boundary), `#verification-depth-tiers`, `reference-test-e2e-guidelines.md`.

---

# Test-Timeout Tuning Discipline {#test-timeout-tuning}

When a test fails on a timeout, the temptation is to bump the timeout. Doing so without measurement is superstition, not engineering. The right rubric:

1. **Measure local timing** 3 times. Take the worst. (Local hardware is the cheapest signal you have.)
2. **Measure CI timing variance** via the last 10 runs of the same test (e.g. `gh run list --workflow=test --json conclusion,databaseId | head -10`, then drill into the test's runtime). Take the worst.
3. **Set the timeout** to 2× the larger of (local-worst, CI-worst).
4. **Leave a comment** at the test definition with the measurements and the date. Example:
   ```ts
   // 30s timeout: local-worst 2.7s × 2 + headroom; CI-worst 13.5s × 2 ≈ 27s.
   // Measured 2026-04-30. Test runs 1010 sequential atomic writes; cost is real.
   it('audit log is bounded to 1000 events on disk', { timeout: 30_000 }, async () => {
   ```

The comment is non-negotiable. Without it, the next person to see the timeout will either re-bump it (compounding the workaround) or rip it out as "magic number" – and neither has any evidence to argue with.

## Anti-patterns {#timeout-anti-patterns}

- **Bump-without-measure.** "It failed at 10s, let's try 30s." This is a workaround dressed as a fix. The timeout might be hiding an unbounded loop, a deadlock, or a real performance regression. Always measure before bumping.
- **Bump-and-forget.** Increasing the timeout but leaving no comment. The next reader has zero context.
- **Disable the test.** "It's flaky, let's `.skip` it for now." If you do this, the bug is now invisible. Re-arm it within 7 days or delete it; do not let `.skip` become permanent.
- **Increase the global default.** Bumping the framework's default timeout to fix one slow test punishes every other test. Use a per-test override.

## When the bump is legitimate {#timeout-bump-legitimate}

Bumping a timeout is the right call when measurement shows the test does real, expected work that takes that long under realistic conditions – for example, sequential disk writes whose count is intentionally large, network round-trips whose latency is bounded by an external service, or warm-up flows that exercise the cold-start path on purpose. In these cases the timeout is part of the test's specification of expected runtime and the comment should explain why the lower bound exists.

If measurement shows the test is taking longer than it *should* be – that is a regression, not a flake. File a bug or an investigation note rather than masking it with a timeout bump.

---

# AI-Assisted Development and Testing

## Why Higher Coverage Matters for AI Code {#why-higher-coverage-for-ai}

AI-assisted development changes the testing equation:

| Factor | Impact | Mitigation |
|--------|--------|------------|
| AI produces code faster | More code = more potential bugs | Higher coverage catches more issues |
| AI can hallucinate | Incorrect implementations look plausible | Tests verify actual behaviour |
| AI may miss edge cases | Focus on happy path | Explicit edge case testing |
| AI code may drift from spec | Implementation doesn't match requirements | Tests enforce spec compliance |

**Target: 90% coverage** - Proven achievable with AI assistance across multiple projects.

## Complexity/churn-weighted test risk {#complexity-test-risk}

Test depth need not be uniform. `complexity.py assess --files <touched>` returns a
**risk_band** (low / medium / high) - a churn-weighted composite of each file's cognitive
complexity and its git churn. Churn is weighted ~3x complexity because the 2026-06-21
calibration against two real boards (consuming repo B n=305) found bug-affected files were
~1.8x more complex but ~4.9x more churned than clean files, and the top-complexity decile
carried ~2.2x the bug rate. Defect risk concentrates in complex, frequently-
changed code - so put the test effort there:

| risk_band | Coverage target | Edge-case scenarios | Verification tier |
| --- | --- | --- | --- |
| low | the project default (e.g. 90%) | the minimum | smoke + functional |
| medium | +5% over default | +50% scenarios; cover each branch | functional |
| high | ~100% of the touched code | exhaustive branch + boundary + failure cases | functional + a contract/integration test |

This is advisory: it reallocates effort, it does not lower the floor. Thresholds are
`complexity.cognitive_high` / `complexity.churn_high` in `.config.yaml`. (Wave-sizing by
token/iteration cost stays deferred: it needs run-cost telemetry, which the defect
calibration does not provide.)

## Review Patterns for AI Tests {#review-patterns-for-ai-tests}

When reviewing AI-generated tests:

1. **Check mock realism** - Would this mock catch a real bug?
2. **Verify edge cases** - Are boundary conditions tested?
3. **Confirm contract coverage** - Is every mocked field contract-tested?
4. **Test the test** - Temporarily break the code and ensure test fails

---

## Pre-Generation Analysis Checklist {#pre-generation-checklist}

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
  grep "^##\|^###" prompts/template.md
  ```

- [ ] **Create verified import block FIRST**: Write and test imports before test code
  ```python
  # Test this imports correctly before proceeding
  from api.models import Job, StageResult, ThumbnailStatus
  from api.services.thumbnail import ThumbnailService, ThumbnailResult
  ```

---

## Warning Policy {#warning-policy}

**Warnings are errors.** Do not dismiss them as "benign" - they indicate real quality issues.

### Why Warnings Matter {#why-warnings-matter}

- **Resource leaks**: Unclosed connections, file handles, async tasks
- **Deprecated APIs**: Code that will break in future library versions
- **Async lifecycle issues**: Event loops closing before cleanup, thread communication failures
- **Flaky tests**: Race conditions that occasionally fail in CI

### Common Warning Types and Fixes {#common-warning-types}

| Warning | Root Cause | Fix |
|---------|------------|-----|
| `PytestUnhandledThreadExceptionWarning` | Thread/async cleanup failed | Ensure proper disposal in fixtures |
| `DeprecationWarning` | Using outdated API | Update to current API pattern |
| `RuntimeWarning: coroutine never awaited` | Missing await | Add await or ensure proper async handling |
| `ResourceWarning: unclosed file` | File not closed | Use context manager (`with open(...)`) |
| `Event loop is closed` (aiosqlite) | DB connections outlive event loop | Dispose engine before event loop closes |

### Async/Database Test Fixture Pattern {#async-database-fixture-pattern}

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

### Running Tests {#running-tests}

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

## Test Writing Guidelines {#test-writing-guidelines}

### Unicode and Encoding {#unicode-and-encoding}

When testing unicode handling functions:

```python
# BAD: Literal unicode can break Python parsing
text = "It's a "test" string"  # Smart quotes break the file!

# GOOD: Use escape sequences
text = "It\u2019s a \u201ctest\u201d string"
```

### Assertion Patterns {#assertion-patterns}

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

### Model Instantiation {#model-instantiation}

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

### Enum vs String {#enum-vs-string}

Check implementation before using status values:

```python
# If StageResult.status is a string (not enum):
stage = StageResult(stage=0, name="Stage 0", status="complete")

# If using an actual enum:
from api.models import StageStatus
stage = StageResult(stage=0, name="Stage 0", status=StageStatus.COMPLETE)
```

---

## Frontend Testing Patterns (Vitest + React) {#frontend-testing-patterns}

Patterns for testing React components with Vitest and jsdom.

### Shared API Client Mock {#shared-api-mock}

Most frontend tests need the same API client mock. Create a complete mock to avoid partial-mock errors:

```typescript
vi.mock("../../src/api/client.ts", () => ({
  fetchProjects: vi.fn(),
  fetchProject: vi.fn(),
  createProject: vi.fn(),
  updateProject: vi.fn(),
  deleteProject: vi.fn(),
  triggerSync: vi.fn(),
  fetchDocuments: vi.fn(),
  fetchDocument: vi.fn(),
  fetchProjectStats: vi.fn(),
  fetchAggregateStats: vi.fn(),
}));

// Then import and type the specific function:
const { fetchProjectStats } = await import("../../src/api/client.ts");
const mockFetch = vi.mocked(fetchProjectStats);
```

**Key:** The `vi.mock()` call must list ALL exports from the module, not just the ones your test uses. Missing exports cause runtime errors in the component under test.

### Libraries That Need jsdom Mocking {#jsdom-mocking}

These libraries use Canvas, SVG rendering, or browser APIs that jsdom doesn't support:

| Library | Issue | Mock Pattern |
|---------|-------|-------------|
| Recharts | Relies on SVG measurement APIs | Mock all chart components as div stubs |
| D3 | Canvas/SVG rendering | Mock at module level |
| MapboxGL | WebGL context | Mock entire module |

**Recharts mock pattern:**

```typescript
vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  BarChart: ({ children, data }: { children: React.ReactNode; data: unknown[] }) => (
    <div data-testid="bar-chart" data-count={data.length}>{children}</div>
  ),
  Bar: ({ dataKey }: { dataKey: string }) => <div data-testid={`bar-${dataKey}`} />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Cell: () => <div data-testid="cell" />,
}));
```

Then assert chart presence via `data-testid` attributes rather than visual output.

### React Router Testing {#react-router-testing}

Use `MemoryRouter` with `initialEntries` for route-dependent components:

```typescript
import { MemoryRouter, Route, Routes } from "react-router";

function renderWithRoute(slug = "my-project") {
  const { MyPage } = await import("../../src/pages/MyPage.tsx");
  return render(
    <MemoryRouter initialEntries={[`/projects/${slug}`]}>
      <Routes>
        <Route path="projects/:slug" element={<MyPage />} />
      </Routes>
    </MemoryRouter>,
  );
}
```

### Dynamic Import Pattern for Mocked Modules {#dynamic-import-pattern}

When using `vi.mock()`, import the component under test dynamically to ensure mocks are applied:

```typescript
vi.mock("../../src/api/client.ts", () => ({ /* ... */ }));

// Dynamic import AFTER mock setup:
async function renderMyComponent() {
  const { MyComponent } = await import("../../src/pages/MyComponent.tsx");
  return render(<MyComponent />);
}
```

### Batch TDD for Frontend Components {#batch-tdd-frontend}

For frontend components, the practical TDD cycle is **batch tests** rather than AC-by-AC:

1. **RED:** Write ALL test cases in one file (all fail because component doesn't exist)
2. **GREEN:** Implement the full component (all tests pass)
3. **REFACTOR:** Clean up if needed

This is more efficient than AC-by-AC because:
- Frontend components are tightly coupled (header + cards + charts in one component)
- Creating a partial component just to pass one AC adds unnecessary intermediate states
- The failing test file as a whole defines the component's contract

---

## Coverage Verification {#coverage-verification}

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

## Test Anti-Patterns to Avoid {#test-anti-patterns}

Common mistakes that cause test failures, false positives, or maintenance burden.

> **The most dangerous anti-pattern is the test that cannot fail** - see `#assertion-integrity` (vacuous/tautological asserts, injected-data tests that bypass the real wiring, and the mutation check that proves a test can go red). Over-mocking below is the unit-boundary form of the same disease.

### 1. Over-Mocking (Mocking at Wrong Boundary) {#anti-pattern-over-mocking}

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

### 2. Framework Testing {#anti-pattern-framework-testing}

**Bad:**
```python
def test_cors_headers_present():
    # Tests FastAPI's CORS middleware, not your application
    assert "access-control-allow-origin" in response.headers
```

**Good:**
- One smoke test to verify CORS is configured correctly
- Focus tests on your business logic, not framework behaviour

### 3. Time-Dependent Tests Without Mocking {#anti-pattern-time-dependent}

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

### 4. Tests That Always Pass {#anti-pattern-always-pass}

**Symptom:** Test mocks return exactly what the code expects. AI is especially prone
to this - it generates mocks that mirror the implementation, so the test passes no
matter how broken the code is.

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

### 5. Mocking Everything in E2E Tests {#anti-pattern-mock-everything}

**Bad:**
```typescript
// Every API call mocked - doesn't test real backend at all
beforeEach(() => {
  cy.intercept('GET', '/api/*', { fixture: 'response.json' });
  cy.intercept('POST', '/api/*', { statusCode: 200 });
});
```

**Good:**
- Mock network for UI rendering tests
- Run separate contract tests against real backend
- Use real backend for integration E2E tests

**Rule:** E2E tests with mocked APIs must be paired with contract tests.

### 6. Skipping Contract Tests Between Layers {#anti-pattern-skip-contract-tests}

**Problem:** Frontend mocks API, backend never tested for those fields.

**Example scenario:**
1. Frontend expects `response.metrics.uptime_seconds`
2. E2E test mocks `{ metrics: { uptime_seconds: 86400 } }` - passes
3. Backend schema doesn't include `uptime_seconds` - no test fails
4. Production shows "--" because field is missing

**Rule:** For every field mocked in E2E tests, write a contract test:
```python
def test_server_response_includes_uptime_seconds(client):
    """Contract: Frontend expects uptime_seconds field."""
    response = client.get('/api/servers/test')
    assert 'uptime_seconds' in response.json()['metrics']
```

### 7. Conditional Assertions {#anti-pattern-conditional-assertions}

Tests using `if` to guard assertions silently pass when the condition isn't met.

```python
# NEVER - silently passes if service_alerts is empty
if service_alerts:
    response = client.post(f"/api/v1/alerts/{service_alerts[0]['id']}/acknowledge")
    assert response.status_code == 400

# ALWAYS - assert the precondition, then the behaviour
assert len(service_alerts) > 0, "Service alerts should be created"
response = client.post(f"/api/v1/alerts/{service_alerts[0]['id']}/acknowledge")
assert response.status_code == 400
```

**Rule:** Never guard a test assertion with `if`. Assert preconditions explicitly.

### 8. Silent Test Helpers {#anti-pattern-silent-helpers}

Helper functions that omit data a feature needs to trigger, so the code under test is
never reached and the test passes vacuously.

```python
# BAD - service alerts only fire when metrics are present, but the helper omits them
def _create_service_down_alert(client, headers, server_id, name):
    client.post("/api/v1/agents/heartbeat", json={
        "server_id": server_id, "services": [{"name": name, "status": "stopped"}],
    }, headers=headers)  # evaluate_services() is inside `if heartbeat.metrics:` - never runs

# GOOD - include the data that triggers the path
def _create_service_down_alert(client, headers, server_id, name):
    client.post("/api/v1/agents/heartbeat", json={
        "server_id": server_id,
        "metrics": {"cpu_percent": 10.0, "memory_percent": 30.0, "disk_percent": 50.0},
        "services": [{"name": name, "status": "stopped"}],
    }, headers=headers)
```

**Rule:** A helper must include everything the feature needs to fire. Verify by
asserting the setup worked (e.g. that the alert was actually created) before testing it.

### Integration test dependency checklist {#integration-dependency-checklist}

Before writing an integration test, read the endpoint source and:

- [ ] Identify every `if` condition in the code path
- [ ] List the data that triggers each condition
- [ ] Ensure the test data satisfies ALL of them
- [ ] Add explicit assertions for the preconditions

Common hidden dependencies: service alerts need `metrics` in the heartbeat; threshold
evaluation needs a `notifications` config; metrics storage needs the server registered
first; remediation actions need approval.

### Debugging low coverage {#debugging-low-coverage}

When tests pass but coverage stays low, the code path is not being hit:

1. Add temporary `print()` markers in the code under test
2. Run with output visible: `pytest -s tests/test_file.py::Test::test_method`
3. If an outer marker prints but an inner one does not, that condition is unmet -
   trace backwards and fix the test data
4. Confirm with `pytest --cov=module --cov-report=term-missing`

---

## See Also {#see-also}

| Document | Purpose |
|----------|---------|
| `reference-tsd.md`, `reference-test-spec.md`, `reference-test-automation.md` | Test workflows |
| `reference-test-validation.md` | Validation workflows and advanced testing patterns |
| `reference-test-e2e-guidelines.md` | E2E mocking patterns and strategies |
