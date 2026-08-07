# US0594: A unit whose ticked criteria the tree contradicts is reported outstanding at the close

> **Status:** Draft
> **Delivers:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0197
> **Points:** 5

## User Story

**As a** operator signing off a batch
**I want** a tick the tree contradicts reported outstanding
**So that** a false completion claim cannot pass the close that exists to catch it

## Acceptance Criteria

### AC1: a tick the tree contradicts is outstanding at the close

- **Given** a unit whose criteria are ticked while the surfaces they name are unchanged since the run's base ref
- **When** the checklist resolves
- **Then** the item is OUTSTANDING and names the unit and the criterion, because two units of one run were closed on exactly this and the checklist passed them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationTests::test_a_tick_the_tree_contradicts_is_outstanding

### AC2: a tick the tree supports passes

- **Given** a unit whose ticked criteria name surfaces the run did change
- **When** the checklist resolves
- **Then** the item passes - the control against an item that flags every ticked criterion
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationTests::test_a_supported_tick_passes

### AC3: an unrecorded base ref refuses rather than passing every tick

- **Given** a run whose base ref was never recorded, so `run_state.base_ref()` answers `""`
- **When** the checklist resolves
- **Then** the item is OUTSTANDING and says the base ref is missing, because a consumer that
  falls back to HEAD treats everything as changed, passes every tick, and reproduces the exact
  defect this story cites while staying green
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationTests::test_an_unrecorded_base_ref_refuses

## Test-plan notes

Written after a plan review rejected the first draft.

1. **Assert the message, not only the state.** `_resolve_item` converts ANY resolver exception
   into `NOT_RUN`/`UNANSWERED` with the traceback in `detail`, so a resolver that raises on all
   input is indistinguishable from a correct OUTSTANDING verdict to a state-only assertion.
   Each test asserts the unit id and the criterion heading appear in the row's `detail`.
2. **The seam is the changed-paths SOURCE, never the comparison.** The fixture patches a
   `_changed_paths(root, base_ref)`-shaped helper; the tick-versus-surface comparison stays
   inside the resolver under test. A seam drawn around the comparison patches both mutants away
   and leaves neither test able to die.
3. AC3 exists because `run_state.base_ref()` returns `""` when nothing was recorded and its own
   docstring mandates refusal rather than a fallback. Both of the first two fixtures record a
   base ref, so without AC3 a HEAD fallback passes every tick with both tests green.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | change sprint_report.py to emit a detail naming neither the unit nor the criterion, so the row cannot be acted on | a tick the tree contradicts is outstanding at the close |
| AC2 | delete the changed-surface consultation from sprint_report.py, so every ticked criterion is flagged | a tick the tree supports passes |
| AC3 | change sprint_report.py to fall back to HEAD when the recorded base ref is empty | an unrecorded base ref refuses rather than passing every tick |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
