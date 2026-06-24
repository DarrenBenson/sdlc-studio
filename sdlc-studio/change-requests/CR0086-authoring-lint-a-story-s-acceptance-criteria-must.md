# CR-0086: authoring lint - a story's acceptance criteria must be satisfiable within its own epic

> **Status:** Complete
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement

## Summary

Two foundation stories carried acceptance criteria for functionality owned by **later**
epics: US0002 (auth middleware, EP0001) asserted *"a valid account token resolves a
userId"* - accounts are EP0006; US0018 (list create, EP0004) asserted *"items inherit
list ownership"* - items are EP0003. Such stories are **structurally un-Done-able in
their own epic**: their ACs cannot pass until a downstream epic ships. The field agent
called this *"the single most useful defect this exercise found"*. Add an authoring-phase
check that flags an AC referencing a capability owned by a downstream (not-yet-delivered)
epic, so a story's ACs are satisfiable within its own epic.

## Problem

From the reflection (verbatim): *"US0002 'valid account token resolves userId' (accounts
= EP0006) and US0018 'items inherit list ownership' (items = EP0003). So those stories
are structurally un-Done-able in this tranche. Yes - I'd rather these were split at
authoring time: a story's ACs should be satisfiable within its own epic. That's an
authoring-phase rule the skill could lint for."*

When stories are fanned out per epic, an agent authoring epic E can write an AC that
quietly depends on epic F's capability. Nothing flags it, so the contradiction only
surfaces at implementation as an un-passable AC (and tempts a false `Done`, the symptom
CR0084 catches downstream). Catching it at authoring is cheaper and keeps the backlog
honest - it also sharpens RFC0019's reviewable-backlog output.

## Proposed Changes

### Item 1: Cross-epic AC dependency check

**Priority:** Medium
**Effort:** 2

A check (in `validate`, and run by the authoring loop's closing consistency pass) that
flags an AC whose subject maps to a capability owned by a later epic in the dependency
order. Heuristic and advisory: match AC nouns/verbs against other epics' titles/scope and
the PRD feature-to-epic map; report "US0002 AC references 'account token', owned by EP0006
(downstream)" for a human to split or re-scope. Never auto-edits.

### Item 2: Remediation guidance

**Priority:** Low
**Effort:** 1

The finding suggests the fix: move the AC to the owning epic's story, or split the story.
Consistent with the project's "checks emit remediation, not just findings" principle
(CR0025).

## Acceptance Criteria

- [x] `validate` flags an AC that references a capability owned by a downstream epic
      (per the epic dependency order / PRD feature map), advisory, naming the owning epic
- [x] the authoring loop (RFC0019) runs the check in its closing consistency pass
- [x] the check never auto-edits; it emits remediation (split / re-scope to owning epic)
- [x] false-positive tolerance documented (heuristic match); CHANGELOG `[Unreleased]`
      entry same commit (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
