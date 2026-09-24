# US0879: A commit runs only the checks that catch real defects

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, tools/check_spec_claims.py, tools/runbook.py, tools/best_practice_rules.py, .claude/skills/sdlc-studio/scripts/gate.py, AGENTS.md, tools/tests/test_lean_commit_lanes.py
> **Epic:** EP0261
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** developer committing a change
**I want** each commit to run only the lint and test lanes that have caught real defects
**So that** a commit is quick and a lane that only checks docs against docs never blocks work

## Acceptance Criteria

- **AC1:** Given any commit, when the pre-commit and commit-msg hooks run, then the runbook, lens-signatures, spec-claims (with its timing claims), practice-rules, claim-drift, lane-check and suite-claim lanes do not run, and the AGENTS.md lane roster names only the lanes that do
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::CommitLaneTests::test_the_deleted_lanes_do_not_run
  - **Verified:** yes (2026-09-24)
- **AC2:** Given a fresh clone or worktree whose timing store holds one slow suite sample, when a commit runs, then no timing claim refuses it - the deadlock of BG0746 cannot recur
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::CommitLaneTests::test_a_slow_first_sample_never_blocks_a_commit
  - **Verified:** yes (2026-09-24)
- **AC3:** Given a staged style, link or markdown defect, when a commit runs, then it is still refused - the kept lint lanes still bite
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::CommitLaneTests::test_the_kept_lint_lanes_still_refuse
  - **Verified:** yes (2026-09-24)
- **AC4:** Given the concurrent-write window check, then exactly one implementation exists (gate.py's window lane) and the inline copy in the pre-commit hook is gone
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::CommitLaneTests::test_there_is_one_window_claim_implementation
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | sdlc-studio | AC1's roster clause (the AGENTS.md lane roster names only the lanes that run) is superseded by US0901: AGENTS.md carries no roster, each hook lists its own lanes with `--list`, and the roster half of the AC1 test is deleted |
