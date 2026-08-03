# US0616: sprint close and sprint stop refuse while the tree carries a repair to a batch unit

> **Status:** Ready
> **Delivers:** CR0527
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0204
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator closing a sprint
**I want** the close to refuse while a repair to one of its own batch units is sitting in the tree
**So that** the account the close is about to write cannot be invalidated by the commit that follows it

## Notes

Delivers criteria 1 and 2 of CR0527. The rule and its gate are one unit on purpose - LL0027: a
rule stated in a document with no gate behind it is a known-weak rule, and this repository's
recorded failure mode is rules that were read and then not followed.

The rule is that **a finding surfaced during a close is FILED and deferred to the next run,
never repaired inline.** Observed twice in one close of RUN-01KYZKY5 - `BG0496` was fixed during
the close and re-opened the ledger, then `BG0498` was fixed and re-opened it again. Each repair
invalidated the account written moments earlier, and every mechanical check passed each time.

The refusal must name what to do, not merely refuse: which unit the tree touches, and the two
ways out - commit it as batch work before the close begins, or file it and defer. A refusal that
leaves the operator to work out the remedy is the shape that gets bypassed.

## Acceptance Criteria

### AC1: a working tree carrying a repair to a batch unit refuses the close

- **Given** an open run whose batch names a unit, and a working tree with an uncommitted change
  to a file that unit declares in `Affects`
- **When** `sprint.py close` runs
- **Then** it refuses before writing anything, names the unit and the offending path, and states
  both remedies - commit it as batch work, or file it and defer to the next run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseFixedPointTests::test_close_refuses_while_the_tree_carries_a_batch_unit_repair

### AC2: `sprint stop` refuses on the same terms

- **Given** the same tree
- **When** `sprint.py stop` runs
- **Then** it refuses identically, because a stop writes the same account a close does - and the
  last run was STOPPED rather than closed, so a gate covering only `close` would leave the route
  actually taken ungated
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseFixedPointTests::test_stop_refuses_on_the_same_terms_as_close

### AC3: a clean tree, and a change outside the batch, both proceed

- **Given** an open run and either a clean tree, or a tree whose only changes are to files no
  batch unit declares
- **When** the close runs
- **Then** it proceeds - the gate refuses a repair to the work being certified, not any edit at
  all, and a guard that stopped every close over any dirty file would be switched off within a
  sprint
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseFixedPointTests::test_a_clean_tree_and_an_out_of_batch_change_both_proceed

### AC4: the doctrine states the rule and names the command that enforces it

- **Given** `reference-doctrine.md` and `reference-sprint.md`, which a consuming project inherits
- **When** the close-time rule is read
- **Then** both state that a finding surfaced during a close is filed and deferred, and name the
  command that refuses otherwise, so a project learns the rule and where it bites rather than
  being asked to remember it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseFixedPointTests::test_the_doctrine_states_the_rule_and_names_its_gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Groomed against CR0527 criteria 1-2: criteria authored, the doctrine leg folded in with `Affects` widened to the two references it touches, each Verify given a discriminating selector |
