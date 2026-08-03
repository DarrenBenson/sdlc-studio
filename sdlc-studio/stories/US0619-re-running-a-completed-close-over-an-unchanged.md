# US0619: re-running a completed close over an unchanged tree is a no-op that says so

> **Status:** Review
> **Delivers:** CR0527
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0204
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** an operator who is not sure whether the close finished
**I want** running it again over an unchanged tree to report the run already accounted for
**So that** the safe response to uncertainty is running the command, not avoiding it

## Notes

Delivers criterion 5 of CR0527. The close was run three times on RUN-01KYMJEM and repeatedly on
RUN-01KYZKY5, and the operator's reading was that the sprint was never being closed. It was:
each close was undone by the next repair, and each re-run re-derived an account that could
differ from the one before it.

This is the fixed point stated as an invariant: **the close is idempotent over an unchanged
tree.** Once that holds, re-running is free and the operator can check rather than guess - which
is the behaviour a close-time gate makes people want.

The tree, not `HEAD`, is what "unchanged" must mean. `BG0492` is the live instance of getting
that wrong in the suite verdict, and it is in this same batch: binding to a commit id makes an
unchanged working tree look changed after any commit, and a changed one look unchanged before
any.

## Acceptance Criteria

### AC1: a second close over an unchanged tree writes nothing and says why

- **Given** a run whose close completed, and a tree unchanged since
- **When** `sprint.py close` runs again
- **Then** it exits zero, reports the run already accounted for, and writes no artefact - no
  re-derived retro row, no re-stamped baseline, no second handoff
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseIdempotenceTests::test_a_second_close_over_an_unchanged_tree_writes_nothing
- **Verified:** yes (2026-08-03)

### AC2: "unchanged" is judged on the tree, not on HEAD

- **Given** a completed close, then a commit that changes nothing the close reads
- **When** the close runs again
- **Then** it still reports already-accounted - the comparison is over content, so a commit alone
  does not manufacture a difference, and an uncommitted edit is not hidden by there being no new
  commit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseIdempotenceTests::test_unchanged_is_judged_on_the_tree_not_on_head
- **Verified:** yes (2026-08-03)

### AC3: a genuinely changed tree re-runs the close

- **Given** a completed close, then a change to something the close accounts for
- **When** the close runs again
- **Then** it proceeds normally - the no-op is an idempotence guarantee, not a lock, and a close
  that refused to re-run after real work would be worse than the churn it replaces
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseIdempotenceTests::test_a_changed_tree_re_runs_the_close
- **Verified:** yes (2026-08-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Groomed against CR0527 criterion 5, with the tree-versus-HEAD distinction made a criterion of its own after BG0492 showed the cost of getting it wrong |
