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

### AC1: `--record` rewrites ceilings and leaves every reason byte-identical

- **Given** `check_budgets.py`, whose ceilings each carry a justification comment
- **When** `--record` runs
- **Then** only the ceiling INTEGERS change and every reason comment is byte-identical
  afterwards. The reasons are the argument for the number, and a tool that rewrites both loses
  the argument the moment the number moves - which is how `reference-sprint.md` came to sit at
  827 lines on a justification asserting twice that its Reading Guide anchors partial reads,
  while it has none
- **Verify:** pytest tools/tests/test_check_budgets.py::RecordTests::test_record_rewrites_ceilings_and_never_a_reason

### AC2: `--drift` names the files inside the tolerance, and exits 0

- **Given** the eight files within +5% of their ceiling, `reference-outputs.md` among them at
  4.9% over
- **When** `--drift` runs
- **Then** each is named with its percentage and the command exits 0. A file one line from
  failing a hard threshold is worth seeing before it fails, and a report that fails is a report
  that gets a bigger number rather than a smaller file
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_drift_names_the_files_inside_the_tolerance_and_exits_zero

### AC3: the hard threshold is unchanged, and a real breach still fails

- **Given** a file pushed past its ceiling outright
- **When** `check_budgets.py` runs with no flag
- **Then** it FAILS exactly as before. `--record` and `--drift` are reporting verbs added beside
  the gate, not a softening of it, and a test that only exercised the new ones would let the old
  one be lost
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_the_hard_threshold_still_fails

### AC4: a ceiling justification that names a Reading Guide must have one

- **Given** `reference-sprint.md`'s justification, which asserts a Reading Guide twice over a
  file that has none
- **When** the budgets are checked
- **Then** a justification naming a Reading Guide is required to have one in the file it
  justifies. The premise is fixed by MAKING IT TRUE - US0658 generates the guide - rather than
  by deleting the sentence, because the sentence is right about what the file needs
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_a_justification_naming_a_reading_guide_must_have_one

### AC5: the three unbudgeted trees get a REPORTED total, not a hard budget

- **Given** `help/` at 9,447 lines, `best-practices/` at 4,881 and `templates/` at 5,860, none
  of them budgeted
- **When** the budgets are reported
- **Then** each carries a total and none carries a threshold. A hard budget set on day one over
  a tree nobody has been pruning fails on day one and is waived on day two, and a waived gate is
  worse than a reported number because it looks like a gate
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_the_unbudgeted_trees_are_reported_not_gated

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | rewrite the whole budget entry, reason comment included | `--record` rewrites ceilings only |
| AC2 | exit non-zero when `--drift` finds a file inside the tolerance | `--drift` names and exits 0 |
| AC3 | make the hard threshold advisory now that `--drift` reports | the hard threshold is unchanged |
| AC4 | accept a justification that names a Reading Guide the file does not have | a justification naming a guide must have one |
| AC5 | give the three unbudgeted trees a hard ceiling from their current size | the unbudgeted trees are REPORTED |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
