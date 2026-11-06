# US1134: Print one line on success from the hooks and the commands agents filter, and emit lint-clean markdown

> **Status:** Ready
> **Delivers:** CR0681
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/docgen.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/retro.py, tools/tests/test_quiet_hooks.py (new), .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py (new), changelog.d/US1134.md
> **Epic:** EP0300
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Print one line on success from the hooks and the commands agents filter, and emit lint-clean markdown
**So that** agents stop piping shipped commands through `tail` and hand-built wrappers, and a filter can no longer hide why a command refused

## Acceptance Criteria

- **AC1:** Given a commit whose lanes all pass, then `pre-commit` and `commit-msg` each print one summary line; given a failing lane, or `SDLC_GATE_VERBOSE=1`, they print the per-lane list with the failing lane's rule, detail and fix. Fails on: the summary printed on failure too, hiding the failing lane, or the `ok <lane>` lines still printed on success.
  - **Verify:** pytest tools/tests/test_quiet_hooks.py::QuietHookTests::test_success_is_one_line_and_failure_is_verbose
- **AC2:** Given a fixture where each succeeds, then `critic.py self-check record`, `verify_ac.py run`, `docgen.py surface`, `docgen.py reading-guides` and `sprint.py lane return` print at most two lines; given a refusal, each prints its full reason. Fails on: any success path over two lines, or a refusal path cut to the same two lines.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py::QuietSuccessTests::test_each_command_is_quiet_on_success_and_verbose_on_refusal
- **AC3:** Given an argument carrying a URL, then the markdown `file_finding.py`, `critic.py record` and the retro write passes the markdown lane's rules unedited, with no bare URL. Fails on: a producer writing a bare URL (the BG1227 shape) or a line the markdown lane refuses.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py::QuietSuccessTests::test_the_producers_write_lint_clean_markdown

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria and Verify checks authored |
