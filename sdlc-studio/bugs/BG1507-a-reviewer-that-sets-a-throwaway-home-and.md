# BG1507: A reviewer that sets a throwaway HOME and runs git config --global rewrites the operator's real git identity, because XDG_CONFIG_HOME still points at the real ~/.config

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/agents/sdlc-reviewer.md, .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md, .claude/agents/sdlc-reviewer.md, .claude/agents/sdlc-builder.md, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py, .claude/skills/sdlc-studio/scripts/tests/test_git_identity_guard.py, changelog.d/BG1507.md
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:50:13Z

## Summary

Several QA reviewer agents in runs ten to fifteen isolated a test run with `export HOME=<tmp>` (some also `XDG_DATA_HOME)` and then ran `git config --global user.name r|t|x` and `user.email r@x|t@e.com|r@e`. On a host that exports `XDG_CONFIG_HOME`=$HOME/.config, the throwaway HOME has no .gitconfig, so git writes the XDG file: the operator's real ~/.config/git/config. The operator's identity became t, then r, then x, from 2026-11-12 09:51 UTC; about 180 commits pushed to main since then carry a test identity, and the first v6.4.0 tag was made as 'x' before it was caught and remade. The test helper is already hermetic (tests/gitutil.py sets `GIT_CONFIG_GLOBAL`=/dev/null); the leak is in agents' ad-hoc command lines, and neither shipped agent template says how to isolate git. Restored by hand on 2026-11-16 with a backup at ~/.config/git/config.sdlc-agent-leak-2026-11-16.bak. Same class as the 2026-11-08 leak that wrote ~/.gitconfig.

## Steps to Reproduce

1. On a host with `XDG_CONFIG_HOME`=/home/<user>/.config and no ~/.gitconfig, set HOME to a new empty directory made with mktemp -d, then run git config --global user.name x
2. git config --file /home/<user>/.config/git/config user.name prints x.

## Proposed Fix

Two parts. (1) The agent templates tell a builder or reviewer that needs a git identity in a fixture to pass it with `-c user.name=... -c user.email=...` or to set `GIT_CONFIG_GLOBAL` to a file inside its throwaway directory, and never to run `git config --global`; redirecting HOME alone does not isolate git. (2) A deterministic guard, since a rule stated only in a template is weak (LL0027): the run records the operator's global git identity when it opens, and `sprint lane land` and `sprint close` refuse when it has changed, naming the file git now reads and the identity recorded.

## Acceptance Criteria

- [ ] **AC1** Given the shipped builder and reviewer cards and this repository's installed copies, when each is read, then it tells the agent to give a fixture its git identity with `-c user.name` and `-c user.email` or a `GIT_CONFIG_GLOBAL` file inside its throwaway directory, never to write the global git configuration, and that redirecting HOME alone does not isolate git. Fails on: either card or either copy silent on git isolation.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::AgentDefinitionTests::test_both_cards_forbid_writing_the_global_git_identity
  - **Verified:** yes (2026-11-18)
- [ ] **AC2** Given a run opened while the global git identity was one name and email, and that identity then rewritten in the file git reads, when `sprint.py lane land` runs, then it refuses before committing or moving main, naming the file git now reads, the identity recorded at open and the identity found. Fails on: a unit landed under an identity an agent wrote.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_git_identity_guard.py::GitIdentityGuardTests::test_lane_land_refuses_when_the_global_identity_changed_since_the_run_opened
  - **Verified:** yes (2026-11-18)
- [ ] **AC3** Given the same changed identity, when `sprint.py sprint close` runs, then it refuses with the same three facts and the run stays open. Fails on: a run closing over commits made under the wrong identity.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_git_identity_guard.py::GitIdentityGuardTests::test_sprint_close_refuses_when_the_global_identity_changed_since_the_run_opened
  - **Verified:** yes (2026-11-18)
- [ ] **AC4** Given a run whose recorded identity still matches the one git reads, and a second run opened where no global identity is set at all, when `lane land` and `sprint close` run, then neither is refused on identity; the fixtures point `GIT_CONFIG_GLOBAL` at a file of their own and never touch the host's. Fails on: the guard refusing an unchanged identity, or a test of the guard writing the operator's real configuration.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_git_identity_guard.py::GitIdentityGuardTests::test_an_unchanged_or_unset_identity_lands_and_closes
  - **Verified:** yes (2026-11-18)

## Impact

An autonomous run silently rewrites the operator's global git identity, so every later commit and tag on every repository on the host is misattributed until someone notices; pushed history cannot be corrected on a trunk-based repo.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
