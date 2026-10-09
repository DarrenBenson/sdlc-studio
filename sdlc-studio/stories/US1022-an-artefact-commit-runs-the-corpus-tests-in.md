# US1022: An artefact commit runs the corpus tests in the commit hooks, names them and their time, and records them apart from the code-commit series

> **Status:** Draft
> **Delivers:** CR0617
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/gate.py, tools/gate_timing.py, AGENTS.md, tools/tests/test_commit_runs_corpus_tests.py, changelog.d/US1022.md
> **Epic:** EP0282
> **Points:** 5
> **Depends on:** US1021
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer committing a bug filing, a triage or a review page
**I want** the commit hooks to hand the corpus selection from pre-commit to commit-msg and run it there, refusing the commit when a corpus test fails, reporting the phase's own tests and seconds, and keeping that run out of the series and verdicts that describe code-commit and full runs
**So that** an artefact that breaks a corpus test is refused at its own commit, not found by CI after a push that was slow or bypassed, without corrupting the timings the planner prices commits from

## Acceptance Criteria

- **AC1:** Given a fixture clone with the tracked pre-commit and commit-msg hooks and a `reads_corpus` test that fails when any bug file contains a sentinel word, when a commit stages only a bug file carrying that word, then the commit is refused and the output names the failing corpus test.
  - **Verify:** pytest tools/tests/test_commit_runs_corpus_tests.py::CommitRunsCorpusTestsTests::test_an_artefact_that_breaks_a_corpus_test_is_refused_at_its_commit
- **AC2:** Given the same clone, when a commit stages only a clean bug file, then the commit lands, no test outside the corpus selection runs, and the budget output states the corpus phase's own test count and seconds, apart from pre-commit's seconds.
  - **Verify:** pytest tools/tests/test_commit_runs_corpus_tests.py::CommitRunsCorpusTestsTests::test_a_clean_artefact_commit_runs_only_the_corpus_tests_and_reports_their_share
- **AC3:** Given the same clone with a seeded gate-timings.json, when a corpus-only commit lands, then its seconds are recorded in a series of their own and the `total`, `total.selected` and `total.last_series` entries are unchanged.
  - **Verify:** pytest tools/tests/test_commit_runs_corpus_tests.py::CommitRunsCorpusTestsTests::test_a_corpus_only_commit_records_its_time_in_its_own_series
- **AC4:** Given the same clone, when a corpus-only commit lands green, then the recorded suite verdict carries the mode `corpus`, never `full`.
  - **Verify:** pytest tools/tests/test_commit_runs_corpus_tests.py::CommitRunsCorpusTestsTests::test_a_corpus_only_green_is_recorded_as_corpus_not_full
- **AC5:** Given the same clone with a python3 that cannot import pytest, when a corpus-only commit runs, then the hooks name the corpus phase as skipped (it needs pytest) and the commit is not refused by the suite-collapse lane.
  - **Verify:** pytest tools/tests/test_commit_runs_corpus_tests.py::CommitRunsCorpusTestsTests::test_without_pytest_the_corpus_phase_is_named_skipped_and_not_a_collapse

## Notes

- Release: 6.2 (D0355 breakdown G8, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: pre-commit not handing the corpus selection over (today: the decision is `skip`, 'artefacts ... run no unit suite here', and the commit lands)
- AC2 must fail on: commit-msg reading a handover that carries corpus lines but no `suite-selector=` line as 'run everything' (commit-msg:250-258 today), so the whole fixture suite runs
- AC3 must fail on: `total_suite` still keyed on `$selectors` (commit-msg:394), so the corpus run lands in the full-run `total` series that the planner prices commits from (sprint.py:12352) and flips `total.last_series` to `full`, the comparability failure BG0239 fixed
- AC4 must fail on: commit-msg:451-452 unchanged, so a corpus-only green with no selector lines is recorded as a `full` green and a later commit over the same surface reuses it as if the whole suite had passed
- AC5 must fail on: the unittest fallback's scope check (commit-msg:396-413) run against the full-suite peak with no selection passed, refusing the commit as a collapsed suite; or the fallback running whole modules
- Re-sized from 3 to 5 on the panel's finding. Four places in commit-msg turn on whether `$selectors` is empty, not one:
- the run-everything branch (:258); `total_suite` (:394); `--verdict-mode` (:452); and the unittest path's suite-collapse check (:396-413).
- The handover record (`sdlc-gate-suites` in the git directory) gains a `suite-corpus=<module>` line kind. commit-msg passes those lines as `--corpus` to the one `gate.py --run-tests` invocation.
- gate.py's `--verdict-mode` choices (gate.py:2765, today `full` and `selected`) gain `corpus`. tools/gate_timing.py gains the corpus series, with its own `last_series` handling if needed.
- The commit budget stays reported, not refused (commit-msg:419-430). The corpus phase's seconds are reported against the operator's figure (the panel suggests 30s) and recorded in their own series, so creep shows. Which line an artefact commit prints for the 90-second whole-commit comparison is the operator's question.
- AGENTS.md:189-191 ('a docs or artefact commit runs none') changes to say that an artefact commit now runs a timed corpus phase. Agents commit artefacts with default tool timeouts on the strength of that sentence.
- Fixture pattern: tools/tests/test_lean_commit_lanes.py and test_commit_msg_hook.py already build throwaway clones with the tracked hooks. Reuse tools/tests/hookutil.py.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G8 after the refine panel's review |
