# US1024: The measured corpus readers outside the guarded modules carry the marker or a reasoned exemption, BG0813's test among them

> **Status:** Draft
> **Delivers:** CR0617
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_epic_index_derivation.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_cr_filing.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_ledger_retired.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_mutation_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issue_rulings.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_operator_interventions.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_retired.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_seats.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_k_terms.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py, .claude/skills/sdlc-studio/scripts/tests/test_root_census.py, tools/tests/test_adr011_agreement.py, tools/tests/test_availability_contract.py, tools/tests/test_epic_index_derived.py, tools/tests/test_evidence_in_git.py, tools/tests/test_lean_commit_lanes.py, tools/tests/test_lean_docs_v61.py, tools/tests/test_lean_prd_refresh.py, tools/tests/test_lean_release_verify.py, tools/tests/test_lean_spec_restatements.py, tools/tests/test_lean_trd_constraints_repo.py, tools/tests/test_lean_tsd_script_pin.py, tools/tests/test_lean_value_docs.py, tools/tests/test_lint_workflow_coverage.py, tools/tests/test_persona_coherence.py, tools/tests/test_porting_doctrine.py, tools/tests/test_seat_examples_quote_real_goals.py, tools/tests/test_supersession_records.py, tools/tests/test_token_premise.py, sdlc-studio/retros/evidence/corpus-readers-measured.txt, tools/tests/test_corpus_measured_readers.py, changelog.d/US1024.md
> **Epic:** EP0282
> **Points:** 3
> **Depends on:** US1021
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose second artefact-caused red (BG0813) came from a test no `in_dev_repo` census can see
**I want** every test measured reading this repository's artefacts, beyond the guarded modules, to go through `workspace.reads_corpus` (marked, or exempt with a reason), working from a measured list committed as evidence
**So that** the corpus phase covers the readers an artefact has actually broken, not only the third that happen to carry a guard

## Acceptance Criteria

- **AC1:** Given this repository, when `gate.py --suite-decision --changed sdlc-studio/bugs/<any>.md` runs and then `gate.py --run-tests --corpus` over the modules it names, then test_critic.py is among the `suite-corpus:` lines and `BriefTierTests::test_the_corpus_spans_more_than_one_band` is among the tests run.
  - **Verify:** pytest tools/tests/test_corpus_measured_readers.py::MeasuredReadersTests::test_bg0813s_test_is_in_the_corpus_run
- **AC2:** Given the measured reader list committed at `sdlc-studio/retros/evidence/corpus-readers-measured.txt`, when each listed test is looked up in the test sources, then every one is decorated `reads_corpus`, marked or exempt with a non-empty reason.
  - **Verify:** pytest tools/tests/test_corpus_measured_readers.py::MeasuredReadersTests::test_every_measured_reader_is_marked_or_exempt
- **AC3:** Given a fixture with a `reads_corpus` test under `tools/tests` as well as one under the skill tests directory, when an artefact change is answered by `--suite-decision` and run with `--run-tests --corpus`, then both modules are named and both tests run.
  - **Verify:** pytest tools/tests/test_corpus_measured_readers.py::MeasuredReadersTests::test_a_tools_tests_reader_is_selected_like_a_skill_test

## Notes

- Release: 6.2 (D0355 breakdown G8, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: test_critic's BriefTierTests left unmarked, so the test BG0813's filings turned red on 2026-09-28 stays outside the corpus phase
- AC2 must fail on: one listed test left undecorated (the census over the committed list must name it)
- AC3 must fail on: the first story's discovery reading only the skill tests tree, so every tools/tests reader (18 of the 37 modules here) is never selected
- Driven by measurement, not a static rule (the panel's required change). No static census can see test_critic.py, which reads the corpus through a local `repo` variable and through library calls given `REPO_ROOT` (LL0043).
- At delivery, run the audit-hook probe (a pytest plugin recording `open`, `os.listdir` and `os.scandir` under `<repo>/sdlc-studio/` per test) once over the whole suite. The drafter ran it only over 58 candidate modules. Commit its list as the evidence file, then decorate or exempt each test.
- The affects above are the 37 modules the candidate run found outside the guarded set, plus test_critic.py. The whole-suite run may add modules, and the story's Affects is updated with them at delivery.
- The evidence file is a dated snapshot, not a hand-maintained registry. The measured CI census (the next CR) re-derives it and becomes the drift guard.
- tools/tests modules import `workspace` from the skill tests directory by path, as several already import the skill's scripts.
- Same delivery rules as the guarded story: classify by kind, record the times, keep marked tests out of `sdlc-studio/.local/`.
- Reads made by a spawned subprocess are not counted by an in-process audit hook. Where a test drives a CLI with `--root` at the repository, decide it by reading the test and record the decision in the evidence file.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G8 after the refine panel's review |
