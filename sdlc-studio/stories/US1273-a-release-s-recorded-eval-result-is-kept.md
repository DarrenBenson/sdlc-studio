# US1273: A release's recorded eval result is kept as committed evidence

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0718
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .gitignore, evals/README.md, tools/tests/test_eval_results_committed.py
> **Epic:** EP0357
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A release's recorded eval result is kept as committed evidence
**So that** CR0718 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A results file is not ignored by git

- **Given** the repository's `.gitignore` and the results directory `tools/eval_run.py` writes to (`evals/.results/`)
- **When** `git check-ignore` is asked about a results file for a new run label in that directory
- **Then** git reports the file as not ignored, so a plain `git add` stages it, and the two results files already tracked stay tracked. Fails on: the `evals/.results/` ignore line still standing, which leaves a new run's result out of every commit unless someone remembers `git add -f`
- **Verify:** pytest tools/tests/test_eval_results_committed.py::EvalResultsCommittedTests::test_a_new_results_file_is_not_ignored

### AC2: The eval README says the release's result is committed under its version

- **Given** `evals/README.md`
- **When** its record step is read
- **Then** it says the run for a release is recorded under the version being cut as its label, that the results file is committed with the release, and it no longer tells the reader to force the add past an ignore rule. Fails on: a README that still instructs `git add -f`, or names no label a release check could look for
- **Verify:** pytest tools/tests/test_eval_results_committed.py::EvalResultsCommittedTests::test_the_readme_names_the_committed_result_and_its_label

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
