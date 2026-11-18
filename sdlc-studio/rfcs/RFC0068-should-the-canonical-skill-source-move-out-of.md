# RFC-0068: Should the canonical skill source move out of .claude/skills/ to a harness-neutral path

> **Status:** Draft
> **Affects:** install.sh, install.ps1, tools/forward-port.sh
> **Date:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T15:25:16Z

## Summary

The canonical skill lives under `.claude/skills/sdlc-studio/` and CLAUDE.md sits at the repository root, which some reviewers read as a Claude Code dependency. CR0742 leaves the move out of scope because it affects the installers, the forward-port, the test suite's paths and every existing user's install, and asks for it to be assessed here.

## Design Options

- **Keep `.claude/skills/sdlc-studio/` and state in docs/harnesses.md why the path is where it is**
- **Move the source to a neutral path (for example `skills/sdlc-studio/`) and keep `.claude/skills/sdlc-studio` as a generated or linked copy for this repository's own dogfooding**
- **Move it and drop the `.claude` copy, updating the installers and the upgrade path for existing users**

## Recommendation

Assess the cost of option 2 against the installers, forward-port.sh, the tests' fixed paths and the upgrade path before choosing; until then option 1's explanation is enough.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Choose between: Keep `.claude/skills/sdlc-studio/` and state in docs/harnesses.md why the path is where it is, Move the source to a neutral path (for example `skills/sdlc-studio/`) and keep `.claude/skills/sdlc-studio` as a generated or linked copy for this repository's own dogfooding or Move it and drop the `.claude` copy, updating the installers and the upgrade path for existing users | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
