# US1167: A test module or class marked `# test-selection: sweep` joins every commit's selection, within a 30-second budget

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0671
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py, tools/tests/test_doc_claims.py, tools/tests/test_precommit_floor_pending.py, .claude/skills/sdlc-studio/scripts/tests/test_root_census.py, tools/tests/test_skill_tests_env.py, .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py, tools/tests/test_commit_msg_hook.py, .claude/skills/sdlc-studio/scripts/tests/test_sweep_selection.py, changelog.d/US1167.md
> **Epic:** EP0312
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** a test module or class marked `# test-selection: sweep` joins every commit's selection, within a 30-second budget
**So that** I know what each team's delivery costs per point and can hold it to a monthly budget

## Acceptance Criteria

- **AC1:** Given a repository with a module carrying `# test-selection: sweep` that imports nothing changed, when `gate.select_tests` answers for a change to scripts/sprint.py, and again for a docs-only change, then the sweep is selected in both beside whatever the change reaches, and the reason names it as a sweep.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sweep_selection.py::SweepSelectionTests::test_a_sweep_joins_every_commits_selection
- **AC2:** Given a module where only one class is the sweep, when the marker names that class, then the selection carries that class's node id and not the whole module.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sweep_selection.py::SweepSelectionTests::test_a_class_marker_selects_only_that_class
- **AC3:** Given this repository's markers, when they are read, then test_doc_claims, test_precommit_floor_pending, test_root_census, the test_skill_tests_env scrub sweep, the test_gitutil raw-git sweep (UnconfinedRawGitCallSweepTests) and the commit-hook hermeticity tests (HookInvocationHermeticityTests) are marked, tools/tests/test_test_census.py is not, and the marked set's recorded run times total at most 30 seconds, an unrecorded time being named rather than counted as zero.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sweep_selection.py::SweepSelectionTests::test_the_repositorys_sweeps_are_marked_and_fit_the_budget

## Notes

- Serves Abena Osei's End goal 3; delivers part of CR0671 (D0479).
- AC1 must fail on: selection by imports, loads, name and census subject only (gate.py:2557-2610 at HEAD)
- AC2 must fail on: a class marker selecting the whole module (test_commit_msg_hook.py and test_gitutil.py are mostly not sweeps)
- AC3 must fail on: a named sweep unmarked, test_test_census.py's RealRepoTests (about 250 s) marked, or a missing timing read as zero
- Start from gate.py select_tests (:2557) and the selection indexes with `_CENSUS_SUBJECT` (:2419-2530). The hook asks `gate.py --suite-decision --staged` in its suite lane (.githooks/pre-commit:452-520).
- test_lean_test_selection.py::SelectionTests::test_a_docs_only_commit_runs_no_suite stays green because its fixture carries no sweep marker; add a fixture case with one rather than loosening that test.
- Measured in the CR (2026-11-06): test_doc_claims 0.24 s, test_precommit_floor_pending 10 s, test_root_census about 18 s, the scrub sweep about 2 s, already near 30 s. Re-measure at HEAD (gate_timing.py) before marking; the budget may force one out.
- The CR's replay criterion (run six's commits refused at commit) and its before-and-after criterion are measurements for the orchestrator after the run, not Verify lines.
- The new test carries `# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
