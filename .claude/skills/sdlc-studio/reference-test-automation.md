# SDLC Studio Reference - Test Automation

Detailed workflows for test automation generation and test environment management.

<!-- Load when: generating automated tests, setting up test environments -->

---

## /sdlc-studio test-automation - Step by Step

### 1. Check Prerequisites

- Verify test specs exist in sdlc-studio/test-specs/
- If none, prompt: "Run `/sdlc-studio test-spec` first"

### 2. Implementation Discovery (CRITICAL)

Before generating any test code, examine the actual implementation to extract:

#### a. Enum Definitions

- Grep for `class.*Enum` in services/routes being tested
- Extract exact enum values (not assumed from spec descriptions)
- Example: `ConversationPhase.IDENTIFICATION` not `"greeting"`

#### b. Dataclass/Model Structures

- Grep for `@dataclass` and Pydantic models
- Extract all fields and their types
- Note required vs optional attributes
- Example: `FieldValue` has `value`, `confidence`, `source`

#### c. Singleton Patterns (Globals)

- Look for global variables (e.g., `_discovery_engine = None`)
- Identify `@lru_cache` decorators and lazy initialization
- Mocking strategy: patch the global variable directly
- See: `reference-test-e2e-guidelines.md` → Mocking Singletons

#### d. Factory Function Patterns (Dependency Injection)

- Look for `def get_*():` factory functions in route files
- Identify `Depends(get_something)` patterns in route handlers
- Mocking strategy: patch the factory function, not the class
- See: `reference-test-e2e-guidelines.md` → Mocking Factory Functions

#### e. API Response Status Codes

- Read route handlers to find actual status codes returned
- Don't assume REST conventions (POST=201, etc.)
- FastAPI defaults to 200 for all responses unless explicitly set

#### f. Schema Versions (for validation tests)

- Check validation service for `REQUIRED_TOP_LEVEL` or similar
- Verify current schema version (e.g., V2.3.0 vs V1)
- Use current field names, not outdated specs

#### g. API Request Schemas

- Check FastAPI route signatures and Pydantic models
- Extract required request fields
- Note default values and optional fields

#### h. Generate Mock Helpers

For each dataclass that needs mocking, generate a helper:

```python
def make_field_value(value, confidence=0.8, source="user"):
    """Create a MagicMock that behaves like FieldValue."""
    mock = MagicMock()
    mock.value = value
    mock.confidence = confidence
    mock.source = source
    return mock
```

### 3. Detect Language

| Detection File | Language | Framework | Support Level |
|----------------|----------|-----------|---------------|
| `pyproject.toml`, `setup.py` | Python | pytest | Full - templates and examples |
| `package.json` + vitest | TypeScript | Vitest | Full - templates and examples |
| `package.json` | TypeScript | Jest | Full - templates and examples |
| `go.mod` | Go | testing | Basic - templates only |
| `pom.xml` | Java | JUnit | Full - templates and examples |
| `build.gradle` | Java/Kotlin | JUnit | Full - templates and examples |
| `*.csproj` | C# | xUnit | Full - templates and examples |
| `Cargo.toml` | Rust | cargo test | Detection only - no template |

**Support levels:**

- **Full:** Templates, examples, automatic generation
- **Basic:** Templates exist but fewer examples
- **Detection only:** Language detected but manual test guidance provided

If Rust detected, prompt user:

```text
Detected Rust project. Test automation templates not yet available.
Would you like guidance for writing cargo tests manually?
```

If none found, use AskUserQuestion to ask user.

### 4. Detect Framework

- Python: Check for pytest in dependencies (default: pytest)
- TypeScript: Check for vitest vs jest in package.json
- Go: Standard testing package
- Rust: Standard cargo test

### 5. Parse Test Specs

- Read TS file(s) to process
- Extract test cases not yet automated
- Extract fixtures/test data
- Group by test type (unit, integration, api, e2e)

### 6. Select Template

Based on language + test type:

- `templates/automation/pytest.py.template` - Python unit/integration
- `templates/automation/pytest-api.py.template` - Python API tests
- `templates/automation/jest.ts.template` - TypeScript/Jest
- `templates/automation/vitest.ts.template` - TypeScript/Vitest
- `templates/automation/go_test.go.template` - Go testing
- `templates/automation/junit.java.template` - Java/JUnit 5
- `templates/automation/xunit.cs.template` - C#/xUnit

### 7. Generate Test Code

For each test case:

- Convert Given/When/Then to code structure
- Generate fixture functions from spec data
- Add docstring with TC ID and story reference
- Include proper assertions
- Apply best practices from `reference-test-best-practices.md`

### 8. Determine Output Location

All frameworks use the unified `tests/` structure at project root:

| Test Type | Path | Subdirectory |
|-----------|------|--------------|
| Unit (backend) | `tests/unit/backend/` | `test_*.py`, `*_test.go` |
| Unit (frontend) | `tests/unit/frontend/` | `*.test.ts` |
| Integration | `tests/integration/` | Cross-component tests |
| API | `tests/api/` | Endpoint tests |
| E2E | `tests/e2e/` | `*.spec.ts` browser tests |
| Contracts | `tests/contracts/` | API contract tests |
| Fixtures | `tests/fixtures/` | Shared test data (JSON, YAML) |

### 9. Write Test Files

- Write test files to appropriate directories
- Create directories if needed
- Group tests by spec (one file per TS typically)

### 10. Update Specs

- Mark test cases as "Automated: Yes"
- Add file path to Automation Status table
- Update _index.md coverage stats

### 11. Run Generated Tests

Execute the generated tests immediately with warnings as errors:

```bash
pytest tests/path/to/new_tests.py -v -W error
```

- Fix any failures AND warnings before proceeding
- Common issues: mock paths, API status codes, schema mismatches

> **Warning Policy:** `reference-test-best-practices.md` → Warning Policy

- Only proceed to report when tests pass with ZERO warnings

### 12. Report

- Tests generated
- Files created
- Test execution status (PASS/FAIL count)
- Updated coverage percentage

---

## Test Generation Examples

### Python/pytest Example

Input (from TS):

```markdown
### TC001: Valid login succeeds
**Type:** api
**Story:** US0001
**Automated:** No

#### Scenario
| Step | Action | Expected |
|------|--------|----------|
| 1 | Given valid user credentials | User exists |
| 2 | When POST /login | Request sent |
| 3 | Then 200 OK with token | Session created |
```

Output:

```python
class TestAuthentication:
    """TS0001: Authentication Tests"""

    @pytest.mark.asyncio
    async def test_valid_login_succeeds(self, client, valid_user):
        """TC001: Valid login succeeds

        Story: US0001
        Priority: Critical
        """
        # Given: valid user credentials
        credentials = {
            "email": valid_user["email"],
            "password": valid_user["password"]
        }

        # When: POST /login
        response = await client.post("/login", json=credentials)

        # Then: 200 OK with token
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
```

### TypeScript/Jest Example

Output:

```typescript
describe('Authentication', () => {
  /**
   * TS0001: Authentication Tests
   */

  it('should succeed with valid credentials', async () => {
    /**
     * TC001: Valid login succeeds
     * Story: US0001
     */

    // Given: valid user credentials
    const credentials = {
      email: 'test@example.com',
      password: 'secret123'
    };

    // When: POST /login
    const response = await api.post('/login', credentials);

    // Then: 200 OK with token
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('token');
  });
});
```

---

## Test Environment Workflows

### /sdlc-studio test-env setup - Step by Step

1. **Check Prerequisites**
   - Verify TRD exists at sdlc-studio/trd.md
   - If TRD missing, prompt: "Run `/sdlc-studio trd` first"
   - Check for existing docker-compose.test.yml

2. **Parse TRD Technology Stack**
   Extract services requiring containers:

   | TRD Entry | Container Image | Default Port |
   |-----------|-----------------|--------------|
   | PostgreSQL | postgres:16-alpine | 5432 |
   | MySQL | mysql:8 | 3306 |
   | Redis | redis:7-alpine | 6379 |
   | MongoDB | mongo:7 | 27017 |
   | RabbitMQ | rabbitmq:3-management-alpine | 5672 |
   | Elasticsearch | elasticsearch:8 | 9200 |

3. **Determine Application Build**
   - Detect Dockerfile presence
   - Identify build targets (development, test, production)
   - Extract exposed ports from Dockerfile
   - Identify health check endpoint

4. **Generate docker-compose.test.yml**
   Use `templates/docker-compose.test.template`:
   - Database service with health checks
   - Cache service if Redis/Memcached in TRD
   - Queue service if RabbitMQ/SQS in TRD
   - Application service depending on infrastructure
   - Test runner service depending on application

5. **Generate .env.test**
   Create environment template:

   ```text
   # Database
   DB_HOST=localhost
   DB_PORT=5433  # Test port (offset from default)
   DB_NAME=test_db
   DB_USER=test_user
   DB_PASSWORD=test_pass

   # Application
   APP_PORT=8001  # Test port
   APP_ENV=test
   ```

6. **Write Files**
   - Write docker-compose.test.yml to project root
   - Write .env.test template
   - Add .env.test to .gitignore if not present

7. **Report**
   - Services configured
   - Ports allocated (offset from defaults)
   - Next steps for starting environment

---

### /sdlc-studio test-env up - Step by Step

1. **Validate Configuration**
   - Check docker-compose.test.yml exists
   - Check Docker daemon is running
   - Validate .env.test exists (warn if missing)

2. **Start Services**

   ```bash
   docker compose -f docker-compose.test.yml up -d
   ```

3. **Wait for Health**
   - Poll each service health check
   - Timeout after 60 seconds
   - Report status as services become healthy

4. **Report Status**

   ```text
   ## Test Environment Status

   | Service | Status | Port |
   |---------|--------|------|
   | db | healthy | 5433 |
   | redis | healthy | 6380 |
   | app | healthy | 8001 |
   ```

---

### /sdlc-studio test-env down - Step by Step

1. **Stop Services**

   ```bash
   docker compose -f docker-compose.test.yml down -v
   ```

2. **Clean Volumes**
   - Remove test data volumes
   - Remove test result volumes

3. **Report**
   - Services stopped
   - Volumes cleaned

---

## Running Tests Against Containers

### Integration Tests

```bash
# Start environment
/sdlc-studio test-env up

# Run integration tests
/sdlc-studio code test --type integration

# Or run directly with environment
docker compose -f docker-compose.test.yml run test-runner pytest tests/integration/
```

### E2E Tests

```bash
# Start environment
/sdlc-studio test-env up

# Run E2E tests against containerised app
APP_URL=http://localhost:8001 npx playwright test

# Stop environment
/sdlc-studio test-env down
```

### CI/CD Integration

```yaml
# GitHub Actions
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start test environment
        run: docker compose -f docker-compose.test.yml up -d --wait

      - name: Run tests
        run: docker compose -f docker-compose.test.yml run test-runner

      - name: Collect test results
        if: always()
        run: docker cp $(docker compose -f docker-compose.test.yml ps -q test-runner):/app/test-results ./test-results

      - name: Stop environment
        if: always()
        run: docker compose -f docker-compose.test.yml down -v
```

---

## Error Handling

- No Test Strategy exists → prompt to run `/sdlc-studio tsd` first
- No Epics exist → prompt to run `/sdlc-studio epic` first
- No Test Specs exist → prompt to run `/sdlc-studio test-spec` first
- Unknown language → ask user to specify framework
- `--spec` flag with invalid ID → report error, list valid IDs
- No old artifacts for migration → report nothing to migrate

---

## See Also

- `reference-tsd.md` - Test strategy and status dashboard workflows
- `reference-test-spec.md` - Test specification workflows
- `reference-test-best-practices.md` - Test generation pitfalls and validation
- `reference-test-e2e-guidelines.md` - E2E and mocking patterns
- `help/test-automation.md` - Test automation command quick reference
- `help/test-env.md` - Test environment command quick reference
