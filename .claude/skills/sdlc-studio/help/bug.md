<!--
Load: On /sdlc-studio bug or /sdlc-studio bug help
Dependencies: SKILL.md (always loaded first)
Related: reference-bug.md (deep workflow), templates/bug-template.md
-->

# /sdlc-studio bug - Bug Tracking

## Quick Reference

```
/sdlc-studio bug                        # Create new bug (interactive)
/sdlc-studio bug list                   # List all bugs
/sdlc-studio bug list --status open     # List open bugs
/sdlc-studio bug list --severity critical  # List critical bugs
/sdlc-studio bug list --epic EP0001     # List bugs for epic
/sdlc-studio bug fix --bug BG0001       # Start fixing a bug
/sdlc-studio bug verify --bug BG0001    # Verify bug fix
/sdlc-studio bug close --bug BG0001     # Close a bug
/sdlc-studio bug reopen --bug BG0001    # Reopen a closed bug
```

## Prerequisites

- For linking: Stories should exist in `sdlc-studio/stories/`
- For test integration: Test specs should exist in `sdlc-studio/test-specs/`

## Actions

### (default)

Create a new bug report with full traceability.

**What happens:**
1. Prompts for bug details (title, description, steps)
2. Determines severity and priority
3. Auto-detects affected stories/epics from description
4. Creates bug file using `templates/bug-template.md`
5. Updates `sdlc-studio/bugs/_index.md`
6. Optionally adds "Known Issue" note to affected story

**Interactive prompts:**
- Title (short description)
- Summary (detailed description)
- Reproduction steps
- Expected vs actual behaviour
- Severity (Critical/High/Medium/Low)
- Priority (P1/P2/P3/P4)
- Affected area (component, story, epic)

### list

List bugs with optional filtering.

**Filters:**
| Filter | Description |
|--------|-------------|
| `--status open` | Open bugs only |
| `--status fixed` | Fixed, awaiting verification |
| `--severity critical` | Critical severity only |
| `--priority P1` | P1 priority only |
| `--epic EP0001` | Bugs linked to epic |
| `--story US0001` | Bugs linked to story |
| `--assignee name` | Assigned to person |

**Output:**
```
## Open Bugs (12)

| ID | Title | Severity | Priority | Age |
|----|-------|----------|----------|-----|
| BG0003 | Player falls through floor | Critical | P1 | 2d |
| BG0007 | Score not saved | High | P2 | 5d |
```

### fix

Start fixing a bug with proper documentation.

**What happens:**
1. Reads bug details
2. Updates bug status: Open → In Progress
3. Identifies linked stories/epics
4. Explores codebase for relevant code
5. Creates fix plan (similar to code plan)
6. Prompts to add regression test
7. Updates story with fix reference

**Workflow:**
```
/sdlc-studio bug fix --bug BG0001
```

Outputs:
- Root cause analysis
- Suggested fix approach
- Files to modify
- Test cases to add

After implementing:
```
/sdlc-studio bug fix --bug BG0001 --complete
```

Updates:
- Bug status → Fixed
- Fills in "Fix Description" section
- Adds test case references
- Updates story revision history

### verify

Verify and close a bug fix (quick happy path).

**What happens:**
1. Reads bug and fix details
2. Runs associated tests
3. Checks fix addresses root cause
4. Updates status: Fixed → Closed (verified)
5. Updates verification section
6. Removes from "Open Bugs" in story (if linked)

**Requirements:**
- Bug must be in "Fixed" status
- Tests must pass

### close

Close a bug with reason selection.

**What happens:**
1. Prompts for close reason:
   - **Verified** - Fix confirmed working
   - **Rejected/Won't Fix** - Not a bug or won't address
2. Updates status → Closed
3. Records close reason
4. Updates metrics in index
5. Removes from "Open Bugs" in story (if linked)

**Note:** Use `bug verify` for the common case of closing a verified fix.

### reopen

Reopen a closed bug (regression found).

**What happens:**
1. Updates status: Closed → Open
2. Adds note about regression
3. Links to related test failure (if applicable)

## Severity Guide

| Severity | Description | Response Time |
|----------|-------------|---------------|
| Critical | System unusable, data loss, security issue | < 24 hours |
| High | Major feature broken, no workaround | < 3 days |
| Medium | Feature impaired, workaround exists | < 1 week |
| Low | Minor issue, cosmetic, edge case | Next release |

## Priority Guide

| Priority | Description |
|----------|-------------|
| P1 | Fix immediately, blocks release |
| P2 | Fix this sprint |
| P3 | Fix this release |
| P4 | Fix when possible |

## Output

### Bug Report

**Location:** `sdlc-studio/bugs/BG{NNNN}-{slug}.md`

**Sections:**
- Summary and metadata
- Affected area (epic, story, component)
- Environment details
- Reproduction steps
- Expected vs actual behaviour
- Root cause (filled when fixing)
- Fix description (filled when fixing)
- Tests added (filled when fixing)
- Verification checklist

### Bug Index

**Location:** `sdlc-studio/bugs/_index.md`

**Contents:**
- Summary counts by status
- Counts by severity
- All bugs table
- Open bugs grouped by severity
- Recently fixed bugs
- Bugs by epic

## Integration

### Story Integration

When a bug is linked to a story:
- Story gets "Known Issues" section with bug reference
- When fixed, story revision history is updated
- Bug count shown in story metadata

### Test Integration

When fixing a bug:
- Prompt to add regression test
- Test case added to relevant test spec
- Test ID recorded in bug report
- `/sdlc-studio code test --bug BG0001` runs regression tests

### Status Integration

`/sdlc-studio status` shows:
```
### Bugs
- Critical: 1 open
- High: 3 open, 2 in progress
- Total: 12 open, 5 fixed, 23 closed
```

`/sdlc-studio hint` suggests:
```
## Next Step
**Action:** Fix critical bug
**Run:** `/sdlc-studio bug fix --bug BG0003`
**Why:** Critical bug open for 2 days
```

## Examples

```
# Create a bug interactively
/sdlc-studio bug

# List all open bugs
/sdlc-studio bug list --status open

# List critical bugs
/sdlc-studio bug list --severity critical

# List bugs for an epic
/sdlc-studio bug list --epic EP0002

# Start fixing a bug
/sdlc-studio bug fix --bug BG0003

# Mark fix complete
/sdlc-studio bug fix --bug BG0003 --complete

# Verify the fix
/sdlc-studio bug verify --bug BG0003

# Close the bug
/sdlc-studio bug close --bug BG0003

# Reopen if regression found
/sdlc-studio bug reopen --bug BG0003
```

## Bug Lifecycle

```
         ┌──────────────────────────────────────┐
         │                                      │
         ▼                                      │
      Open ──[fix]──▶ In Progress ──[complete]──▶ Fixed
         │                                        │
         │                                   [verify]
         │                                        │
         │                                        ▼
         ├──[close: won't fix]────────────────▶ Closed
         │                                        │
         └────────────────[reopen]────────────────┘
```

**Quick paths:**
- `bug verify` = verify fix + close (most common)
- `bug close` = prompt for reason (verified/rejected/won't fix)

## See Also

- `/sdlc-studio story help` - Stories affected by bugs
- `/sdlc-studio code help` - Implementation workflow (includes test command)
- `reference-bug.md` - Detailed bug workflow
