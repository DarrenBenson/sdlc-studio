# BG0809: install.sh --local rewrites every personal copy of the skill, and the copy it installs is one Claude Code does not load

> **Status:** Open
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** install.sh, tools/tests/test_install_sweep.py, changelog.d/BG0809.md
> **Severity:** Medium
> **Points:** 2

## Summary

`install.sh --local` ends with a sweep that walks the GLOBAL and local skill directory of every target (install.sh 490-532) and replaces any sdlc-studio copy not newer than the one installed. A user who pins a release in one project therefore moves the personal copy every other project loads. And Claude Code loads a personal skill ahead of a project skill of the same name (its documented load order: enterprise, personal, project), so when a personal copy exists the project pin is shadowed and the installer's success line is not true of what Claude Code will run.

## Steps to Reproduce

Read install.sh `sweep_stale`: `for scope in global local` over `$ALL_TARGETS`, with only a downgrade guard. Reproduced 2026-09-27 in a scratch project: `install.sh --local --dry-run --from <skill>` prints '[dry run] would refresh: /home/darren/.claude/skills/sdlc-studio (6.0.0-rc.1 -> local:6.0.0-rc.1)' and '... /home/darren/.config/opencode/skills/sdlc-studio (5.1.0 -> local:6.0.0-rc.1)'. Load order: code.claude.com/docs/en/skills.md#load-order-by-location.

## Proposed Fix

Under `--local`, sweep only the local scope; when a personal Claude Code copy exists, print that Claude Code will load it ahead of the project copy, naming both paths and their versions.

## Acceptance Criteria

- [ ] Given a personal copy at `$HOME/.claude/skills/sdlc-studio`, when `install.sh --local --from <dir>` runs in a project, then the personal copy is byte-identical afterwards and the project copy is installed. Fails on: HEAD's sweep, which rewrites a personal copy of the same or an older version, so pinning a candidate in one project moves every project
- [ ] Given that personal copy, when `install.sh --local --target claude` completes, then it prints that Claude Code loads the personal copy ahead of the project copy, naming both paths and versions. Fails on: HEAD, which reports success for a copy Claude Code will not load

## Notes

Pre-existing, not a v6 regression, so cuttable to v6.1. Measured while planning the website soak: the sweep is proven from the code; the load order is from Claude Code's documentation, and the soak's first step confirms it on this machine. It bites exactly the user the rc.1 notes invite to 'try the candidate'. Product view: in Sprint 6 only if capacity allows; otherwise file it and disclose it in the 6.0.0 known issues.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (BG0809) |
