# /sdlc-studio test-spec

Generates consolidated test specifications that combine test plans, suites, cases, and fixtures into a single document per Epic.

## Actions

| Action | Description |
|--------|-------------|
| (default) | Generate specs from epics/stories (greenfield) |
| generate | Reverse-engineer specs from existing tests (brownfield) |
| update | Sync spec status with codebase and test files |

## Usage

```bash
# Greenfield - generate from epics/stories
/sdlc-studio test-spec                    # All epics without specs
/sdlc-studio test-spec --epic EP0001      # Specific epic only

# Brownfield - reverse-engineer from existing tests
/sdlc-studio test-spec generate           # Discover from tests/ directory

# Maintenance
/sdlc-studio test-spec update             # Sync automation status
```

## Output

```
sdlc-studio/testing/specs/
  _index.md                    # Spec registry
  TSP0001-authentication.md    # Spec per epic
  TSP0002-dashboard.md
```

## Spec Structure

Each TSP file contains:

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
5. Creates TSP files with cases marked as "Automated: Yes"
6. Cross-references with epics/stories if they exist

## Prerequisites

- Test strategy should exist (`sdlc-studio/testing/strategy.md`)
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
/sdlc-studio test-strategy

# 2. Generate test specs
/sdlc-studio test-spec

# 3. Review and edit specs as needed

# 4. Generate automated tests
/sdlc-studio test-automation
```

## See Also

- `/sdlc-studio test-strategy` - Define testing approach first
- `/sdlc-studio test-automation` - Generate executable tests from specs
- `/sdlc-studio status` - Check overall pipeline progress
