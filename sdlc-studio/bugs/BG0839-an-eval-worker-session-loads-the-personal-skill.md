# BG0839: An eval worker session loads the personal skill ahead of the candidate copy, and nothing in the harness says so or prevents it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/eval_run.py, evals/README.md, tools/tests/test_lean_eval_isolation.py, changelog.d/BG0839.md, tools/tests/test_eval_run.py
> **Evidence:** eval harness note (/tmp/evals-v6-final 06 run); HEAD 7e53a438 grep: no CLAUDE_CONFIG_DIR in tools/ or evals/
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:27:13Z

## Summary

Under `claude -p` a same-named project skill does not outrank the personal `~/.claude/skills/sdlc-studio`: the first v6-final eval 06 worker loaded the personal copy and diffed both, so that run was mixed and could not be the D0280 evidence. Clean runs need `CLAUDE_CONFIG_DIR`. evals/README.md says only 'with the candidate skill installed', and `tools/eval_run.py setup` neither isolates nor warns.

## Steps to Reproduce

With a personal copy installed, run a scenario worker per evals/README.md: the transcript shows the personal skill loaded.

## Proposed Fix

`eval_run.py setup` prints the worker command with an isolated `CLAUDE_CONFIG_DIR` holding only the candidate skill, and warns when a personal copy differs from it; the README says so.

## Acceptance Criteria

- [ ] **AC1** Given a personal skill copy that differs from the candidate, when `eval_run.py setup` runs, then it prints a worker command with an isolated `CLAUDE_CONFIG_DIR` and a warning naming both paths. Fails on: HEAD
  - **Verify:** pytest tools/tests/test_lean_eval_isolation.py::EvalIsolationTests::test_setup_isolates_the_candidate_skill

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
