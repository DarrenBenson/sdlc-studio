# US0657: The budget records what shipped and reports the files sitting inside its tolerance

> **Status:** Ready
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_budgets.py, tools/tests/test_check_budgets.py, package.json
> **Epic:** EP0211
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The budget records what shipped and reports the files sitting inside its tolerance
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: `--record` MOVES a ceiling, appends its provenance, and rewrites no existing reason

- **Given** a fixture whose file has grown past its recorded ceiling, and whose ceiling carries
  a justification comment
- **When** `--record` runs
- **Then** the ceiling INTEGER changes to the measured size - asserted as a value, because a
  fixture already in step makes `--record` a no-op and the file is byte-identical under the
  honest implementation and the mutant alike - and every PRE-EXISTING reason byte survives, and
  a new provenance line is APPENDED naming the move.
- **And** appending rather than editing is the criterion, not a nicety: the existing reasons
  CONTAIN their numbers (`Raised 705 -> 755`, `Raised 724 -> 740`), so a tool that preserved
  them byte-identically while moving the ceiling would leave an argument that is false about the
  ceiling it justifies. The history accumulates; nothing already written is rewritten
- **Verify:** pytest tools/tests/test_check_budgets.py::RecordTests::test_record_moves_the_ceiling_appends_provenance_and_rewrites_no_reason

### AC2: `--drift` names the files inside the tolerance, and exits 0

- **Given** the SET of files within +5% of their ceiling - `reference-outputs.md` at 4.87%,
  `reference-decisions.md` at 4.83% and `reference-test-best-practices.md` at 4.67% among them
- **When** `--drift` runs
- **Then** every member of that set is named with its percentage and the command exits 0 -
  the SET, not one member, since a report naming only the worst offender passes a
  single-member assertion while hiding the rest. A file one line from
  failing a hard threshold is worth seeing before it fails, and a report that fails is a report
  that gets a bigger number rather than a smaller file
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_drift_names_the_files_inside_the_tolerance_and_exits_zero

### AC3: the hard threshold is unchanged, and a real breach still fails

- **Given** a file pushed past its ceiling outright
- **When** `check_budgets.py` runs with no flag
- **Then** it FAILS exactly as before. `--record` and `--drift` are reporting verbs added beside
  the gate, not a softening of it, and a test exercising only the new ones would let the old one
  be lost
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_the_hard_threshold_still_fails

### AC4: the three unbudgeted trees get a REPORTED total and NO threshold

- **Given** `help/` at 9,456 markdown lines, `best-practices/` at 4,881 and `templates/` at
  5,863 - counted over `*.md` only, which is stated because `templates/` is 7,412 over all files
  and a total whose filter is unstated is a number nobody can reproduce - none
  of them walked by `check_budgets.py` today, which reads only `SKILL.md` and `reference-*.md`
- **When** the budgets are reported
- **Then** each carries a total, and NO threshold exists for any of them - both directions
  asserted, because a test checking only that a total appears passes on an implementation that
  also added a ceiling. A hard budget set on day one over a tree nobody has been pruning fails
  on day one and is waived on day two, and a waived gate is worse than a reported number because
  it looks like a gate
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_the_unbudgeted_trees_are_reported_and_not_gated

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | leave the ceiling integer untouched while reporting success | `--record` MOVES a ceiling |
| AC1 | rewrite the whole budget entry, reason comment included | `--record` MOVES a ceiling |
| AC1 | edit the existing reason in place rather than appending a new provenance line | `--record` MOVES a ceiling |
| AC2 | exit non-zero when `--drift` finds a file inside the tolerance | `--drift` names and exits 0 |
| AC3 | make the hard threshold advisory now that `--drift` reports | the hard threshold is unchanged |
| AC4 | give the three unbudgeted trees a hard ceiling from their current size | the unbudgeted trees are REPORTED and not gated |
| AC4 | report the totals from a constant rather than by walking the trees | the unbudgeted trees are REPORTED and not gated |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-08 | sdlc-studio | AC4 moved to US0658, from the plan-time engineering seat's finding. `check_budgets.py` is a BLOCKING pre-commit lane, so a requirement that `reference-sprint.md`'s justification have a Reading Guide - landing here, one story before US0658 generates it - leaves main red between the two commits. The requirement belongs with the story that makes it true |
| 2026-08-08 | sdlc-studio | Plan review round 1 REJECTed AC1 as a vacuous pass - with a fixture already in step, `--record` is a no-op and the file is byte-identical under both the honest implementation and the mutant, and nothing asserted that an integer moved. It does now. The reviewer also found the real tension underneath: the reason comments CONTAIN their numbers, so preserving them byte-identically while the ceiling moves leaves an argument false about its own ceiling - `--record` APPENDS a provenance line instead, so the history accumulates and nothing written is rewritten. AC4's totals were wrong (help is 9,456 and templates 5,863) and `check_budgets.py` does not walk those trees at all today |
| 2026-08-08 | sdlc-studio | Plan review round 2 APPROVEd, ruling all three round-1 findings CLOSED. Its two minors are folded in: AC2 asserts the SET inside the tolerance rather than one member, and AC4 states that the tree totals count `*.md` only, since `templates/` is 7,412 over all files |
