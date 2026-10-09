# US1023: The tests guarded to this repository's artefacts carry the corpus marker or a reasoned exemption, the shell-hazard test that turned main red among them

> **Status:** Draft
> **Delivers:** CR0617
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_advisory_warnings.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_duplicate_selectors.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_gate_lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_tag_no_close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/tests/test_corpus_marker_census.py, changelog.d/US1023.md
> **Epic:** EP0282
> **Points:** 3
> **Depends on:** US1021
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer who had main turn red from three bug texts no commit-time test read
**I want** every test guarded on `workspace.in_dev_repo` to go through `workspace.reads_corpus`, marked when it is a bounded read of the artefacts and exempt with a reason when it sweeps the whole corpus, and a census that fails when a guarded test does neither
**So that** the selection the hooks run holds the tests an artefact can break, and it cannot quietly shrink when the next guarded test is added

## Acceptance Criteria

- **AC1:** Given a throwaway `git clone --shared` of this repository with BG0967's original wording (an odd count of backticks in a fenced-bash phrase, as committed in 815e5c04) restored in its bug file, when the clone's `gate.py --suite-decision --changed` for that file and then `gate.py --run-tests --corpus` over the modules it names are run, then the run exits non-zero naming `test_no_legitimate_artefact_field_is_flagged`.
  - **Verify:** pytest tools/tests/test_corpus_marker_census.py::CorpusIncidentTests::test_the_incident_artefact_is_refused_by_the_corpus_selection
- **AC2:** Given this repository's test sources, when the census reads every test whose body, setUp or class guards on `workspace.in_dev_repo`, then each is decorated `reads_corpus`, either marked or exempt with a non-empty reason.
  - **Verify:** pytest tools/tests/test_corpus_marker_census.py::CorpusCensusTests::test_every_guarded_test_is_marked_or_exempt_with_a_reason
- **AC3:** Given fixture sources holding one guarded test with no decoration and one guarded test carrying only `boundary_only`, when the census runs over them, then it fails naming each by module, class and name.
  - **Verify:** pytest tools/tests/test_corpus_marker_census.py::CorpusCensusTests::test_an_undecorated_or_boundary_only_guarded_test_is_named
- **AC4:** Given a module carrying `reads_corpus` tests, when it is run with `python3 -m unittest` under an interpreter that cannot import pytest, then it imports and its tests pass or skip as they do today.
  - **Verify:** pytest tools/tests/test_corpus_marker_census.py::CorpusMarkerCompatTests::test_a_marked_module_loads_and_runs_without_pytest
- **AC5:** Given a fixture module holding one `reads_corpus(exempt='sweeps the whole corpus')` test that imports a code file, when `--run-tests --corpus` runs it and when a code change selects the module, then the exempt test is absent from the corpus run and runs in the code selection.
  - **Verify:** pytest tools/tests/test_corpus_marker_census.py::CorpusMarkerCompatTests::test_an_exempt_test_runs_where_it_ran_before

## Notes

- Release: 6.2 (D0355 breakdown G8, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: test_shell_hazard_rate's corpus tests left unmarked, so the selection never reaches the test that would have caught the 2026-10-07 incident
- AC2 must fail on: the decorator removed from one guarded test in this repository (for example test_no_legitimate_artefact_field_is_flagged), which the census must then report
- AC3 must fail on: a census satisfied by `boundary_only` (a unittest skip, boundary.py:60-63, which would silently take a heavy guarded test out of every code commit), or one that counts per module so a marked test hides an unmarked sibling
- AC4 must fail on: a top-level `import pytest` (or a bare `@pytest.mark.corpus`) in a marked module, which makes it unloadable under `npm test`'s unittest discovery (tools/skill-tests.sh:107-110) and the commit-msg fallback
- AC5 must fail on: the exemption implemented as a skip, so an exempt heavy reader stops running in the code-commit selections that reach it today
- Classified by kind at delivery, not by a per-test ceiling (the panel's answer). A test that sweeps the whole corpus is exempt with a reason: the `test_no_stamp_names_a_deleted_test` sweeps, the live-repository derivations, and test_gate's real-gate tests. A bounded read is marked. Record each test's measured time in the story at delivery.
- Measured at HEAD with the drafter's audit-hook probe: of the 20 guarded modules, 19 read the corpus in-process. test_refine's guarded test did not, so the census marks it exempt with that reason rather than forcing a corpus marker onto a test an artefact cannot break (the panel's proxy-drift point).
- The incident test (AC1) is the heaviest in the module, because it clones the repository and runs the corpus phase, so it gets its own class (CorpusIncidentTests). The static census classes stay cheap enough to run on every commit that touches a test module.
- Check the repo-writes lane while marking. It now runs on artefact commits too, so no marked test may write into `sdlc-studio/.local/`.
- test_gate.py is also in BG1000's Affects. This story builds after BG1000 and the first story, so the edits are sequential.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G8 after the refine panel's review |
