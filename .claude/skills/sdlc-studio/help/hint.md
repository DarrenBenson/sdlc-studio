<!--
Load: On /sdlc-studio hint or /sdlc-studio hint help
Dependencies: SKILL.md (always loaded first)
Related: None (standalone utility command)
-->

# /sdlc-studio hint - Next Step Suggestion

Get a single actionable next step based on current pipeline state.

## Usage

```
/sdlc-studio hint                    # Get next recommended action
```

## How It Works

Checks pipeline state in priority order and returns the first applicable action. Also detects blockers that may prevent progress.

## Priority Logic

| # | Condition | Suggested Action | Command |
|---|-----------|------------------|---------|
| 1 | No PRD + existing code | Extract PRD from codebase | `prd generate` |
| 2 | No PRD + no code | Create PRD interactively | `prd create` |
| 3 | No TRD + existing code | Extract TRD from codebase | `trd generate` |
| 4 | No TRD + no code | Create TRD interactively | `trd create` |
| 5 | No TSD | Create test strategy | `tsd` |
| 6 | No personas | Create personas | `persona` |
| 7 | No epics | Generate epics | `epic` |
| 8 | No stories | Generate stories | `story` |
| 9 | Paused workflow | Resume workflow | `story implement --from-phase N` |
| 10 | Starting new epic (no Done stories yet) | Review epic state and dependencies | `epic review --epic {id}` |
| 11 | Stories in Ready (multiple, epic reviewed) | Preview epic workflow | `epic plan --epic {id}` |
| 12 | Stories in Ready (single, epic reviewed) | Execute story workflow | `story implement --story {id}` (recommended) or `code plan --story {id}` (manual control) |
| 13 | Stories in Draft (epic reviewed) | Execute story workflow | `story implement --story {id}` (recommended) or `code plan --story {id}` (manual control) |
| 14 | Stories in Planned | Execute workflow | `story implement --story {id}` |
| 15 | Stories in In Progress | Continue workflow or verify | `code verify` |
| 16 | Stories in Review | Run tests | `code test --story {id}` |
| 17 | All stories Done | Review epic | `epic review` |

## Output Format

### Standard Output

```
## Next Step

**Action:** Generate user stories from epics
**Run:** `/sdlc-studio story`
**Why:** 3 epics ready, no stories yet
```

### Story Ready Output

```
## Next Step

**Action:** Execute story workflow
**Run:**
  /sdlc-studio story implement --story US0004   Full workflow (recommended)
  /sdlc-studio code plan --story US0004         Step-by-step (manual control)
**Why:** US0004 is Ready
```

### With Blocker

When an issue prevents smooth progress:

```
## Blocker

**Issue:** 2 unresolved open questions in plan PL0001
**Fix:** Edit sdlc-studio/plans/PL0001-*.md and check off resolved questions

---

## Next Step

**Action:** Implement planned story
**Run:** `/sdlc-studio code implement`
**Why:** US0003 is planned and ready (blocked by above)
```

### All Complete

```
## Pipeline Complete

All stories are done. Consider:
- `/sdlc-studio prd review` to check for new features
- `/sdlc-studio test-spec review` to sync test coverage
- Start a new epic or feature
```

## Blocker Detection

Checked before returning hint:

### Open Questions
- Unresolved open questions in PRD
- Unresolved open questions in implementation plans

### Dependencies
- Stories blocked by incomplete dependencies
- Test specs blocked by missing stories

### Quality Gates
- Stories in Review with failing tests
- Code check issues blocking merge

### Workflow State
- Paused story workflow (reports phase and error)
- Paused epic workflow (reports story and phase)
- Blocked stories in epic workflow

## Examples

### Early Pipeline

```
$ /sdlc-studio hint

## Next Step

**Action:** Generate PRD from codebase
**Run:** `/sdlc-studio prd generate`
**Why:** No PRD found, existing codebase detected
```

### Starting New Epic

```
$ /sdlc-studio hint

## Next Step

**Action:** Review epic state and dependencies
**Run:** `/sdlc-studio epic review --epic EP0005`
**Why:** EP0005 has no Done stories yet - check dependencies before starting
```

After epic review confirms dependencies are met, hint will suggest `story implement` or `code plan`.

### Mid-Development

```
$ /sdlc-studio hint

## Next Step

**Action:** Execute story workflow
**Run:**
  /sdlc-studio story implement --story US0004   Full workflow (recommended)
  /sdlc-studio code plan --story US0004         Step-by-step (manual control)
**Why:** US0004, US0005 are Ready - starting with US0004
```

### Multiple Ready Stories

```
$ /sdlc-studio hint

## Next Step

**Action:** Preview epic workflow for multiple Ready stories
**Run:** `/sdlc-studio epic plan --epic EP0002`
**Why:** 5 stories in EP0002 are Ready - consider batch execution
```

### Paused Workflow

```
$ /sdlc-studio hint

## Blocker

**Issue:** Story workflow paused at phase 5 (Verify)
**Story:** US0024 - Action Queue API
**Error:** 2 tests failed
**Fix:** Fix failing tests, then resume

---

## Next Step

**Action:** Resume paused workflow
**Run:** `/sdlc-studio story implement --story US0024 --from-phase 5`
**Why:** Workflow paused - needs resume after fix
```

### With Blocker

```
$ /sdlc-studio hint

## Blocker

**Issue:** Unresolved open question in plan PL0002
**Fix:** Answer question in sdlc-studio/plans/PL0002-user-auth.md:45

---

## Next Step

**Action:** Execute different story workflow
**Run:** `/sdlc-studio story implement --story US0003`
**Why:** US0003 has no blockers and is ready
```

## Comparison with Status

| Aspect | `hint` | `status` |
|--------|--------|----------|
| Output | Single next action | Full pipeline overview |
| Detail | Minimal, actionable | Comprehensive |
| Use case | "What do I do next?" | "What's the big picture?" |

## See Also

- `/sdlc-studio status` - Full pipeline overview
- `/sdlc-studio story implement` - Full workflow (recommended)
- `/sdlc-studio code plan` - Step-by-step (manual control)
