# US0969: A CLI never reports success it did not get

> **Status:** Ready
> **Delivers:** CR0592
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_cli_no_false_success.py, changelog.d/US0969.md
> **Epic:** EP0270
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** a command that did not get the answer it was asked for to say so
**So that** a wrong key, a wrong directory or an unreadable CI answer never reads as a clean result

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from CR0592 bullets 17, 20, 33 and 44, 3 points. Each command below exits 0 on a result it did not get. The fix makes each one report what happened; that removes a false success and refuses no valid input.

- #17 `config.py show --key` on a key that is absent prints `null` and exits 0. A key that is present with a null value keeps printing `null`.
- #33 `validate.py check --root <dir>` on a directory with no `sdlc-studio/` prints `checked=0 errors=0 warnings=0` and exits 0.
- #44 `sprint_report.fetch_ci_runs` reads a JSON answer that is not a list (an error object such as `{"message": "HTTP 403"}`) as an empty window, so the report's CI figures read zero rather than unreadable.
- #20 `artifact.py batch` prints `template=minimal` when a project-declared story template rendered the stories.

## Premise at HEAD

Executed at `85042135`:

```text
$ python3 .claude/skills/sdlc-studio/scripts/config.py show --key nonexistent.key
null
exit=0
$ python3 .claude/skills/sdlc-studio/scripts/validate.py check --root <empty dir>
checked=0 errors=0 warnings=0
exit=0
```

## Acceptance Criteria

- [ ] **AC1** Given a fixture project, when `config.py show --key nonexistent.key --root <fixture>` runs, then it exits 1 and names `nonexistent.key` as absent, while `config.py show --key review.max_rounds` still prints its value and exits 0. Fails on: HEAD prints `null` and exits 0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_cli_no_false_success.py::CliNoFalseSuccessTests::test_an_absent_config_key_is_named_not_printed_as_null
- [ ] **AC2** Given an empty directory, when `validate.py check --root <dir>` runs, then it exits 1 and says no `sdlc-studio/` workspace was found. Fails on: HEAD prints `checked=0 errors=0 warnings=0` and exits 0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_cli_no_false_success.py::CliNoFalseSuccessTests::test_validate_on_a_directory_with_no_workspace_says_so
- [ ] **AC3** Given a stub `gh` first on `PATH` whose `run list --json` answer is `{"message": "HTTP 403"}`, when `sprint_report.fetch_ci_runs` reads it, then its reason names an answer that is not a list, so the report reads the CI window as unreadable. Fails on: HEAD returns `([], 'gh run list')`, the shape of a window with no runs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_cli_no_false_success.py::CliNoFalseSuccessTests::test_a_non_list_gh_answer_reads_unreadable_not_empty
- [ ] **AC4** Given a fixture with a project-declared story template, when `artifact.py batch --type story` mints two stories, then its summary line names the template that rendered them. Fails on: HEAD prints `template=minimal`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_cli_no_false_success.py::CliNoFalseSuccessTests::test_batch_names_the_template_it_rendered

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
