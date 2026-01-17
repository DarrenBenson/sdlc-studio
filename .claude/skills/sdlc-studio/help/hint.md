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
| 1 | No sdlc-studio/ | Bootstrap project | `init` |
| 2 | No PRD | Generate requirements | `prd generate` |
| 3 | No TRD | Generate technical requirements | `trd generate` |
| 4 | No personas | Create personas | `persona generate` |
| 5 | No epics | Generate epics | `epic` |
| 6 | No stories | Generate stories | `story` |
| 7 | Stories in Draft/Ready | Plan implementation | `code plan` |
| 8 | Stories in Planned | Execute plan | `code implement` |
| 9 | Stories in In Progress | Review code | `code review` |
| 10 | Stories in Review | Run tests | `test --story {id}` |
| 11 | All stories Done | Congratulate | - |

## Output Format

### Standard Output

```
## Next Step

**Action:** Generate user stories from epics
**Run:** `/sdlc-studio story`
**Why:** 3 epics ready, no stories yet
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
- `/sdlc-studio prd update` to check for new features
- `/sdlc-studio test-spec update` to sync test coverage
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

## Examples

### Early Pipeline

```
$ /sdlc-studio hint

## Next Step

**Action:** Generate PRD from codebase
**Run:** `/sdlc-studio prd generate`
**Why:** No PRD found, existing codebase detected
```

### Mid-Development

```
$ /sdlc-studio hint

## Next Step

**Action:** Plan implementation for next story
**Run:** `/sdlc-studio code plan`
**Why:** US0004, US0005 are Ready status
```

### With Blocker

```
$ /sdlc-studio hint

## Blocker

**Issue:** Unresolved open question in plan PL0002
**Fix:** Answer question in sdlc-studio/plans/PL0002-user-auth.md:45

---

## Next Step

**Action:** Implement planned story
**Run:** `/sdlc-studio code implement --plan PL0001`
**Why:** PL0001 has no blockers and is ready
```

## Comparison with Status

| Aspect | `hint` | `status` |
|--------|--------|----------|
| Output | Single next action | Full pipeline overview |
| Detail | Minimal, actionable | Comprehensive |
| Use case | "What do I do next?" | "What's the big picture?" |

## See Also

- `/sdlc-studio status` - Full pipeline overview
- `/sdlc-studio init` - Bootstrap entire pipeline
- `/sdlc-studio code plan` - Plan story implementation
