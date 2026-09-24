# US0921: Mutation testing is an opt-in run with a yield and nothing more

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_off.py, .claude/skills/sdlc-studio/scripts/tests/fixtures/bg0614-ledger/mutation-runs.json, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_opt_in.py
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer who wants to probe a test suite
**I want** `mutation.py run` and `yield` to measure a suite when she asks, with register, retract, retractions, audit, the per-target ledger and the gate's mutation lane gone
**So that** mutation testing stays available as an instrument without a ledger to keep honest or a lane to feed

## Acceptance Criteria

- **AC1:** Given `mutation.py register`, `retract`, `retractions` or `audit`, when invoked, then each exits 2 with a message that it is retired naming `mutation.py run`, and `mutation.py --help` lists run, yield, window and prefilter only
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_opt_in.py::MutationOptInTests::test_the_ledger_verbs_are_retired
- **AC2:** Given a fixture target and a test that kills a mutant, when `mutation.py run` runs, then it reports the kill and appends a series row that `mutation.py yield --run <id>` reads back, and it writes no per-target ledger (`mutation-runs.json`)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_opt_in.py::MutationOptInTests::test_run_and_yield_work_without_a_ledger
- **AC3:** Given the standard gate, then it runs no `mutation` lane; an open rewrite window claiming a staged path is still refused by the `window` lane, which stays
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_opt_in.py::MutationOptInTests::test_no_mutation_lane_and_the_window_still_guards
- **AC4:** Given `critic.py brief` on a unit and a sprint close, then the brief carries no mutant-retraction section and the close reads no mutation ledger
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_opt_in.py::MutationOptInTests::test_brief_and_close_read_no_ledger
- **AC5:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `mutation.py register`, `retract`, `retractions` or `audit` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_opt_in.py::MutationOptInTests::test_the_surface_names_no_retired_verb
- **AC6:** Given every criterion whose stamped Verify selector names a test this story deletes (the ledger, register, stranded-mutant, registered-line, unreadable-ledger, retract and audit classes in `test_mutation.py`, the mutation lane classes in `test_gate.py` and the register test in `test_lean_mutation_off.py`; at least those on BG0357, BG0651, US0661, US0818, US0882), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_opt_in.py::MutationOptInTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
