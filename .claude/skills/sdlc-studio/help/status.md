<!--
Load: On /sdlc-studio status or /sdlc-studio status help
Dependencies: SKILL.md (always loaded first)
Related: None (standalone utility command)
-->

# /sdlc-studio status

Shows the current state of the specification pipeline and recommends next steps.

## Usage

```bash
/sdlc-studio status              # Full status report
/sdlc-studio status --testing    # Testing pipeline only
/sdlc-studio status --workflows  # Workflow state only
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

3. **Workflow Progress**
   - Active story workflows (in progress or paused)
   - Active epic workflows (in progress or paused)
   - Completed workflows (history)

4. **Next Steps**
   - Recommended commands to run
   - Gaps that need attention
   - Resume commands for paused workflows

## Example Output

```
/sdlc-studio status

Requirements: 80%
  PRD         sdlc-studio/prd.md (14 features)
  Personas    sdlc-studio/personas.md (4 personas)
  Epics       3 epics (2 Done, 1 Draft)
  Stories     12 stories (8 Done, 4 pending)

Testing: 60%
  Strategy    sdlc-studio/tsd.md
  Specs       2/3 epics covered
  Automation  22/135 cases (16%)

Workflows:
  Active      1 story workflow (US0024 - phase 5/7)
  Paused      0
  Completed   7 story workflows, 1 epic workflow

Next steps:
  /sdlc-studio story implement --story US0024   Full workflow (recommended)
  /sdlc-studio code plan --story US0024         Step-by-step (manual control)

Other actions:
  /sdlc-studio test-spec --epic EP0003          Create test spec
  /sdlc-studio test-automation                   Generate 113 pending tests
```

### With Paused Workflow

```
/sdlc-studio status

Requirements: 80%
  ...

Workflows:
  Active      0
  Paused      1 story workflow (US0024 - phase 5, tests failed)
  Completed   6 story workflows

Next steps:
  /sdlc-studio story implement --story US0024 --from-phase 5   Resume paused workflow
```

### Workflows Only

```
/sdlc-studio status --workflows

Workflows:

Story Workflows:
  | Story | Status | Phase | Started | Notes |
  |-------|--------|-------|---------|-------|
  | US0024 | Paused | 5/7 | 10:30 | Tests failed |
  | US0023 | Done | 7/7 | 09:15 | Completed 09:52 |
  | US0022 | Done | 7/7 | Yesterday | Completed |

Epic Workflows:
  | Epic | Status | Stories | Started | Notes |
  |------|--------|---------|---------|-------|
  | EP0004 | In Progress | 2/5 | 09:15 | At US0024 |
```

## Detection Logic

The status command checks:

1. `sdlc-studio/prd.md` - PRD exists
2. `sdlc-studio/personas.md` - Personas defined
3. `sdlc-studio/epics/EP*.md` - Epic files and status
4. `sdlc-studio/stories/US*.md` - Story files and status
5. `sdlc-studio/tsd.md` - Test strategy exists
6. `sdlc-studio/test-specs/TS*.md` - Test specs and case counts
7. `tests/` directory - Actual test file count
8. `sdlc-studio/workflows/WF*.md` - Workflow files and status

## When to Use

- Start of a session to see what needs work
- After generating new artifacts to verify progress
- Before starting test automation to check coverage
- When onboarding to understand project state

## See Also

- `/sdlc-studio help` - Full command reference
- `/sdlc-studio hint` - Single actionable next step
- `/sdlc-studio story plan` - Preview story workflow
- `/sdlc-studio story implement` - Full workflow (recommended)
- `/sdlc-studio code plan` - Step-by-step (manual control)
- `/sdlc-studio epic plan` - Preview epic workflow
- `/sdlc-studio epic implement` - Execute epic workflow
- `/sdlc-studio test-spec` - Generate test specifications
- `/sdlc-studio test-automation` - Generate executable tests
