# SDLC Studio Reference - Testing

Detailed workflows for test artifact generation and automation.

---

# Status Workflow

## /sdlc-studio status - Step by Step

1. **Check Requirements Pipeline**
   - Check if `sdlc-studio/prd.md` exists
   - Check if `sdlc-studio/personas.md` exists
   - Glob `sdlc-studio/epics/EP*.md` and count, parse status
   - Glob `sdlc-studio/stories/US*.md` and count, parse status

2. **Check Testing Pipeline**
   - Check if `sdlc-studio/testing/strategy.md` exists
   - Glob `sdlc-studio/testing/specs/TSP*.md` and count
   - For each spec, count test cases and automation status
   - Scan `tests/` directory for actual test files

3. **Calculate Coverage**
   - Count total test cases across all specs
   - Count cases marked "Automated: Yes"
   - Calculate percentage

4. **Identify Gaps**
   - Epics without test specs
   - Test specs with pending automation
   - Stories without test coverage

5. **Generate Next Steps**
   - Prioritise by impact
   - Suggest specific commands with arguments

6. **Output**
   ```
   Requirements: 80%
     PRD         sdlc-studio/prd.md (14 features)
     Personas    sdlc-studio/personas.md (4 personas)
     Epics       3 epics (2 Done, 1 Draft)
     Stories     12 stories (8 Done, 4 pending)

   Testing: 60%
     Strategy    sdlc-studio/testing/strategy.md
     Specs       2/3 epics covered
     Automation  22/135 cases (16%)

   Next steps:
     /sdlc-studio test-spec --epic EP0003
     /sdlc-studio test-automation --spec TSP0001
   ```

---

# Test Strategy Workflows

## /sdlc-studio test-strategy - Step by Step

1. **Check Prerequisites**
   - Verify PRD exists at sdlc-studio/prd.md
   - Create sdlc-studio/testing/ directory if needed

2. **Gather Context**
   Use AskUserQuestion to collect:
   - Testing objectives and priorities
   - Test level expectations (unit, integration, E2E)
   - Framework preferences
   - CI/CD environment

3. **Analyse PRD**
   - Extract non-functional requirements
   - Identify testability considerations
   - Note integration points requiring testing

4. **Generate Strategy**
   - Use `templates/test-strategy-template.md`
   - Fill test levels based on architecture
   - Define automation candidates
   - Set quality gates

5. **Write File**
   - Write to `sdlc-studio/testing/strategy.md`

6. **Report**
   - Test levels defined
   - Automation approach
   - Quality gates configured

---

## /sdlc-studio test-strategy generate - Step by Step

1. **Analyse Codebase**
   Use Task tool with Explore agent:
   ```
   Analyse codebase for testing patterns:
   1. Existing test files and frameworks
   2. Test configuration (pytest.ini, jest.config, etc.)
   3. CI/CD pipeline test stages
   4. Coverage configuration
   5. Test utilities and helpers
   Return: Current testing landscape
   ```

2. **Infer Strategy**
   - Document existing test levels
   - Identify gaps in coverage
   - Note automation opportunities

3. **Write Strategy**
   - Use template with [INFERRED] confidence markers
   - Include recommendations for gaps

---

# Test Spec Workflows

## /sdlc-studio test-spec - Step by Step (Greenfield)

1. **Check Prerequisites**
   - Verify Test Strategy exists
   - Verify Epics exist in sdlc-studio/epics/
   - Create sdlc-studio/testing/specs/ if needed
   - Scan for existing specs to determine next ID

2. **Parse Epics**
   - Read all Epic files (or specific Epic if --epic flag)
   - Extract acceptance criteria
   - Identify linked User Stories
   - Note technical considerations

3. **Parse Stories**
   - Read linked Story files
   - Extract Given/When/Then acceptance criteria
   - Identify test data requirements

4. **Generate Test Spec**
   For each Epic:
   - Assign ID: TSP{NNNN}
   - Create slug from Epic title
   - Use `templates/test-spec-template.md`
   - Link to parent Epic

   Include:
   - **Scope:** Stories covered, test types needed
   - **Test Cases:** One per AC minimum, with Given/When/Then steps
   - **Fixtures:** Embedded YAML test data
   - **Automation Status:** Initially all "Pending"

5. **Write Files**
   - Write `sdlc-studio/testing/specs/TSP{NNNN}-{slug}.md`
   - Create/update `sdlc-studio/testing/specs/_index.md`

6. **Report**
   - Number of specs created
   - Test cases per spec
   - Next step: `/sdlc-studio test-automation`

---

## /sdlc-studio test-spec generate - Step by Step (Brownfield)

1. **Scan Test Directory**
   - Glob `tests/**/*.py` for pytest
   - Glob `__tests__/**/*.ts` for Jest
   - Glob `*_test.go` for Go
   - Identify framework from file patterns

2. **Parse Test Files**
   For Python/pytest:
   ```python
   # Extract from each test file:
   - class TestX → test group
   - def test_* → test case
   - @pytest.mark.* → tags/categories
   - docstrings → descriptions
   - fixtures used → data requirements
   ```

   For JavaScript/TypeScript:
   ```javascript
   // Extract from each test file:
   - describe() → test group
   - it() / test() → test case
   - beforeEach/afterEach → setup/teardown
   - comments → descriptions
   ```

3. **Group by Feature**
   - Map test files to epics if possible
   - Use file/directory structure as fallback
   - Create logical groupings

4. **Generate Test Specs**
   - Create TSP files with discovered tests
   - Mark all as "Automated: Yes"
   - Link to actual test file paths
   - Note coverage gaps if epics exist

5. **Cross-Reference**
   - Match tests to stories if docstrings contain US IDs
   - Match tests to epics by naming convention
   - Flag untraced tests for review

6. **Write Files**
   - Write `sdlc-studio/testing/specs/TSP{NNNN}-{slug}.md`
   - Update `_index.md`

7. **Report**
   - Tests discovered and documented
   - Coverage vs existing stories
   - Gaps identified

---

## /sdlc-studio test-spec update - Step by Step

1. **Load Test Specs**
   - Read all from sdlc-studio/testing/specs/

2. **Check Automation Status**
   For each Test Spec:
   - Scan tests/ directory for matching files
   - Match test functions to test case IDs
   - Update "Automated: Yes/No" status

3. **Update Files**
   - Update Automation Status table
   - Add file paths for automated tests
   - Update revision history
   - Recalculate _index.md statistics

---

# Test Automation Workflows

## /sdlc-studio test-automation - Step by Step

1. **Check Prerequisites**
   - Verify test specs exist in sdlc-studio/testing/specs/
   - If none, prompt: "Run `/sdlc-studio test-spec` first"

2. **Implementation Discovery (CRITICAL)**

   Before generating any test code, examine the actual implementation to extract:

   a. **Enum Definitions**
      - Grep for `class.*Enum` in services/routes being tested
      - Extract exact enum values (not assumed from spec descriptions)
      - Example: `ConversationPhase.IDENTIFICATION` not `"greeting"`

   b. **Dataclass/Model Structures**
      - Grep for `@dataclass` and Pydantic models
      - Extract all fields and their types
      - Note required vs optional attributes
      - Example: `FieldValue` has `value`, `confidence`, `source`

   c. **Singleton Patterns (Globals)**
      - Look for global variables (e.g., `_discovery_engine = None`)
      - Identify `@lru_cache` decorators and lazy initialization
      - Mocking strategy: patch the global variable directly

   d. **Factory Function Patterns (Dependency Injection)**
      - Look for `def get_*():` factory functions in route files
      - Identify `Depends(get_something)` patterns in route handlers
      - Mocking strategy: patch the factory function, not the class
      - Example: `patch('api.routes.jobs.get_job_service')` not `JobService`

   e. **API Response Status Codes**
      - Read route handlers to find actual status codes returned
      - Don't assume REST conventions (POST=201, etc.)
      - FastAPI defaults to 200 for all responses unless explicitly set

   f. **Schema Versions (for validation tests)**
      - Check validation service for `REQUIRED_TOP_LEVEL` or similar
      - Verify current schema version (e.g., V2.3.0 vs V1)
      - Use current field names, not outdated specs

   g. **API Request Schemas**
      - Check FastAPI route signatures and Pydantic models
      - Extract required request fields
      - Note default values and optional fields

   h. **Generate Mock Helpers**
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

3. **Detect Language**
   Check in order:
   ```
   pyproject.toml OR setup.py → Python
   package.json + "vitest" in devDeps → TypeScript (Vitest)
   package.json → TypeScript (Jest)
   go.mod → Go
   Cargo.toml → Rust
   ```
   If none found, use AskUserQuestion to ask user.

3. **Detect Framework**
   - Python: Check for pytest in dependencies (default: pytest)
   - TypeScript: Check for vitest vs jest in package.json
   - Go: Standard testing package
   - Rust: Standard cargo test

4. **Parse Test Specs**
   - Read TSP file(s) to process
   - Extract test cases not yet automated
   - Extract fixtures/test data
   - Group by test type (unit, integration, api, e2e)

5. **Select Template**
   Based on language + test type:
   - `templates/automation/pytest.py.template`
   - `templates/automation/pytest-api.py.template`
   - `templates/automation/jest.ts.template`
   - `templates/automation/vitest.ts.template`
   - `templates/automation/go_test.go.template`

6. **Generate Test Code**
   For each test case:
   - Convert Given/When/Then to code structure
   - Generate fixture functions from spec data
   - Add docstring with TC ID and story reference
   - Include proper assertions

7. **Determine Output Location**
   | Framework | Unit | Integration | API | E2E |
   |-----------|------|-------------|-----|-----|
   | pytest | tests/unit/ | tests/integration/ | tests/api/ | tests/e2e/ |
   | jest | __tests__/unit/ | __tests__/integration/ | __tests__/api/ | __tests__/e2e/ |
   | vitest | src/__tests__/ | src/__tests__/ | src/__tests__/ | tests/e2e/ |
   | go | same package | same package | same package | same package |

8. **Write Test Files**
   - Write test files to appropriate directories
   - Create directories if needed
   - Group tests by spec (one file per TSP typically)

9. **Update Specs**
   - Mark test cases as "Automated: Yes"
   - Add file path to Automation Status table
   - Update _index.md coverage stats

10. **Run Generated Tests**
    - Execute the generated tests immediately
    - Fix any failures before proceeding
    - Common issues to fix:
      - Mock patch paths (factory functions vs classes)
      - API status codes (verify against actual handlers)
      - Schema mismatches (check current schema version)
    - Only proceed to report when tests pass

11. **Report**
    - Tests generated
    - Files created
    - Test execution status (PASS/FAIL count)
    - Updated coverage percentage

---

## Test Generation Best Practices

These guidelines address common pitfalls discovered during test automation runs.

### Pre-Generation Analysis Checklist

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

### Validation Steps

After generating each test file, validate before running the full suite:

1. **Syntax check** (catches encoding issues, unclosed strings):
   ```bash
   python -m py_compile tests/unit/test_new_feature.py
   ```

2. **Import check** (catches wrong class names, missing modules):
   ```bash
   python -c "from tests.unit.test_new_feature import *"
   ```

3. **Run single file** (faster feedback than full suite):
   ```bash
   pytest tests/unit/test_new_feature.py -v --tb=short
   ```

4. **Only then** run related tests together.

### Test Writing Guidelines

#### Unicode and Encoding

When testing unicode handling functions:

```python
# BAD: Literal unicode can break Python parsing
text = "It's a "test" string"  # Smart quotes break the file!

# GOOD: Use escape sequences
text = "It\u2019s a \u201ctest\u201d string"
```

#### Assertion Patterns

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

#### Model Instantiation

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

#### Enum vs String

Check implementation before using status values:

```python
# If StageResult.status is a string (not enum):
stage = StageResult(stage=0, name="Stage 0", status="complete")

# If using an actual enum:
from api.models import StageStatus
stage = StageResult(stage=0, name="Stage 0", status=StageStatus.COMPLETE)
```

### Coverage Verification

After generating tests, verify coverage:

1. **Count tests vs spec TCs**:
   ```bash
   # Count test functions
   grep -c "def test_\|async def test_" tests/unit/test_feature.py

   # Count TCs in spec (can be fewer - multiple tests per TC is fine)
   grep -c "^### TC" sdlc-studio/testing/specs/TSP0004*.md
   ```

2. **Verify TC IDs in docstrings**:
   ```bash
   # Each test should reference its TC
   grep "TC0" tests/unit/test_feature.py
   ```

3. **Update automation summary**:
   - Edit `sdlc-studio/testing/specs/_index.md`
   - Update Automated count and Coverage percentage
   - Change Status from "Draft" to "Complete"

---

## E2E Test Generation Guidelines

E2E tests have unique requirements that differ from unit/integration tests:

### Mocking Singletons (Global Variables)

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

### Mocking Factory Functions (Dependency Injection)

When routes use factory functions for dependency injection (common in FastAPI):

```python
# Implementation pattern - routes use a factory function:
# api/routes/jobs.py:
#   def get_job_service() -> JobService:
#       return JobService(...)
#
#   @router.get("/{job_id}")
#   async def get_job(job_id: str, service: JobService = Depends(get_job_service)):
#       return await service.get_job(job_id)

# BAD: Patching the class doesn't work - route calls the factory
with patch('api.routes.jobs.JobService') as MockService:
    # This creates a mock class, but the route calls get_job_service()!
    ...

# GOOD: Patch the factory function to return your mock
with patch('api.routes.jobs.get_job_service') as mock_get_service:
    mock_service = MagicMock()
    mock_service.get_job = AsyncMock(return_value=mock_job)
    mock_get_service.return_value = mock_service

    # Now when route calls get_job_service(), it gets mock_service
    response = await client.get(f"/api/v1/jobs/{job_id}")
```

**How to identify** - Check the route file for:
- `Depends(get_something)` patterns
- `def get_*():` factory functions
- Absence of direct class instantiation in route handlers

### API Response Status Codes

Never assume REST conventions. Always verify by reading the route handler:

```python
# BAD: Assumed 201 for POST (REST convention)
assert response.status_code == 201

# GOOD: Check the actual route handler first
# api/routes/jobs.py:
#   @router.post("/")
#   async def create_job(...):
#       ...
#       return job  # Returns 200 by default in FastAPI!

assert response.status_code == 200  # Match actual implementation
```

### Schema Version Verification

For validation tests, always check the current schema version:

```python
# BAD: Used outdated schema fields from old specs
valid_engram = {
    "name": "Test",           # Old V1 field
    "core_identity": {...},   # Old V1 field
}

# GOOD: Check api/services/validation.py for REQUIRED_TOP_LEVEL
# Then use current schema structure
valid_engram = {
    "schema_version": "2.3.0",
    "id": "test-001",
    "slug": "test",
    "identity_and_background": {...},  # V2.3.0 structure
    ...
}
```

### Mock Objects with Attributes

When code accesses attributes on objects (e.g., `field.confidence > 0.4`):

```python
# BAD: Plain dict doesn't have .confidence
state.intent_fields = {"name": {"value": "Ada", "confidence": 0.9}}

# BAD: Basic MagicMock has MagicMock as attributes, not floats
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

### Enum Values

Always extract enum values from implementation, never assume:

```python
# BAD: Guessed from spec description
state.phase = "greeting"  # Doesn't exist!

# GOOD: Use actual enum values from implementation
from api.services.discovery_engine import ConversationPhase
state.phase = ConversationPhase.IDENTIFICATION
# Or as string for JSON payloads:
{"phase": "identification"}  # Exact enum value
```

### Request Payload Completeness

Check route handler for required fields:

```python
# Check the from_dict() or Pydantic model to find required fields
# api/services/discovery_engine.py:
#   state.character_type = CharacterType(data.get("character_type", "UNKNOWN"))

# GOOD: Include all fields that from_dict() expects
response = await client.post("/api/v1/intents/conversation", json={
    "messages": [...],
    "conversation_state": {
        "session_id": session_id,
        "character_type": "UNKNOWN",  # Required by CharacterType enum
        "phase": "identification",     # Valid ConversationPhase value
    },
    "session_id": session_id,
})
```

---

## Test Generation Examples

### Python/pytest Example

Input (from TSP):
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
    """TSP0001: Authentication Tests"""

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
   * TSP0001: Authentication Tests
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

# Migration Workflow

## /sdlc-studio migrate - Step by Step

1. **Scan Existing Artifacts**
   - Glob `sdlc-studio/testing/plans/TP*.md`
   - Glob `sdlc-studio/testing/suites/TS*.md`
   - Glob `sdlc-studio/testing/cases/TC*.md`
   - Glob `sdlc-studio/testing/features/*.feature`
   - Check `sdlc-studio/testing/data/fixtures.yaml`

2. **Build Mapping**
   - Group test cases by parent suite
   - Group suites by parent plan
   - Link plans to epics

3. **Preview (Default Action)**
   ```
   /sdlc-studio migrate

   Scanning existing test artifacts...

   Found:
   - 4 test plans (TP0001-TP0004)
   - 27 test suites (TS0001-TS0027)
   - 135 test cases (TC0001-TC0344)
   - 2 feature files
   - 1 fixtures file

   Migration plan:
   - Create 4 test-spec files (one per plan/epic)
   - Consolidate 135 test cases into specs
   - Archive old files to sdlc-studio/testing/.archive/

   Run `/sdlc-studio migrate --execute` to proceed.
   ```

4. **Execute Migration (--execute flag)**

   a. Create archive directory:
   ```
   sdlc-studio/testing/.archive/
     plans/
     suites/
     cases/
     features/
     data/
   ```

   b. For each Test Plan:
   - Create TSP file with same ID number
   - Include all child suites as sections
   - Include all test cases inline
   - Embed fixtures from fixtures.yaml

   c. Move old files to archive:
   ```
   mv sdlc-studio/testing/plans/* sdlc-studio/testing/.archive/plans/
   mv sdlc-studio/testing/suites/* sdlc-studio/testing/.archive/suites/
   mv sdlc-studio/testing/cases/* sdlc-studio/testing/.archive/cases/
   mv sdlc-studio/testing/features/* sdlc-studio/testing/.archive/features/
   mv sdlc-studio/testing/data/* sdlc-studio/testing/.archive/data/
   ```

   d. Create new index:
   - Write `sdlc-studio/testing/specs/_index.md`

5. **Backup Option (--backup flag)**
   - Create timestamped backup before migration
   - `sdlc-studio/testing/.backup-{timestamp}/`

6. **Report**
   - Files migrated
   - New spec files created
   - Archive location
   - Next step: `/sdlc-studio test-automation`

---

# Traceability Rules

## ID Naming Conventions

| Artefact | Format | Example |
|----------|--------|---------|
| Epic | EP{NNNN} | EP0001 |
| Story | US{NNNN} | US0001 |
| Test Spec | TSP{NNNN} | TSP0001 |
| Test Case | TC{NNNN} | TC0001 |

## Link Formats

From test artifacts, use relative paths:
- To PRD: `../../prd.md`
- To Epic: `../../epics/EP{NNNN}-{slug}.md`
- To Story: `../../stories/US{NNNN}-{slug}.md`
- To Strategy: `../strategy.md`
- To Spec: `TSP{NNNN}-{slug}.md`

## Coverage Matrix

Test Cases should cover all Acceptance Criteria:
- Each AC should have at least one TC
- Map TC to Story AC in test case metadata
- Track coverage in Spec files

---

# Error Handling

- No Test Strategy exists → prompt to run `/sdlc-studio test-strategy` first
- No Epics exist → prompt to run `/sdlc-studio epic` first
- No Test Specs exist → prompt to run `/sdlc-studio test-spec` first
- Unknown language → ask user to specify framework
- `--spec` flag with invalid ID → report error, list valid IDs
- No old artifacts for migration → report nothing to migrate
