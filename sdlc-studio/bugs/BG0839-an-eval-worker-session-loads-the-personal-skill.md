# BG0839: An eval worker session loads the personal skill ahead of the candidate copy, and nothing in the harness says so or prevents it

> **Status:** Fixed
> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: `grep -rn CLAUDE_CONFIG_DIR tools/ evals/` finds nothing; `eval_run.py setup` prints `--- WORKER PROMPT (fresh session, skill installed) ---` and evals/README.md step 2 says only `with the candidate skill installed`. Narrowed: setup always prints the isolated command, so the personal-copy diff warning is dropped (one more check, no extra value), and setup copies no credentials
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/eval_run.py, evals/README.md, tools/tests/test_lean_eval_isolation.py, tools/tests/test_eval_run.py, changelog.d/BG0839.md
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

`eval_run.py setup` also builds `<dir>.claude-config/skills/sdlc-studio` (a sibling of the fixture, so its transcripts never dirty the fixture's `git status`) from the candidate skill (the working tree's `.claude/skills/sdlc-studio`) and prints the worker command as `CLAUDE_CONFIG_DIR=<dir>.claude-config claude -p ...`. evals/README.md step 2 says why (a personal copy outranks a project copy under `claude -p`) and that the operator copies `~/.claude/.credentials.json` into that directory, mode 600, and deletes it after the run; setup never copies a credential.

## Acceptance Criteria

- [ ] **AC1** Given a scenario with a fixture spec, when `eval_run.py setup --scenario <id> --dir <scratch>` runs, then `<scratch>.claude-config/skills/sdlc-studio/SKILL.md` exists, nothing is written under `<scratch>` beyond the fixture, no credential file is written, and stdout carries a worker command beginning `CLAUDE_CONFIG_DIR=<scratch>.claude-config`. Fails on: HEAD, which builds no config directory and prints no command
  - **Verify:** pytest tools/tests/test_lean_eval_isolation.py::EvalIsolationTests::test_setup_isolates_the_candidate_skill

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
