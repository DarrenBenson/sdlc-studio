# US0655: The coverage number surfaces in the gate, the lint aggregate and the close report

> **Status:** Ready
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, package.json, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/help/gate.md, tools/tests/test_check_spec_claims.py
> **Epic:** EP0211
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The coverage number surfaces in the gate, the lint aggregate and the close report
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the gate carries a non-blocking `doc-surface` lane, distinguishable from `doc-coverage`

- **Given** `gate.py`, which ALREADY carries a blocking `doc-coverage` lane reporting
  "N undocumented" - and that lane counts SCRIPTS without a `reference-scripts.md` entry, which
  is at 71 of 71 today
- **When** the gate runs over a tree with undocumented VERBS
- **Then** a `doc-surface` lane reports "N of M verbs carry no invocable form", wording that
  cannot be read as the other lane's number, and the gate's exit code is unchanged. Two lanes
  both saying "undocumented" about different granularities is two numbers a reader has to
  reconcile with nothing telling them they measure different things
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DocSurfaceLaneTests::test_the_lane_reports_verbs_distinguishably_and_does_not_change_the_exit_code

### AC2: the `lint` CHAIN runs `lint:disclosure`, which today it does not

- **Given** `package.json`, where `lint:disclosure` exists as a script key and the `lint` chain
  does not call it - so a checker with 28 advisory findings is one line from being read and is
  not read
- **When** the aggregate is inspected
- **Then** the `lint` chain's own command string contains `lint:disclosure`, and the aggregate
  exits 0. Asserting the KEY exists is green today with nothing changed, which is a criterion
  that cannot fail
- **Verify:** pytest tools/tests/test_check_spec_claims.py::LintAggregateTests::test_the_lint_chain_calls_disclosure

### AC3: the close report carries one row, derived not typed

- **Given** a close
- **When** the report is composed
- **Then** it carries one row naming the verb counts, derived by calling the coverage
  measurement rather than by reading a number somebody wrote down
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::DocSurfaceRowTests::test_the_close_row_is_derived_from_the_measurement

### AC4: the gate lane and the close row MOVE when the DEFINING module is patched

- **Given** the gate lane and the close row - the two readers that consume the coverage
  measurement; the lint aggregate is deliberately NOT among them, because it shells out to
  `disclosure.py`, a different checker with an unrelated count, and could never quote this one
- **When** the measurement function is patched IN ITS DEFINING MODULE to an implausible sentinel
  (4242, a value no real tree produces)
- **Then** both readers quote 4242. The patch is on the defining module and each reader must
  call through it rather than binding the name at import, or the mutant that gives the gate lane
  its own re-derivation survives - a copy patched under the same name moves with it. Asserting
  the two readers AGREE proves nothing either: two correct readers over one tree agree by
  construction
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DocSurfaceLaneTests::test_both_readers_move_when_the_defining_module_is_patched

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | make the `doc-surface` lane fail the gate when the count is non-zero | the gate carries a non-blocking lane |
| AC1 | word the lane's detail as "N undocumented", identical to the `doc-coverage` lane | the gate carries a non-blocking lane |
| AC2 | leave `lint:disclosure` defined as a key but absent from the `lint` chain | the `lint` CHAIN runs `lint:disclosure` |
| AC3 | render the close row from a constant rather than from the measurement | the close report carries one row |
| AC4 | give the gate lane its own re-derivation of the count | both readers MOVE when the defining module is patched |
| AC4 | have each reader bind the measurement by `from ... import` at load time | both readers MOVE when the defining module is patched |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-08 | sdlc-studio | AC4 rewritten from the plan-time qa seat's finding: as written it asserted three readers AGREE, which three correct readers do by construction, so its own mutant survived. It patches the shared routine now and requires each reader to move with it |
| 2026-08-08 | sdlc-studio | Plan review round 1 REJECTed. AC4 named THREE readers and one of them is not executable: the lint lane shells out to `disclosure.py`, a different checker with an unrelated count, so it could never quote a patched coverage value - it is scoped to the two readers that can, with the reason stated. The patch site is named as the DEFINING module, since patching each reader's own attribute leaves the re-derivation mutant alive. AC1 gains the finding that `gate.py` ALREADY reports `N undocumented` at script granularity, so the new lane must be worded so a reader cannot conflate them. AC2 asserts the `lint` CHAIN, not the key, which exists today |
