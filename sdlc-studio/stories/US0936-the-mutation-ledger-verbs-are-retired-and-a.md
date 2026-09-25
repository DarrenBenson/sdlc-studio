# US0936: The mutation ledger verbs are retired and a mutation run reports its yield only

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_off.py, .claude/skills/sdlc-studio/scripts/tests/fixtures/bg0614-ledger/mutation-runs.json, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_ledger_retired.py, changelog.d/US0936.md, .claude/skills/sdlc-studio/help/mutation.md, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/scripts/tests/fixtures/bg0614-ledger/README.md, .claude/skills/sdlc-studio/scripts/tests/fixtures/bg0614-ledger/targets/stale_target.py, .claude/skills/sdlc-studio/scripts/tests/fixtures/bg0614-ledger/targets/unit_a.py, .claude/skills/sdlc-studio/scripts/tests/fixtures/bg0614-ledger/targets/unit_b.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_mutation_gate.py, sdlc-studio/bugs/BG0245-the-mutation-ledger-can-only-be-populated-by.md, sdlc-studio/bugs/BG0531-a-hand-applied-mutant-is-registered-with-no.md, sdlc-studio/bugs/BG0550-register-drops-a-file-s-earlier-registered-mutants.md, sdlc-studio/bugs/BG0552-a-registered-mutant-cannot-be-joined-to-a.md, sdlc-studio/bugs/BG0553-a-mistyped-mutation-verdict-cannot-be-corrected-and.md, sdlc-studio/bugs/BG0614-the-mutation-ledger-keeps-several-live-rows-on.md, sdlc-studio/bugs/BG0651-a-later-commit-that-changes-a-target-file.md, sdlc-studio/bugs/BG0747-the-evidence-drift-lane-still-enforces-mutation-evidence.md, sdlc-studio/stories/US0302-artefacts-filed-from-survivors-link-back-so-yield.md, sdlc-studio/stories/US0573-an-uncommitted-changed-surface-is-reported-as-that.md, sdlc-studio/stories/US0660-a-surviving-mutant-becomes-a-severity-rated-bug.md, sdlc-studio/stories/US0661-a-measured-mutation-run-records-what-it-applied.md, sdlc-studio/stories/US0818-mutation-py-register-replaces-the-live-row-when.md, sdlc-studio/stories/US0822-a-ledger-row-records-the-anchor-it-was.md, sdlc-studio/stories/US0882-mutation-evidence-that-is-switched-off-stops-blocking.md
> **Epic:** EP0263
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer who wants to probe a test suite
**I want** `mutation.py run` and `yield` to measure a suite when she asks, with `register`, `retract`, `retractions`, `audit` and the per-target ledger gone
**So that** mutation testing stays available as an instrument, with no ledger to keep honest and nothing downstream reading one

## Acceptance Criteria

- **AC1:** Given `mutation.py register`, `retract`, `retractions` or `audit`, when invoked, then each exits 2 with a message that it is retired naming `mutation.py run`, and `mutation.py --help` lists run, yield, window and prefilter only. Fails on: deleting the parsers so each verb exits with a usage error instead of the retirement message
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_ledger_retired.py::MutationLedgerRetiredTests::test_the_ledger_verbs_are_retired
- **AC2:** Given a fixture target and a test that kills a mutant, when `mutation.py run` runs, then it reports the kill and appends a series row that `mutation.py yield --run <id>` reads back, and it writes no per-target ledger (`mutation-runs.json`). Fails on: HEAD's `run`, which writes the ledger
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_ledger_retired.py::MutationLedgerRetiredTests::test_run_and_yield_work_without_a_ledger
- **AC3:** Given a fixture whose mutation ledger holds a retraction for the unit (so HEAD's `critic._withdrawn_block` renders) and a batch whose strategy carries the mutation band (so HEAD's `sprint.claimed_proof_gaps` reads the ledger), when `critic.py brief` runs on the unit and the sprint closes, then the brief carries no mutant-retraction section and the close's output is identical with the ledger removed. Fails on: removing the brief section while `claimed_proof_gaps` still reads the ledger
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_ledger_retired.py::MutationLedgerRetiredTests::test_brief_and_close_read_no_ledger
- **AC4:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `mutation.py register`, `retract`, `retractions` or `audit` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_ledger_retired.py::MutationLedgerRetiredTests::test_the_surface_names_no_retired_verb
- **AC5:** Given `verify_ac.py coverage rule` with a reason one character under the floor, when invoked, then it is refused naming the floor, and `verify_ac.py` holds that floor itself rather than reading `mutation._RETRACT_REASON_MIN`. Fails on: deleting `retract` and its constant while `add_coverage_ruling` still reads `mutation._RETRACT_REASON_MIN`, which raises
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_ledger_retired.py::MutationLedgerRetiredTests::test_the_coverage_ruling_floor_survives_the_retract_verb
- **AC6:** Given the criteria whose stamped Verify selector names a test this story deletes (LedgerTests, RegisterTests, StalenessHashTests, LedgerSummaryVocabularyTests, RegisterRunAttributionRefusalTests, MeasuredAttributionTests, RegisteredLineTests, UnreadableLedgerTests, RunUnitAttributionCLITests, RegisterEvidenceIntegrityTests, RetractWithdrawsAVerdictOnTheRecord, RegisterKeepsOtherUnitsRowsTests, DuplicateKeyTests, AuditRemedyTests, RegisterReplacesTests, AnchoredStalenessTests and AnchorIsRequiredTests in `test_mutation.py`, MutationSurvivorCountTests in `test_sprint_report.py`, and `test_lean_mutation_off.py`, which empties and is deleted): BG0245 (3), BG0614 (6), BG0651 (1), BG0747 (1), US0660 (1), US0661 (2), US0818 (3) and US0822 (8), then each is retired in the D0259 pattern (`Verify: manual - retired by US0936: <why>`, `Verified: manual (<date>) - retired, superseded by US0936`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_ledger_retired.py::MutationLedgerRetiredTests::test_no_stamp_names_a_deleted_test

## Notes

- Split from the original US0921 as its "b" half: the old AC1, AC2, AC4 (amended), AC5 and AC6. About 1,000 production lines of `mutation.py` and about 2,300 test lines.
- `StrandedMutantRecoveryTests` covers `run`'s crash recovery, which stays; BG0357 (`KilledMutantsCarryTheirKillerTests`) stays too. Both were dropped from the old AC6.
- Engineering call: AC5 is the readiness review's trap (`verify_ac` coverage rulings at 2517 and 2587 read `mutation._RETRACT_REASON_MIN`). It relocates a constant; it adds no check.
- Engineering call: Affects adds `test_sprint.py` (it calls `sprint.claimed_proof_gaps`) and `test_sprint_report.py` (it writes `mutation-runs.json` fixtures), found by grep beyond the readiness file list.
- Lands after US0920, US0935, US0921, US0912 and US0934: all read the ledger or `plan_execution`.
- Closes CR0556, EP0242 and US0800 together with US0911 (product seat ruling).
- - Line numbers re-measured at 013a46d0: `mutation.py --help` still lists register, retract, retractions and audit; `_RETRACT_REASON_MIN` at 2695, read by `verify_ac.py` 2520 and 2588; `critic._withdrawn_block` 3651 calls `mutation.retractions` (3659); `sprint.claimed_proof_gaps` 5910 reads `mutation._load_ledger` at 5927; `sprint_report.py` 187 reads `series_rows`, which stays; `MutationSurvivorCountTests` at `test_sprint_report.py` 2929. `verify_ac._purge_mutated_bytecode` (about 3828) calls `mutation._purge_bytecode`, which stays with `run`.
- Deleting about 2,300 lines of `test_mutation.py` also shortens the commit selection for a gate.py change (BG0754: `test_mutation` measured 15s of it).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: the US0921b half (8 points); user story written; takes the old AC1, AC2, AC4 (fixture holds a retraction and a mutation-band batch so HEAD reads the ledger), AC5 and AC6 (class list named, stranded-mutant and BG0357 dropped); new AC5 relocates the retraction floor; stamps measured (25 criteria); Affects adds test_sprint.py, test_sprint_report.py, the bg0614 fixture, the surface, the new module and the changelog fragment |
| 2026-09-25 | sdlc-studio v6 planning | Sprint 5 (engineering seat): line numbers refreshed against 013a46d0; premises stand |
