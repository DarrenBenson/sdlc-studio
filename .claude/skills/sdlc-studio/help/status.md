# /sdlc-studio status

Shows the current state of the specification pipeline and recommends next steps.

## Usage

```bash
/sdlc-studio status              # Full status report
/sdlc-studio status --testing    # Testing pipeline only
/sdlc-studio status --brief      # One-line summary
```

## Output

The status command displays:

1. **Requirements Pipeline Progress**
   - PRD existence and feature count
   - Personas defined
   - Epics generated and their status
   - Stories generated and their status

2. **Testing Pipeline Progress**
   - Test strategy defined
   - Test specs generated per epic
   - Automation coverage percentage

3. **Next Steps**
   - Recommended commands to run
   - Gaps that need attention

## Example Output

```
/sdlc-studio status

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
  /sdlc-studio story --epic EP0003      Complete stories for Reports
  /sdlc-studio test-spec --epic EP0003  Create test spec
  /sdlc-studio test-automation          Generate 113 pending tests
```

## Detection Logic

The status command checks:

1. `sdlc-studio/prd.md` - PRD exists
2. `sdlc-studio/personas.md` - Personas defined
3. `sdlc-studio/epics/EP*.md` - Epic files and status
4. `sdlc-studio/stories/US*.md` - Story files and status
5. `sdlc-studio/testing/strategy.md` - Test strategy exists
6. `sdlc-studio/testing/specs/TSP*.md` - Test specs and case counts
7. `tests/` directory - Actual test file count

## When to Use

- Start of a session to see what needs work
- After generating new artifacts to verify progress
- Before starting test automation to check coverage
- When onboarding to understand project state

## See Also

- `/sdlc-studio help` - Full command reference
- `/sdlc-studio test-spec` - Generate test specifications
- `/sdlc-studio test-automation` - Generate executable tests
