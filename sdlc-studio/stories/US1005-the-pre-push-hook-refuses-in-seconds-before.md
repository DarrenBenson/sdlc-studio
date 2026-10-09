# US1005: The pre-push hook refuses in seconds, before the suite, when the suite cannot be green on this interpreter

> **Status:** Draft
> **Delivers:** CR0613
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-push, tools/gate_prereqs.py, tools/tests/test_pre_push_prereqs.py, changelog.d/US1005.md
> **Epic:** EP0278
> **Points:** 3
> **Depends on:** US1003, BG0978
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer pushing from a new machine or a fresh clone
**I want** the pre-push hook to check the prerequisites without which the full suite cannot pass, and refuse before checking out the commit or running the gate when one is missing, naming it and a route that installs it on this interpreter
**So that** a missing package costs me seconds and one install, not a red gate after most of an hour and a retry

## Acceptance Criteria

- **AC1:** Given a fixture clone with the tracked pre-push hook, the prerequisite check and a stub gate.py that records its argv, and a python3 that cannot import coverage, when a branch push runs the hook, then the push is refused naming coverage and its install route, nothing reaches the remote, and the stub gate.py was never invoked.
  - **Verify:** pytest tools/tests/test_pre_push_prereqs.py::PushPrerequisiteTests::test_a_missing_suite_prerequisite_refuses_before_the_gate_runs
- **AC2:** Given the same fixture with coverage missing, when a tag push runs the hook, then it is refused the same way before the release boundary gate is invoked.
  - **Verify:** pytest tools/tests/test_pre_push_prereqs.py::PushPrerequisiteTests::test_a_tag_push_is_refused_before_the_release_gate
- **AC3:** Given a python3 with pytest, coverage and PyYAML but no pytest-xdist, and a PATH with no rg, markdownlint or gh, when a branch push runs the hook, then each is named as a note with its consequence, nothing is refused for them, and the stub gate.py is invoked once.
  - **Verify:** pytest tools/tests/test_pre_push_prereqs.py::PushPrerequisiteTests::test_a_prerequisite_that_does_not_make_the_suite_red_is_named_not_refused
- **AC4:** Given a python3 and PATH with every prerequisite present, when a branch push runs the hook, then no prerequisite line is printed as missing and the stub gate.py is invoked once with `--boundary push`.
  - **Verify:** pytest tools/tests/test_pre_push_prereqs.py::PushPrerequisiteTests::test_a_complete_environment_reaches_the_gate

## Notes

- Release: 6.2 (D0355 breakdown G4, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: no preflight in the hook (today: the gate is invoked and the full suite runs before anything is refused)
- AC2 must fail on: the preflight placed in the branch-push path only, so a tag runs the release lanes and the suite before refusing
- AC3 must fail on: every missing prerequisite treated as a refusal, so an offline push or a machine without xdist can no longer push at all
- AC4 must fail on: the hook reading the check's exit code inverted, or refusing on any output from it, so a complete environment is refused
- Builds after BG0978. The fixture is the stub-PATH pattern of test_pre_push_hook.py, and BG0978 fixes how that pattern links python3. A venv is the likely install route on an externally-managed interpreter.
- Sequence with BG0976, whose keepalive line (pre-push:64) is in the same block.
- Place the preflight right after the stdin loop decides the boundary (pre-push:37). It goes before the known-issues check, the red-CI read and the worktree checkout, so the refusal costs one python3 start.
- `python3 tools/gate_prereqs.py check --refusing` exits 1 only for the 'refuses the push' class from the first story. It honours `SDLC_COVERAGE_PYTHON`, so a push whose coverage tests would pass on that interpreter is not refused.
- The refusal names the bypass (`git push --no-verify`), as every other gate refusal in the hook does.
- An absent tools/gate_prereqs.py is named ('prerequisite check not present - not checked') and the push proceeds (the panel's answer). The existing fixtures in tools/tests/test_pre_push_hook.py and tools/tests/test_lean_release_notes.py copy only the files they need, and they keep passing unchanged.
- No wall-clock assertion. 'Before the suite' is decided by the stub gate never being invoked (BG0963 is what timing assertions cost here).
- Probed at HEAD: gate.py's full-suite lane refuses a missing pytest at once (gate.py:891). A missing coverage or PyYAML is found only by the suite's own red tests, after it has run in full.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G4 after the refine panel's review |
