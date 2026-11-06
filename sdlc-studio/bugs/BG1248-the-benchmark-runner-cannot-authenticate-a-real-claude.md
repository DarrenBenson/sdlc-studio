# BG1248: The benchmark runner cannot authenticate a real Claude Code or Codex run once it empties their config directories, and it accepts a `--dest` inside a git work tree whose skills and repository the session then reaches

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** tools/bench/runner.py, tools/tests/test_bench_headless.py
> **Evidence:** run seven (RUN-01M6RAP7) US1128 review rounds 1 and 2, and the orchestrator's friction log (F11, F13)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:36:45Z

## Summary

Run seven, US1128 review rounds 1 and 2 and the orchestrator's friction log (F11, F13). Both must be fixed before RFC0062 Phase 2's real runs. (1) Authentication: the private, empty config directory drops each CLI's file login (`runner.py:377`), though `changelog.d/US1128.md:18` says a run "authenticates from what the environment exports". Claude Code keeps its login in `$CLAUDE_CONFIG_DIR/.credentials.json` (`~/.claude/.credentials.json` exists here, and `tools/eval_run.py:84,153` already tells the operator to copy it in by hand); with the private directory it authenticates only from an exported `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY`, and neither is exported here. Codex CLI 0.160.0 keeps its ChatGPT login in `$CODEX_HOME/auth.json` (`cli_auth_credentials_store` defaults to file); its environment routes are `OPENAI_API_KEY`, `CODEX_API_KEY` and `CODEX_ACCESS_TOKEN`, otherwise "no Codex credentials were found", so on a ChatGPT subscription every codex run is refused. Copilot CLI 1.0.91 authenticates through `gh` or a token, and OpenCode is untouched. It fails closed: no row is written. (2) Nested dest: `runner.py:367` checks only that the dest is empty. A probe with dest `<copy>/tools/bench/ws-nested` was accepted and wrote an arm-B row stamped measured with the pinned `skill_ref`, while `<copy>/.claude/skills/sdlc-studio` sat on the session's ancestor chain (Claude Code 2.1.318's bundled project walk collects `.claude/skills` from the cwd up to the git root inclusive). In round 1, `git rev-parse --show-toplevel` from such a workspace resolved to the enclosing repository, so an agent running with `bypassPermissions`, `--allow-all-tools` or `--auto` can commit or reset there, and `_GIT_ENV_VARS` (`runner.py:118-121`) drops an operator's `GIT_CEILING_DIRECTORIES` (probe: unset in the child), the one environment guard against that discovery. The changelog's "The session loads only the skill `prepare` installed, and none in arm B" (`changelog.d/US1128.md:12-13`) and the `isolate_skills` docstring (`runner.py:277`) are false on that path.

## Steps to Reproduce

1. With a Claude Code login in `~/.claude/.credentials.json` and neither `CLAUDE_CODE_OAUTH_TOKEN` nor `ANTHROPIC_API_KEY` exported, run one fixture through `tools/bench/runner.py run` for Claude Code: the session fails to authenticate and no row is written. Repeat for Codex on a ChatGPT login. 2. Run `tools/bench/runner.py run` with `--dest <repo>/tools/bench/ws-nested` and a fake CLI that records `git rev-parse --show-toplevel` and the `.claude/skills` directories on its ancestor chain: the run is accepted, the top level is the enclosing repository and the working tree's skill is reachable.

## Proposed Fix

Before the session, symlink only the operator's credential file into the private directory: `.credentials.json` for Claude Code and `auth.json` for Codex, resolved from the operator's `CLAUDE_CONFIG_DIR` or `CODEX_HOME` or their defaults. Never link the whole directory, so the skills stay out, and use a symlink rather than a copy, so a refresh-token rotation writes through instead of logging the operator out. Do not copy Copilot's `config.json`, whose skill directories are a skill source. When no credential exists, name the export a run needs in the refusal. Refuse a dest inside any git work tree (`git rev-parse --show-toplevel` from the dest's nearest existing ancestor) before anything is written, and stop dropping `GIT_CEILING_DIRECTORIES` (set it to the dest's parent). Pin both with a fake CLI that asserts the credential is reachable and the skills are not, and a nested-dest refusal, and correct the changelog and docstring claims.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run seven, US1128 review rounds 1 and 2 and the orchestrator's friction log (F11, F13).
- [ ] **AC2** The proposed fix lands, pinned by a test: Before the session, symlink only the operator's credential file into the private directory: `.credentials.json` for Claude Code and `auth.json` for Codex...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
