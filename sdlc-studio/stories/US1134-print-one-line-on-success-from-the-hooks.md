# US1134: Print one line on success from the hooks and the commands agents filter, and emit lint-clean markdown

> **Status:** Done
> **Delivers:** CR0681
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/docgen.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, tools/tests/test_quiet_hooks.py (new), .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py (new), changelog.d/US1134.md, CONTRIBUTING.md, tools/tests/test_commit_msg_hook.py, tools/tests/test_commit_msg_mentions.py, tools/tests/test_pre_commit_docgen.py, tools/tests/test_precommit_stamps_advisory.py, tools/tests/test_lean_precommit_parallel.py, tools/tests/test_precommit_window_guard.py, tools/tests/test_lean_commit_lanes.py, tools/tests/test_lean_index_drift.py, tools/tests/test_lean_tsd_script_pin.py, tools/tests/test_message_first_gate.py, tools/tests/test_precommit_scope_collapse_lane.py, tools/tests/test_precommit_budget_recording.py, tools/tests/test_precommit_floor_pending.py, tools/tests/test_repo_writes.py, tools/tests/test_lean_refusal_log.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_advisory_warnings.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py
> **Epic:** EP0300
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Print one line on success from the hooks and the commands agents filter, and emit lint-clean markdown
**So that** agents stop piping shipped commands through `tail` and hand-built wrappers, and a filter can no longer hide why a command refused

## Acceptance Criteria

- **AC1:** Given a commit whose lanes all pass, then `pre-commit` and `commit-msg` each print one summary line, the last line each prints, and no `ok <lane>` line; the only lines a pass prints above it are the two an author learns from nowhere else: the stamps-staged lane's re-read list (printed by the hook's `verdict()` on a pass since BG0779) and the settle step's report of the drift it restaged or left unstaged (US0899). Given a failing lane, or `SDLC_GATE_VERBOSE=1`, they print the per-lane list with the failing lane's rule, detail and fix. CONTRIBUTING.md's paragraph on the commit gate names `SDLC_GATE_VERBOSE=1` as the way to see the lanes and the 90-second budget report on a pass. Fails on: the summary printed on failure too, hiding the failing lane; the `ok <lane>` lines still printed on success; a pass that hides the re-read list or the settle report.
  - **Verify:** pytest tools/tests/test_quiet_hooks.py::QuietHookTests::test_success_is_one_line_and_failure_is_verbose tools/tests/test_quiet_hooks.py::QuietHookTests::test_a_pass_still_shows_the_re_read_list_and_the_settle_report
  - **Verified:** yes (2026-11-12)
- **AC2:** Given a fixture where each succeeds, then `critic.py self-check record`, `verify_ac.py run`, `docgen.py surface`, `docgen.py reading-guides` and `sprint.py lane return` print at most two lines; given a refusal, each prints its full reason. Fails on: any success path over two lines, or a refusal path cut to the same two lines.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py::QuietSuccessTests::test_each_command_is_quiet_on_success_and_verbose_on_refusal
  - **Verified:** yes (2026-11-12)
- **AC3:** Given an argument carrying a URL, then the markdown `file_finding.py`, `critic.py record` and the retro write passes the markdown lane's rules unedited, with no bare URL. Fails on: a producer writing a bare URL (the BG1227 shape) or a line the markdown lane refuses.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py::QuietSuccessTests::test_the_producers_write_lint_clean_markdown
  - **Verified:** yes (2026-11-12)
- **AC4:** Given the 17 existing modules that drive the real hooks over a commit (under `tools/tests/`: `test_commit_msg_hook`, `test_commit_msg_mentions`, `test_pre_commit_docgen`, `test_precommit_stamps_advisory`, `test_lean_precommit_parallel`, `test_precommit_window_guard`, `test_lean_commit_lanes`, `test_lean_index_drift`, `test_lean_tsd_script_pin`, `test_message_first_gate`, `test_precommit_scope_collapse_lane`, `test_precommit_budget_recording`, `test_precommit_floor_pending`, `test_repo_writes` and `test_lean_refusal_log`; under the skill's `scripts/tests/`: `test_lean_advisory_warnings` and `test_lean_test_selection`), then each passes, and each assertion it makes on a passing hook's per-lane, SKIP, note, budget or advisory output either runs that hook with `SDLC_GATE_VERBOSE=1` or asserts the summary line; the re-read list and the settle report AC1 keeps are asserted without it. Fails on: any of them red; a pass-path `assertNotIn` left reading the summary line alone, where it holds whatever the hook does (`test_lean_refusal_log.py:119`, `test_repo_writes.py:332`); an assertion on a refusal removed or loosened.
  - **Verify:** pytest tools/tests/test_precommit_window_guard.py tools/tests/test_lean_commit_lanes.py tools/tests/test_lean_tsd_script_pin.py tools/tests/test_precommit_scope_collapse_lane.py tools/tests/test_precommit_stamps_advisory.py .claude/skills/sdlc-studio/scripts/tests/test_lean_advisory_warnings.py .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py tools/tests/test_message_first_gate.py tools/tests/test_lean_refusal_log.py tools/tests/test_lean_index_drift.py tools/tests/test_commit_msg_hook.py tools/tests/test_commit_msg_mentions.py tools/tests/test_pre_commit_docgen.py tools/tests/test_lean_precommit_parallel.py tools/tests/test_precommit_budget_recording.py tools/tests/test_precommit_floor_pending.py tools/tests/test_repo_writes.py
  - **Verified:** yes (2026-11-12)

## Re-grooming note (run nine, D0453)

The run nine build met every criterion but its landing was refused: beyond the six hook tests D0452 added, 8 test modules pin the verbose pass output or are broken by the change, and must join Affects (and the points) before it is built again: `.claude/skills/sdlc-studio/scripts/tests/test_lean_advisory_warnings.py`, `.claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py`, `.claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py`, `tools/tests/test_lean_commit_lanes.py`, `tools/tests/test_lean_index_drift.py`, `tools/tests/test_lean_tsd_script_pin.py`, `tools/tests/test_message_first_gate.py`, `tools/tests/test_precommit_scope_collapse_lane.py`. The staged build is on the local branch `worktree-agent-a8392c4d934f0a9de` until clean-up.

## Re-grooming note (run ten)

Checked at HEAD 508e2408 by grep, `git log` and reading the code.

- **The build still applies.** The run nine build is staged in `.claude/worktrees/agent-a8392c4d934f0a9de` on base f4e3a8c5, and none of its 15 files has changed on main since. It holds the hook, `sprint.py`, `critic.py`, `docgen.py` and `retro.py` changes and both new test modules. A builder may start from it, but it hides the re-read list and the settle report, which AC1 now keeps.
- **test_resume_brief.py leaves the run nine list.** Its failure in that build's gate log, `KnownIssuesTests::test_the_moment_is_read_through_the_report_helper`, came from an order-dependent `sys.modules` patch that BG1329 fixed at 96ac3662. It does not read hook output.
- **Four more modules join Affects.** The run nine commit never selected them, so its gate never ran them. Each asserts a passing hook's output: `test_precommit_budget_recording.py:170` (the docs-only marker) and `:199` (the 90-second budget line), `test_precommit_floor_pending.py:182` (`ok`), and `test_repo_writes.py:315` (`repo-writes`) and `:333` (the docs-only marker). `test_lean_refusal_log.py:119` asserts no failed lane on a passing commit, which would hold against the summary line whatever the hook did. AC4 runs all 17 modules in five Verify lines rather than one, because `lane return` gives each Verify line 300 seconds (`sprint.py:8625`) and these modules drive real commits.
- **Two outputs a pass prints today stay.** `.githooks/pre-commit:114-126` prints the stamps-staged re-read list on a passing commit, because "on a passing commit this is the only place its author would see it" (BG0779). `:171-184` names the drift that settle restaged or left unstaged (US0899). The run nine build counted both as "note line(s) held", which would have undone BG0779.
- **Already met at HEAD.** AC2's success path is already within two lines for `critic.py self-check record` (one line, `critic.py:4453`), `verify_ac.py run` on one unit (a result line and `wrote <report>`, `verify_ac.py:3432-3455`), and `docgen.py surface` and `reading-guides` (one line each, `docgen.py:380-381` and `:415-416`). AC3 is already met for `file_finding.py`, which has code-spanned a bare URL since BG1227 (475b0293, `file_finding._code_urls` at `:1692`). `verify_ac.py` and `file_finding.py` leave Affects, because the build changed neither. Still to do: the hooks, `sprint.py lane return`'s pass path (`sprint.py:9239-9270`), `docgen.py reading-guides` refusing a root with no skill tree (it prints `0 of 0` and exits 0), the issues cell of `critic.py record` (`critic.py:392`) and the retro accuracy block (`retro.py:2013`).
- **A doc goes stale.** CONTRIBUTING.md:232-240 says a commit "reports its time against a 90-second budget". On a quiet pass that report is held back.
- **Points go from 3 to 5.** The work is 17 hook test modules (11 more than the build adapted), AC4's run of them, and the two outputs AC1 keeps. Above 5 points the natural split would be AC1 with AC4 (the hooks and their tests) apart from AC2 with AC3 (`lane return` and the markdown producers).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria and Verify checks authored |
| 2026-11-09 | Claude Opus 5.5 (run nine, D0452) | Affects gains the six hook tests that pin the verbose pass output AC1 retires; they run the hooks with SDLC_GATE_VERBOSE=1 or assert the summary line |
| 2026-11-09 | Claude Opus 5.5 (run nine, D0453) | Descoped from run nine: the change reaches tests beyond its Affects; re-grooming note added |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: Affects gains the 11 further hook test modules (run nine's eight less test_resume_brief.py, plus test_precommit_budget_recording.py, test_precommit_floor_pending.py, test_repo_writes.py and test_lean_refusal_log.py) and CONTRIBUTING.md, and drops verify_ac.py and file_finding.py, whose parts of AC2 and AC3 are met at HEAD; AC1 keeps the re-read list (BG0779) and the settle report (US0899) on a pass; AC4 added; Points 3 to 5 |
