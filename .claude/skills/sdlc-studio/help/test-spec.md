<!--
Load: On /sdlc-studio test-spec or /sdlc-studio test-spec help
Dependencies: SKILL.md (always loaded first)
Related: reference-testing.md (deep workflow), reference-test-best-practices.md, templates/test-spec-template.md
-->

# /sdlc-studio test-spec

Generates consolidated test specifications that combine test plans, suites, cases, and fixtures into a single document per Epic.

## Actions

| Action | Description |
|--------|-------------|
| (default) | Generate specs from epics/stories (greenfield) |
| generate | Reverse-engineer specs from existing tests (brownfield) |
| review | Review spec status, sync with codebase and test files |

## Usage

```bash
# Greenfield - generate from epics/stories
/sdlc-studio test-spec                    # All epics without specs
/sdlc-studio test-spec --epic EP0001      # Specific epic only

# Brownfield - reverse-engineer from existing tests
/sdlc-studio test-spec generate           # Discover from tests/ directory

# Maintenance
/sdlc-studio test-spec review             # Review and sync status
```

## Coverage Targets

| Level | Target |
|-------|--------|
| Unit | 90% line coverage |
| Integration | 85% line coverage |
| E2E | 100% feature coverage (one spec file per feature) |

**Why 90%?** AI-assisted development requires higher quality gates. This target has been proven achievable.

## Output

```
sdlc-studio/test-specs/
  _index.md                    # Spec registry
  TS0001-authentication.md     # Spec per epic
  TS0002-dashboard.md
```

## Spec Structure

Each TS file contains:

1. **Metadata** - Epic link, status, dates
2. **Scope** - Stories covered, test types needed
3. **Test Cases** - Individual cases with Given/When/Then
4. **Fixtures** - Shared test data in YAML
5. **Automation Status** - Which cases are automated

## Generate Mode (Brownfield)

When running `/sdlc-studio test-spec generate`, the skill:

1. Scans unified `tests/` directory for test files:
   - `tests/unit/backend/` - Python/Go unit tests
   - `tests/unit/frontend/` - TypeScript unit tests
   - `tests/integration/` - Cross-component tests
   - `tests/api/` - API endpoint tests
   - `tests/e2e/` - End-to-end browser tests
   - `tests/contracts/` - API contract tests
2. Parses test structure based on language:
   - Python: `class TestX`, `def test_*`, `@pytest.mark.*`
   - JavaScript/TypeScript: `describe()`, `it()`, `test()`
   - Go: `func Test*(t *testing.T)`
3. Extracts metadata from docstrings and comments
4. Groups tests by feature/component
5. Creates TS files with cases marked as "Automated: Yes"
6. Cross-references with epics/stories if they exist

## Prerequisites

- Test strategy should exist (`sdlc-studio/tsd.md`)
- Epics must exist in `sdlc-studio/epics/`
- Stories should exist for AC mapping (recommended)

## Options

| Option | Description |
|--------|-------------|
| `--epic EP0001` | Generate for specific epic only |
| `--force` | Overwrite existing spec files |

## Example Workflow

```bash
# 1. Ensure prerequisites exist
/sdlc-studio epic
/sdlc-studio story
/sdlc-studio tsd

# 2. Generate test specs
/sdlc-studio test-spec

# 3. Review and edit specs as needed

# 4. Generate automated tests
/sdlc-studio test-automation
```

## AC Coverage Matrix

Every test spec includes an AC Coverage Matrix mapping Story ACs to test cases:

```markdown
| Story | AC | Description | Test Cases | Status |
|-------|-----|-------------|------------|--------|
| US0001 | AC1 | Valid login | TC001, TC003 | Covered |
| US0001 | AC2 | Invalid password | TC002 | Covered |
| US0001 | AC3 | Rate limiting | - | **UNCOVERED** |
```

**Coverage requirements:**
- Every Story AC MUST have at least one test case
- Uncovered ACs are flagged prominently
- Test-spec cannot be marked Ready until all ACs are covered

**Coverage summary generated:**
- Total ACs: count from all covered stories
- Covered: ACs with at least one test case
- Uncovered: ACs without test cases (blocking)

## Ready Status Criteria

> **Source of truth:** `reference-decisions.md` → Test-Spec Ready

A test-spec can be marked **Ready** when:

| Criterion | Check |
|-----------|-------|
| AC coverage | All story ACs have at least one test case |
| Coverage matrix | Shows no UNCOVERED status |
| Test data | Fixtures defined for all test cases |
| No placeholders | No "verify result", "check response" assertions |
| Test types | Appropriate for story (unit for logic, API for endpoints) |

## E2E Feature Coverage

**Target:** One spec file per user-visible feature area.

| Feature Area | Spec File | Minimum Tests |
|--------------|-----------|---------------|
| Dashboard | `dashboard.spec.ts` | Happy path, error states, auth |
| Authentication | `auth.spec.ts` | Login, logout, session expiry |
| Settings | `settings.spec.ts` | View, edit, validation |

**Naming convention:** `[feature].spec.ts` (or language equivalent)

## Multi-Language Spec Examples

Test specs are language-agnostic. Here's how they map to different frameworks:

**Python (pytest):**
```markdown
### TC001: Valid login succeeds
```
→ `def test_valid_login_succeeds(self, client):`

**TypeScript (vitest/jest):**
```markdown
### TC001: Valid login succeeds
```
→ `it('TC001: valid login succeeds', async () => { ... });`

**Go:**
```markdown
### TC001: Valid login succeeds
```
→ `func TestValidLoginSucceeds(t *testing.T) { ... }`

## See Also

**REQUIRED for this workflow:**
- `reference-testing.md` - Test specification workflow details

**Recommended:**
- `/sdlc-studio story help` - User Stories (upstream)
- `/sdlc-studio test-automation help` - Test automation (downstream)

**Optional (deep dives):**
- `reference-test-best-practices.md` - Testing guidelines
- `reference-test-e2e-guidelines.md` - E2E patterns and guidelines
- `reference-decisions.md#test-spec-ready` - Ready status criteria
- `reference-outputs.md` - Output formats reference
