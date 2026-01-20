# SDLC Studio Reference - Testing

Detailed workflows for test artifact generation and automation.

<!-- Load when: generating test strategy, test specs, or test automation -->

## Related References

| Document | Content |
|----------|---------|
| `reference-prd.md, reference-trd.md, reference-persona.md` | PRD, TRD, Persona workflows |
| `reference-epic.md, reference-story.md, reference-bug.md` | Epic, Story, Bug workflows |
| `reference-test-best-practices.md` | Pre-generation checklist, validation steps, test writing guidelines |
| `reference-test-e2e-guidelines.md` | E2E mocking patterns, singleton/factory mocking, API contract tests |

---

# Status Workflow

## /sdlc-studio status - Step by Step

1. **Check Requirements Pipeline**
   - Check if `sdlc-studio/prd.md` exists
   - Check if `sdlc-studio/personas.md` exists
   - Glob `sdlc-studio/epics/EP*.md` and count, parse status
   - Glob `sdlc-studio/stories/US*.md` and count, parse status

2. **Check Testing Pipeline**
   - Check if `sdlc-studio/tsd.md` exists
   - Glob `sdlc-studio/test-specs/TS*.md` and count
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
     Strategy    sdlc-studio/tsd.md
     Specs       2/3 epics covered
     Automation  22/135 cases (16%)

   Next steps:
     /sdlc-studio test-spec --epic EP0003
     /sdlc-studio test-automation --spec TS0001
   ```

---

# TSD Workflows

## /sdlc-studio tsd - Step by Step

1. **Check Prerequisites**
   - Verify PRD exists at sdlc-studio/prd.md
   - Create sdlc-studio/ directory if needed

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
   - Use `templates/tsd-template.md`
   - Fill test levels based on architecture
   - Define automation candidates
   - Set quality gates

5. **Write File**
   - Write to `sdlc-studio/tsd.md`

6. **Report**
   - Test levels defined
   - Automation approach
   - Quality gates configured

---

## /sdlc-studio tsd generate - Step by Step

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
   - Create sdlc-studio/test-specs/ if needed
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
   - Assign ID: TS{NNNN}
   - Create slug from Epic title
   - Use `templates/test-spec-template.md`
   - Link to parent Epic

   Include:
   - **Scope:** Stories covered, test types needed
   - **AC Coverage Matrix:** Map every Story AC to test cases (see step 4b)
   - **Test Cases:** One per AC minimum, with Given/When/Then steps
   - **Fixtures:** Embedded YAML test data
   - **Automation Status:** Initially all "Pending"

4b. **Build AC Coverage Matrix (MANDATORY)**

   Every Acceptance Criterion from covered Stories MUST have at least one test case:

   a) Extract all ACs from each Story in scope
   b) Create mapping table:
      ```markdown
      ### AC Coverage Matrix

      | Story | AC | Description | Test Cases | Status |
      |-------|-----|-------------|------------|--------|
      | US0001 | AC1 | Valid login | TC001, TC003 | Covered |
      | US0001 | AC2 | Invalid password | TC002 | Covered |
      | US0001 | AC3 | Rate limiting | - | **UNCOVERED** |
      ```

   c) Validate coverage:
      - Total ACs: N
      - Covered: M (ACs with at least one test case)
      - Uncovered: N-M (must be zero to mark Ready)

   d) **Blocking condition:** If any AC is uncovered, test-spec cannot be marked Ready
      - Flag uncovered ACs prominently
      - Generate test case stubs for uncovered ACs

5. **Write Files**
   - Write `sdlc-studio/test-specs/TS{NNNN}-{slug}.md`
   - Create/update `sdlc-studio/test-specs/_index.md`

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
   - Create TS files with discovered tests
   - Mark all as "Automated: Yes"
   - Link to actual test file paths
   - Note coverage gaps if epics exist

5. **Cross-Reference**
   - Match tests to stories if docstrings contain US IDs
   - Match tests to epics by naming convention
   - Flag untraced tests for review

6. **Write Files**
   - Write `sdlc-studio/test-specs/TS{NNNN}-{slug}.md`
   - Update `_index.md`

7. **Report**
   - Tests discovered and documented
   - Coverage vs existing stories
   - Gaps identified

---

## /sdlc-studio test-spec review - Step by Step

1. **Load Test Specs**
   - Read all from sdlc-studio/test-specs/

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
   - Verify test specs exist in sdlc-studio/test-specs/
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
      - See: `reference-test-e2e-guidelines.md` → Mocking Singletons

   d. **Factory Function Patterns (Dependency Injection)**
      - Look for `def get_*():` factory functions in route files
      - Identify `Depends(get_something)` patterns in route handlers
      - Mocking strategy: patch the factory function, not the class
      - See: `reference-test-e2e-guidelines.md` → Mocking Factory Functions

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

   | Detection File | Language | Framework | Support Level |
   |----------------|----------|-----------|---------------|
   | `pyproject.toml`, `setup.py` | Python | pytest | Full - templates and examples |
   | `package.json` + vitest | TypeScript | Vitest | Full - templates and examples |
   | `package.json` | TypeScript | Jest | Full - templates and examples |
   | `go.mod` | Go | testing | Basic - templates only |
   | `Cargo.toml` | Rust | cargo test | Detection only - no template |
   | `pom.xml` | Java | JUnit | Detection only - no template |
   | `build.gradle` | Java/Kotlin | JUnit | Detection only - no template |
   | `*.csproj` | C# | xUnit/NUnit | Detection only - no template |

   **Support levels:**
   - **Full:** Templates, examples, automatic generation
   - **Basic:** Templates exist but fewer examples
   - **Detection only:** Language detected but manual test guidance provided

   If Rust, Java, or C# detected, prompt user:
   ```
   Detected {language} project. Test automation templates not yet available.
   Would you like guidance for writing {framework} tests manually?
   ```

   If none found, use AskUserQuestion to ask user.

4. **Detect Framework**
   - Python: Check for pytest in dependencies (default: pytest)
   - TypeScript: Check for vitest vs jest in package.json
   - Go: Standard testing package
   - Rust: Standard cargo test

5. **Parse Test Specs**
   - Read TS file(s) to process
   - Extract test cases not yet automated
   - Extract fixtures/test data
   - Group by test type (unit, integration, api, e2e)

6. **Select Template**
   Based on language + test type:
   - `templates/automation/pytest.py.template`
   - `templates/automation/pytest-api.py.template`
   - `templates/automation/jest.ts.template`
   - `templates/automation/vitest.ts.template`
   - `templates/automation/go_test.go.template`

7. **Generate Test Code**
   For each test case:
   - Convert Given/When/Then to code structure
   - Generate fixture functions from spec data
   - Add docstring with TC ID and story reference
   - Include proper assertions
   - Apply best practices from `reference-test-best-practices.md`

8. **Determine Output Location**
   | Framework | Unit | Integration | API | E2E |
   |-----------|------|-------------|-----|-----|
   | pytest | tests/unit/ | tests/integration/ | tests/api/ | tests/e2e/ |
   | jest | __tests__/unit/ | __tests__/integration/ | __tests__/api/ | __tests__/e2e/ |
   | vitest | src/__tests__/ | src/__tests__/ | src/__tests__/ | tests/e2e/ |
   | go | same package | same package | same package | same package |

9. **Write Test Files**
   - Write test files to appropriate directories
   - Create directories if needed
   - Group tests by spec (one file per TS typically)

10. **Update Specs**
    - Mark test cases as "Automated: Yes"
    - Add file path to Automation Status table
    - Update _index.md coverage stats

11. **Run Generated Tests**
    - Execute the generated tests immediately with warnings as errors:
      ```bash
      pytest tests/path/to/new_tests.py -v -W error
      ```
    - Fix any failures AND warnings before proceeding
    - Common issues: mock paths, API status codes, schema mismatches

    > **Warning Policy:** `reference-test-best-practices.md` → Warning Policy

    - Only proceed to report when tests pass with ZERO warnings

12. **Report**
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

# Traceability Rules

## ID Naming Conventions

| Artefact | Format | Example |
|----------|--------|---------|
| Epic | EP{NNNN} | EP0001 |
| Story | US{NNNN} | US0001 |
| Test Spec | TS{NNNN} | TS0001 |
| Test Case | TC{NNNN} | TC0001 |

## Link Formats

From test artifacts, use relative paths:
- To PRD: `../../prd.md`
- To Epic: `../../epics/EP{NNNN}-{slug}.md`
- To Story: `../../stories/US{NNNN}-{slug}.md`
- To TSD: `../tsd.md`
- To Spec: `TS{NNNN}-{slug}.md`

## Coverage Matrix

Test Cases should cover all Acceptance Criteria:
- Each AC should have at least one TC
- Map TC to Story AC in test case metadata
- Track coverage in Spec files

---

# Error Handling

- No Test Strategy exists → prompt to run `/sdlc-studio tsd` first
- No Epics exist → prompt to run `/sdlc-studio epic` first
- No Test Specs exist → prompt to run `/sdlc-studio test-spec` first
- Unknown language → ask user to specify framework
- `--spec` flag with invalid ID → report error, list valid IDs
- No old artifacts for migration → report nothing to migrate

---

# See Also

- `reference-prd.md, reference-trd.md, reference-persona.md` - PRD, TRD, Persona workflows
- `reference-epic.md, reference-story.md, reference-bug.md` - Epic, Story, Bug workflows
- `reference-code.md` - Code plan, implement, review workflows
- `reference-philosophy.md` - Create vs Generate philosophy
- `reference-test-best-practices.md` - Test generation pitfalls and validation
- `reference-test-e2e-guidelines.md` - E2E and mocking patterns
