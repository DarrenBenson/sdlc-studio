# EP0166: The persona layer becomes load-bearing: the registry is resolved by the path that mints work, and the PRD names it

> **Status:** Draft
> **Parent:** CR0426
> **Derived Point Total:** 12
> **Parent:** CR0425
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0425. Delivers the work CR0425 requested.

## Story Breakdown

- [ ] [US0447: A shared reader parses the design-persona registry into Primary, Secondary and Negative with their card paths](../stories/US0447-a-shared-reader-parses-the-design-persona-registry.md)
- [ ] [US0448: artifact.py resolves --persona through the registry: the declared Primary by default, a warning on an unregistered name, a refusal under strict](../stories/US0448-artifact-py-resolves-persona-through-the-registry-the.md)
- [ ] [US0449: The batch and refine minting paths resolve the persona the same way, so the commands that mint most stories are covered too](../stories/US0449-the-batch-and-refine-minting-paths-resolve-the.md)
- [ ] [US0450: The PRD Target Users section names the registry's Primary, Secondary and Negative personas and points at the registry](../stories/US0450-the-prd-target-users-section-names-the-registry.md)
- [ ] [US0451: personas.md is labelled a legacy appendix whose still-true content is folded into or pointed at the registry](../stories/US0451-personas-md-is-labelled-a-legacy-appendix-whose.md)

## Acceptance Criteria (Epic Level)

- [ ] Make artifact.py resolve --persona against personas/index.md, defaulting to the declared Primary when omitted and warning (or refusing under strict) on a name not in the registry, so the pipeline that actually mints every story performs persona selection.

### From CR0426

- [ ] Rewrite the PRD Target Users section to name the registry's Primary/Secondary/negative personas with a pointer to personas/index.md, and demote personas.md to an explicitly-labelled legacy appendix (or fold its still-true content into the registry).

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
