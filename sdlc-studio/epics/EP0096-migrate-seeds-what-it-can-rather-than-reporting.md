# EP0096: migrate seeds what it can rather than reporting it as a human task

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0352
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0352. Delivers the work CR0352 requested.

## Story Breakdown

- [ ] [US0293: migrate --apply seeds a missing AGENTS.md and CLAUDE.md from the template, preserving project sections](../stories/US0293-migrate-apply-seeds-a-missing-agents-md-and.md)
- [ ] [US0294: The hygiene check reports a missing instructions file as seedable rather than as an error](../stories/US0294-the-hygiene-check-reports-a-missing-instructions-file.md)

## Acceptance Criteria (Epic Level)

- [ ] migrate --apply CREATES AGENTS.md from templates/agent-instructions.md when none exists, filling the placeholders it can derive and leaving the rest marked
- [ ] an AGENTS.md that exists but drifts is reported with the specific rules it fails and an offered merge, never silently overwritten - project sections survive
- [ ] a CLAUDE.md that duplicates rather than importing @AGENTS.md is reported with the one-line pointer that replaces it
- [ ] the dry run states exactly what it would write, so seeding is visible before it happens

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
