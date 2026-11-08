# BG1291: The benchmark runner refuses a Claude Code run that authenticates from `ANTHROPIC_AUTH_TOKEN`, Bedrock or Vertex, and accepts a `--dest` whenever git errors

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/bench/runner.py, tools/tests/test_bench_headless.py
> **Evidence:** BG1248 review round 1 (qa-seat-BG1248-r1), probes through `runner.py run`
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:55:23Z

## Summary

From BG1248's independent review (qa-seat-BG1248-r1, round 1), both [new] and non-blocking. (1) `LOGIN_EXPORTS["claude"]` (`tools/bench/runner.py:266`) names only `CLAUDE_CODE_OAUTH_TOKEN` and `ANTHROPIC_API_KEY`, so a run with no login file that authenticates from `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_USE_BEDROCK` or `CLAUDE_CODE_USE_VERTEX` is refused, and the comment at :265 and BG1248's fragment over-claim 'the exports that CLI authenticates from'. (2) `enclosing_work_tree` (`runner.py:341`) fails open on any non-zero `git rev-parse --show-toplevel`: a dest at `<repo>/.git/ws`, or under a directory whose `.git` file points nowhere, is accepted. Repo-only tooling.

## Steps to Reproduce

Run `tools/bench/runner.py run` with no login file and only `ANTHROPIC_AUTH_TOKEN` exported: exit 1 'none of `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_API_KEY` is exported'. Run it with `--dest <repo>/.git/ws`: accepted.

## Proposed Fix

Add the three variables to the Claude entry and reword the comment and fragment to 'the exports this runner accepts'; refuse a dest when `git rev-parse` errors for any reason other than 'not a git repository'.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From BG1248's independent review (qa-seat-BG1248-r1, round 1), both [new] and non-blocking.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run `tools/bench/runner.py run` with no login file and only `ANTHROPIC_AUTH_TOKEN` exported: exit 1 'none of `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_API_KEY` is...
- [ ] **AC3** The proposed fix lands, pinned by a test: Add the three variables to the Claude entry and reword the comment and fragment to 'the exports this runner accepts'; refuse a dest when `git rev-parse` errors...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
