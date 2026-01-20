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

1. Scans `tests/` directory for test files
2. Parses test structure based on language:
   - Python: `class TestX`, `def test_*`, `@pytest.mark.*`
   - JavaScript/TypeScript: `describe()`, `it()`, `test()`
   - Go: `func Test*(t *testing.T)`
3. Extracts metadata from docstrings and comments
4. Groups tests by feature/file
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

## See Also

- `/sdlc-studio tsd` - Define testing approach first
- `/sdlc-studio test-automation` - Generate executable tests from specs
- `/sdlc-studio status` - Check overall pipeline progress
- `reference-testing.md` - Detailed test spec workflows
- `reference-decisions.md` - Ready criteria, validation checkpoints
- `reference-test-best-practices.md` - Test writing guidelines
