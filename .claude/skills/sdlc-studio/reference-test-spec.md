# SDLC Studio Reference - Test Specifications

Detailed workflows for test specification creation and management.

<!-- Load when: generating test specs, reviewing test coverage -->

---

## /sdlc-studio test-spec - Step by Step (Greenfield)

1. **Check Prerequisites**
   - Verify Test Strategy exists
   - Verify Epics exist in sdlc-studio/epics/
   - Create sdlc-studio/test-specs/ if needed
   - Scan for existing specs to determine next ID
   - **ID Collision Check:** Glob for `sdlc-studio/test-specs/TS{NNNN}*.md` with the proposed ID. If file(s) already exist with that prefix, increment to the next available ID. Log a warning if a collision was avoided.

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
   - Use `templates/core/test-spec.md`
   - Link to parent Epic

   Include:
   - **Scope:** Stories covered, test types needed
   - **AC Coverage Matrix:** Map every Story AC to test cases (see step 4b)
   - **Test Cases:** One per AC minimum, with Given/When/Then steps
   - **Fixtures:** Embedded YAML test data
   - **Automation Status:** Initially all "Pending"

5. **Build AC Coverage Matrix (MANDATORY)**

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

6. **Write Files**
   - Write `sdlc-studio/test-specs/TS{NNNN}-{slug}.md`
   - Create/update `sdlc-studio/test-specs/_index.md`

7. **Report**
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

## TC Numbering {#tc-numbering}

Test Case IDs are **globally sequential** across all test specs. They do NOT reset per spec.

### Finding the Next TC Number

Before creating a new test spec, find the last assigned TC number:

```bash
# Search all test specs for highest TC number
grep -h "^### TC" sdlc-studio/test-specs/TS*.md | sort -t'C' -k2 -n | tail -1
```

Or check the most recently created test spec file and find its last TC.

### Assigning TC Ranges

When planning multiple test specs (e.g., for an epic), assign contiguous ranges:

| Test Spec | Story | Test Cases | TC Range |
|-----------|-------|------------|----------|
| TS0017 | US0017 | 13 | TC0187-TC0199 |
| TS0018 | US0018 | 8 | TC0200-TC0207 |

This prevents ID collisions when specs are created in parallel.

---

## Traceability Rules

### ID Naming Conventions

| Artefact | Format | Example |
|----------|--------|---------|
| Epic | EP{NNNN} | EP0001 |
| Story | US{NNNN} | US0001 |
| Test Spec | TS{NNNN} | TS0001 |
| Test Case | TC{NNNN} | TC0001 (globally sequential) |

### Link Formats

From test artifacts, use relative paths:

- To PRD: `../../prd.md`
- To Epic: `../../epics/EP{NNNN}-{slug}.md`
- To Story: `../../stories/US{NNNN}-{slug}.md`
- To TSD: `../tsd.md`
- To Spec: `TS{NNNN}-{slug}.md`

### Coverage Matrix

Test Cases should cover all Acceptance Criteria:

- Each AC should have at least one TC
- Map TC to Story AC in test case metadata
- Track coverage in Spec files

## Epic-Scoped Test Spec Coverage {#epic-scoped-coverage}

Some test specs cover an entire epic rather than a single story. These require special handling for coverage checks and cascade behaviour.

### Scope Identification

| Scope | Frontmatter | Example |
|-------|-------------|---------|
| Story-level | `story: US0024` | TS0024 covers US0024 only |
| Epic-level | `epic: EP0006` (no `story:` field, or `story:` lists multiple) | TS0253 covers all stories in EP0006 |

**Detection rule:** A test spec is epic-scoped when it references an epic but either omits the `story:` field or lists multiple stories in its scope section.

### Coverage Resolution

When checking whether a story has test coverage:

1. Check for a **direct story-level spec** (`story: US0024`)
2. If none found, check for an **epic-scoped spec** that covers the story's parent epic
3. A story is "covered" if either check succeeds

This prevents false "missing test spec" findings for stories covered by an epic-wide spec.

### Cascade Implications

Epic-scoped test specs follow different cascade rules:

- **Story-level specs:** Cascade immediately when their single linked story reaches terminal status.
- **Epic-scoped specs:** Only cascade when **ALL** stories covered by the spec are terminal. If some stories are still active, the spec remains in its current status.

**Example:** TS0253 covers EP0006 (stories US0024-US0027). If US0025 is marked Superseded but US0024, US0026, US0027 are still In Progress, TS0253 remains active. Only when all four stories reach terminal status does TS0253 cascade.

---

## See Also

- `reference-tsd.md` - Test strategy and status dashboard workflows
- `reference-test-automation.md` - Test automation and environment workflows
- `reference-test-best-practices.md` - Test generation pitfalls and validation
- `reference-test-e2e-guidelines.md` - E2E and mocking patterns
- `help/test-spec.md` - Test spec command quick reference
