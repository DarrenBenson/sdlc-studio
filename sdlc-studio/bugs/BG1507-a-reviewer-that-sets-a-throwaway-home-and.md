# BG1507: A reviewer that sets a throwaway HOME and runs git config --global rewrites the operator's real git identity, because XDG_CONFIG_HOME still points at the real ~/.config

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/agents/sdlc-reviewer.md, .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md, .claude/agents/sdlc-reviewer.md, .claude/agents/sdlc-builder.md
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:50:13Z

## Summary

Several QA reviewer agents in runs ten to fifteen isolated a test run with `export HOME=<tmp>` (some also `XDG_DATA_HOME)` and then ran `git config --global user.name r|t|x` and `user.email r@x|t@e.com|r@e`. On a host that exports `XDG_CONFIG_HOME`=$HOME/.config, the throwaway HOME has no .gitconfig, so git writes the XDG file: the operator's real ~/.config/git/config. The operator's identity became t, then r, then x, from 2026-11-12 09:51 UTC; about 180 commits pushed to main since then carry a test identity, and the first v6.4.0 tag was made as 'x' before it was caught and remade. The test helper is already hermetic (tests/gitutil.py sets `GIT_CONFIG_GLOBAL`=/dev/null); the leak is in agents' ad-hoc command lines, and neither shipped agent template says how to isolate git. Restored by hand on 2026-11-16 with a backup at ~/.config/git/config.sdlc-agent-leak-2026-11-16.bak. Same class as the 2026-11-08 leak that wrote ~/.gitconfig.

## Steps to Reproduce

1. On a host with `XDG_CONFIG_HOME`=/home/<user>/.config and no ~/.gitconfig, run: export HOME=$(mktemp -d); git config --global user.name x
2. git config --file /home/<user>/.config/git/config user.name prints x.

## Proposed Fix

Two parts. (1) The agent templates tell a builder or reviewer that needs a git identity in a fixture to pass it with `-c user.name=... -c user.email=...` or to set `GIT_CONFIG_GLOBAL` to a file inside its throwaway directory, and never to run `git config --global`; redirecting HOME alone does not isolate git. (2) A deterministic guard, since a rule stated only in a template is weak (LL0027): the run records the operator's global git identity when it opens, and `sprint lane land` and `sprint close` refuse when it has changed, naming the file git now reads and the identity recorded.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Several QA reviewer agents in runs ten to fifteen isolated a test run with `export HOME=<tmp>` (some also `XDG_DATA_HOME)` and then ran `git config --global...

## Impact

An autonomous run silently rewrites the operator's global git identity, so every later commit and tag on every repository on the host is misattributed until someone notices; pushed history cannot be corrected on a trunk-based repo.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
