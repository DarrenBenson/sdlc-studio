# CR-0352: migrate --apply should seed a missing AGENTS.md rather than report it as a human task

> **Status:** In Progress
> **Decomposed-into:** EP0096
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/templates/agent-instructions.md
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`migrate` is documented as the front door for 'bring this project up to date', and it orchestrates `project_upgrade`, which calls `validate.check_instructions`. But the result is only ever a `manual` item reading 'refresh from templates/agent-instructions.md, preserving project sections'. Nothing writes. `init` is the only command that seeds the file, and `init` is for an empty project - so the most common brownfield case, a repo adopting the skill with no AGENTS.md at all, produces an ERROR from the hygiene check and a hand task from the command whose whole purpose is to bring the project up to date. The asymmetry is odd on its own terms: migrate --apply already writes the deterministic safe set (conventions, version, sizing), and seeding a file that does not exist is strictly safer than editing artefacts that do.

## Impact

A brownfield adopter runs migrate, is told AGENTS.md is missing, and must find the template and fill it in by hand - or, more likely, does not, and works without the instructions file that establishes how the project is meant to be run. The agent instructions are what make the discipline hold across sessions and tools, so a project that skips them gets the artefact tree without the working model.

## Acceptance Criteria

- [ ] migrate --apply CREATES AGENTS.md from templates/agent-instructions.md when none exists, filling the placeholders it can derive and leaving the rest marked
- [ ] an AGENTS.md that exists but drifts is reported with the specific rules it fails and an offered merge, never silently overwritten - project sections survive
- [ ] a CLAUDE.md that duplicates rather than importing @AGENTS.md is reported with the one-line pointer that replaces it
- [ ] the dry run states exactly what it would write, so seeding is visible before it happens

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
