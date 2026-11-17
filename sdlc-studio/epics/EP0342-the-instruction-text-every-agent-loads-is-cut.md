# EP0342: The instruction text every agent loads is cut to what current models need, every gated rule kept

> **Status:** Draft
> **Derived Point Total:** 12
> **Parent:** CR0700
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0700. Delivers the work CR0700 requested.

## Story Breakdown

- [ ] [US1243: The prompt audit of the instruction files is committed, each finding dispositioned and each kept gate named](../stories/US1243-the-prompt-audit-of-the-instruction-files-is.md)
- [ ] [US1244: This repository's always-loaded instruction files take the accepted cuts, sizes reported before and after](../stories/US1244-this-repository-s-always-loaded-instruction-files-take.md)
- [ ] [US1245: The shipped instruction templates and SKILL.md take the accepted cuts and reach projects on project upgrade](../stories/US1245-the-shipped-instruction-templates-and-skill-md-take.md)
- [ ] [US1246: The rendered lane brief and review brief take the accepted cuts, with every gated rule's text still present](../stories/US1246-the-rendered-lane-brief-and-review-brief-take.md)

## Acceptance Criteria (Epic Level)

- [ ] The audit report, run with Opus 5.5 as the target model, is committed as evidence, each finding with file:line, pattern, why it is obsolete and confidence
- [ ] Each finding is dispositioned as changed, removed or kept, and each kept rule names the gate or current failure it guards
- [ ] The accepted changes land as sized stories, and the shipped template changes reach consuming projects through project upgrade
- [ ] No rule a gate enforces loses the text that tells an agent about it, and AGENTS.md stays within its budget (tools/`check_budgets.py)`
- [ ] The token size of each changed always-loaded file is reported before and after, and the next run's priced tokens per point is reported against run nine's

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
