# BG1492: Nothing stops the orchestrator committing a reviewer's half-written verdict: git add of the records sweeps in a verdict file still being written

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .githooks/pre-commit, tools/tests/test_precommit_unrecorded_verdict.py, changelog.d/BG1492.md
> **Evidence:** Run fourteen (RUN-01M7GEHM), US1161 accept, 2026-11-15.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T01:57:33Z

## Summary

In run fourteen, the orchestrator committed accepted units' records with `git add -A sdlc-studio/` while a reviewer was still writing US1161's verdict, so a half-written verdict (its line citations incomplete) went into a commit. A verdict file being written has no marker the commit can see, and the hooks do not refuse a verdict that `critic.py record` has not yet read.

## Steps to Reproduce

1. Start a reviewer writing a verdict under sdlc-studio/reviews/.
2. Before it finishes, commit the records with git add -A sdlc-studio/.
3. See the partial verdict committed.

## Proposed Fix

Have critic.py write verdicts through a temp file and rename it into place, and have the pre-commit hook refuse a staged verdict file that no recorded review row cites.

## Acceptance Criteria

- [ ] **AC1** Given a verdict file staged under sdlc-studio/reviews/verdicts/ that no recorded review row cites, when the staged-verdict check in `critic.py` runs, then it exits non-zero and names the file and the `critic.py record` command that would bind it. Fails on: a verdict still being written passing as a record.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StagedVerdictTests::test_a_staged_verdict_no_recorded_row_cites_is_refused_by_name
- [ ] **AC2** Given a staged verdict file whose bytes a recorded review row cites, when the same check runs, then it exits 0 and prints no refusal. Fails on: the check refusing the verdicts an accept legitimately commits, or passing a file edited after its row was recorded.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StagedVerdictTests::test_a_staged_verdict_its_recorded_row_cites_passes
- [ ] **AC3** Given a clone with the hooks enabled and an unrecorded verdict file swept in by a git add of the records, when the commit runs, then pre-commit refuses it on a lane that `.githooks/pre-commit --list` prints, and nothing is committed. Fails on: the check existing in `critic.py` with no hook lane calling it.
  - **Verify:** pytest tools/tests/test_precommit_unrecorded_verdict.py::UnrecordedVerdictLaneTests::test_a_commit_holding_an_unrecorded_verdict_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
