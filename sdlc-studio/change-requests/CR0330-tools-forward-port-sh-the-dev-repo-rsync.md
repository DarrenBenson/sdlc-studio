# CR-0330: tools/forward-port.sh: the dev-repo rsync to the installed copy as a guarded one-liner

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** tools/forward-port.sh, AGENTS.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; seams-sprint retro RUN-01KXPA4N

## Summary

Dev-repo-only convenience with a safety edge: a checked-in tools/forward-port.sh wrapping the canonical rsync (repo skill tree -> ~/.claude/skills/sdlc-studio, -rc --delete, .local and `__pycache__` excluded), refusing to run FROM an installed copy or TOWARD the repo (the BG0100 direction), printing the dry-run diff first with a --yes to apply. AGENTS.md points at it.

## Impact

The forward-port rsync (with its exact exclude flags) was hand-typed four times today; a wrong --delete without the .local exclude would destroy the installed copy's local state, and BG0100 already records what a wrong direction does.

## Acceptance Criteria

- [ ] The script runs the canonical rsync with the exact exclusions, dry-run by default, --yes to apply; reversed direction or a non-dev-repo cwd is refused
- [ ] AGENTS.md's forward-port note references the script instead of an inline rsync incantation

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
