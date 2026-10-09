# US1021: gate.py names and runs the corpus-marked tests that a change under sdlc-studio/ reaches

> **Status:** Draft
> **Delivers:** CR0617
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/workspace.py, pytest.ini, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/scripts/tests/test_gate_corpus_selection.py, changelog.d/US1021.md
> **Epic:** EP0282
> **Points:** 3
> **Depends on:** BG1000
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose agents commit artefacts many times a day
**I want** `gate.py --suite-decision` to answer a change under `sdlc-studio/` with the test modules that use the `workspace.reads_corpus` decorator, and `gate.py --run-tests --corpus` to run only the tests it marks and report how many ran and how long they took
**So that** an artefact change has a selection I can ask for and run in seconds, instead of 'artefacts run no unit suite here'

## Acceptance Criteria

- **AC1:** Given a fixture root holding one test module with a test decorated `reads_corpus` and one undecorated module whose docstring uses the word 'corpus', when `gate.py --suite-decision --changed sdlc-studio/bugs/BG0001-x.md` runs, then it answers `suite-decision: run`, prints a `suite-corpus:` line naming only the decorated module, and its reason says the change is an artefact.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_corpus_selection.py::CorpusSelectionTests::test_an_artefact_change_selects_only_the_decorated_modules
- **AC2:** Given the same root, when `--changed` names only a code file that one test module imports, then the answer is that import-edge selection as today and carries no `suite-corpus:` line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_corpus_selection.py::CorpusSelectionTests::test_a_code_only_change_selects_by_import_edges_alone
- **AC3:** Given the same root with the decorated module also importing the changed code file, when `--changed` names both an artefact and that code file, then the decorated module appears once, as a `suite-selector:` line, and no `suite-corpus:` line repeats it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_corpus_selection.py::CorpusSelectionTests::test_a_mixed_change_runs_each_module_once
- **AC4:** Given a module holding one `reads_corpus` passing test and one undecorated failing test, when `gate.py --run-tests --corpus <module>` runs, then it exits 0, runs exactly one test, and prints a `corpus:` line naming the module count, the test count and the seconds taken.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_corpus_selection.py::CorpusRunTests::test_the_corpus_run_executes_only_marked_tests_and_reports_them

## Notes

- Release: 6.2 (D0355 breakdown G8, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the marked modules found by a substring scan for 'corpus' (53 of 430 modules carry the word today), so the undecorated module is selected; or today's `_CODE_SUFFIXES` filter left as the only route, so the answer is `skip` with mode `none`
- AC2 must fail on: the corpus route firing on every change, so a code-only commit pays for the corpus tests too
- AC3 must fail on: one route replacing the other when both apply, or a module selected whole by a code route run a second time in the corpus phase
- AC4 must fail on: the corpus phase running whole modules (no `-m corpus`), so the undecorated red test runs and the exit is non-zero
- This story creates `workspace.reads_corpus(exempt=None)` in .claude/skills/sdlc-studio/scripts/tests/workspace.py. The decorator does four things:
- It skips outside the dev repository, as `in_dev_repo` guards do today. It applies `pytest.mark.corpus` only when pytest imports, so unittest discovery and the no-pytest fallback still load the module. With `exempt='reason'` it applies no marker and leaves the test running exactly where it runs today. Its name is the precise token that selection and the census read.
- Discovery (the panel's required change). First a cheap substring prefilter for `reads_corpus`, then an AST pass that keeps a module only if it decorates a test with `reads_corpus` and carries no `exempt=`. Docstrings and string literals never count, which follows the repository's own precedent that a source scan for a marker is a mutant (test_gate.py:4940-4943, :4981). pytest's `-m corpus` then decides the tests themselves.
- Precision protects consuming projects too. TEST_SUITE_DIRS includes `tools/tests` (gate.py:2243-2246) and every consuming project has an `sdlc-studio/` workspace, so 'suite_modules is empty there' is not always true.
- Run the corpus phase serially, or at `-n 2`, when the marked set is small. Measured by the panel: collection alone for the 19 guarded modules took 12.9s serial against 32.2s at `-n 8`, because every xdist worker collects every module. Register `corpus` in pytest.ini beside `serial_only` and `boundary_only`.
- `--corpus` must be consumed where it lands, because the pre-commit `dead-flags` lane refuses a parsed flag that nothing acts on.
- help/gate.md's 'How a commit's selection is made' list (lines 121-131) says artefacts select nothing. This story owns its rewrite, after BG1000 lands.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G8 after the refine panel's review |
