# BG0651: A later commit that changes a target file empties an earlier unit's mutation evidence silently, and nothing refuses until the close dry-run

> **Status:** Open
> **Verification depth:** functional [[derived: criteria 3; plan rows 6; EVIDENCE ABSENT - the mutation ledger holds no entry for this unit, which is not the same fact as nought killed; NOT RUN 6 (AC1 row 0, AC1 row 1, AC1 row 2, AC2 row 0, AC2 row 1, AC3 row 0); entry point 0 of 3 criteria through the shipped CLI, 0 in-process; 3 undetermined (the named node could not be isolated) | fp f03ce8755a00 ]]
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/tests/test_check_spec_claims.py, AGENTS.md
> **Evidence:** RUN-01M1NS3C close dry-run 2026-09-04: `done-gate: BG0641 -> Fixed blocked: 19 planned mutant(s) unaccounted for` and `BG0643: 2 planned mutant(s) unaccounted for`, both units Fixed with 30/30 and 12/12 killed at transition. Ruled a Medium bug by the operator on 2026-09-06.
> **Created:** 2026-09-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`mutation.py register` hashes the target's bytes, and any later edit to that file drops every registered row for it (LL0053). In RUN-01M1NS3C this happened four times in one day: BG0642's edit to `.githooks/pre-push` emptied BG0641's thirty rows, BG0603's edit to `verify_ac.py` emptied two of BG0643's, and the round-two repairs emptied BG0644's and BG0647's own rows. Each unit was Fixed with `from-plan` reading every row killed; the drop surfaced only when `sprint close --dry-run` re-checked the done-gate hours later. No commit-time lane compares the ledger's live rows against the files a commit changes.

## Steps to Reproduce

1. Register a unit's mutants against a file and transition it to Fixed.
2. In a later unit, edit that file and commit.
3. `mutation.py run --story <first unit> --from-plan`: every row reads not-run; `transition set <first unit> Fixed --dry-run` is blocked; nothing at the second commit said so.

## Proposed Fix

A pre-commit lane (in `gate.py`'s block, beside derived-depth) that lists every Fixed or Done unit whose live ledger rows target a file the commit changes, and refuses with the units and their re-measure command; or re-measures automatically when the unit's runner is recorded. Decide at grooming which; refusing is the smaller change.

## Acceptance Criteria

- [ ] **AC1** Given a Fixed unit whose registered mutant rows target a file, when a commit stages a change to that file, then the pre-commit gate's `evidence-drift` lane refuses, naming the unit, the file and the re-measure command (`mutation.py run --story <id> --from-plan`), and a commit staging no registered target passes the lane - the control
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::EvidenceDriftTests::test_a_commit_that_rewrites_a_registered_target_is_refused_with_the_unit_named
- [ ] **AC2** Given the same unit, when the changed file's rows are re-registered against the new bytes before the commit, then the lane passes, and a unit in `Open` or `In Progress` whose rows are dropped is reported, not refused - its evidence is still being made
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::EvidenceDriftTests::test_re_registered_rows_pass_and_an_open_unit_is_reported_not_refused
- [ ] **AC3** Given the AGENTS.md lane roster, when `tools/tests/test_check_spec_claims.py` runs, then `evidence-drift` is named in the roster with its blocking status, so the lane is not one nobody wrote down (LL0013)
  - **Verify:** pytest tools/tests/test_check_spec_claims.py::GateLaneTests::test_the_lane_roster_names_evidence_drift_and_its_blocking_status

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `gate.py`, compare the ledger's rows against the working tree instead of the staged files, so an unstaged edit refuses and a staged one passes | Given a Fixed unit whose registered mutant rows target a file, when a commit stages a change to that file, then the pre-commit gate's `evidence-drift` lane refuses, naming the unit, the file and the re-measure command (`mutation.py run --story <id> --from-plan`), and a commit staging no registered target passes the lane - the control |
| AC1 | in `gate.py`, name the unit but not the re-measure command | Given a Fixed unit whose registered mutant rows target a file, when a commit stages a change to that file, then the pre-commit gate's `evidence-drift` lane refuses, naming the unit, the file and the re-measure command (`mutation.py run --story <id> --from-plan`), and a commit staging no registered target passes the lane - the control |
| AC1 | in `gate.py`, refuse whenever any unit has rows on the file, ignoring whether the commit changes it | Given a Fixed unit whose registered mutant rows target a file, when a commit stages a change to that file, then the pre-commit gate's `evidence-drift` lane refuses, naming the unit, the file and the re-measure command (`mutation.py run --story <id> --from-plan`), and a commit staging no registered target passes the lane - the control |
| AC2 | in `gate.py`, refuse an `In Progress` unit's dropped rows as if it were Fixed | Given the same unit, when the changed file's rows are re-registered against the new bytes before the commit, then the lane passes, and a unit in `Open` or `In Progress` whose rows are dropped is reported, not refused - its evidence is still being made |
| AC2 | in `gate.py`, read the rows' recorded hash but never re-hash the staged bytes, so re-registered rows still refuse | Given the same unit, when the changed file's rows are re-registered against the new bytes before the commit, then the lane passes, and a unit in `Open` or `In Progress` whose rows are dropped is reported, not refused - its evidence is still being made |
| AC3 | in `AGENTS.md`, leave the roster without the lane | Given the AGENTS.md lane roster, when `tools/tests/test_check_spec_claims.py` runs, then `evidence-drift` is named in the roster with its blocking status, so the lane is not one nobody wrote down (LL0013) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-06 | sdlc-studio | Filed |
| 2026-09-06 | sdlc | Shape ruled by the operator on 2026-09-06: refuse the commit and name the unit - a pre-commit lane that lists every Fixed unit whose registered mutant rows target a file the commit changes and refuses with the unit and its re-measure command; automatic re-measure and advisory-first were declined. Groomed alongside the D0182 batch |
