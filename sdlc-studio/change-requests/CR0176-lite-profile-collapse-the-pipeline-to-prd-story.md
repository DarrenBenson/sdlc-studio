# CR-0176: Lite profile: collapse the pipeline to PRD, story, implement for small repos

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Enhancement
> **Raised-by:** Lena Marsh (Product amigo)
> **Depends on:** none (independent of the schema tranche)

## Summary

A scale-down mode - a flag or project-level config setting - that collapses the pipeline to
PRD, story, implement, skipping epics and plans for small repos. The full pipeline remains
the default for larger work.

## Motivation

The process-ceremony objection is the most common reason a small project walks away: a
weekend-sized repo that adopts the full pipeline accumulates more workflow markdown than
source, which is indefensible to exactly the user the tool most wants (Maya, the primary
design persona - solo founder-engineer who wants discipline without ceremony; Trevor, the
negative persona, is the one who wants mandatory stage gates). Scope should serve the goal:
for a repo with a dozen stories, epic decomposition and per-story implementation plans add
tracking surface without adding discipline. The discipline that matters at that scale -
evidence, executable ACs, reconcile - survives intact in the lite profile.

## Scope

**In scope**

- Project-level setting (config, e.g. `profile: lite`) plus a per-invocation flag; `init`
  offers the choice.
- Lite pipeline: PRD (create or generate) -> stories (parented to the PRD directly, no epic
  layer) -> `code implement` (plan folded into the implement step, not a separate artefact).
- `status`, `hint`, `reconcile`, and `validate` all honour the profile: no nagging about
  missing epics/plans, no drift reports for layers that are switched off.
- Upgrade path: a lite project can promote to the full profile later (`project upgrade`
  inserts the epic layer above existing stories mechanically); one-way documented as
  lite-to-full only.
- Docs: getting-started names the two profiles and when to pick each.

**Out of scope**

- Removing TRD/TSD/personas from the full pipeline or making lite the default.
- A third intermediate profile; two is the offer.
- Schema changes; lite is a routing and validation profile over the same artefact schema
  (deliberately, so promotion is mechanical).

## Acceptance Criteria

- [ ] A lite-profile project runs PRD -> story -> implement with zero epic or plan artefacts
      created and zero warnings about their absence from status/hint/reconcile/validate.
- [ ] Executable AC verification (`verify_ac.py`) and reconcile work identically in lite
      (the discipline survives; the ceremony goes).
- [ ] `init` offers the profile choice; config documents it; the flag overrides per
      invocation.
- [ ] Promotion test: a lite fixture project upgrades to full, epics inserted above existing
      stories, reconcile clean afterwards.
- [ ] Workflow-markdown-to-source ratio demonstrably drops on the fixture (count artefact
      files lite vs full for the same story set; recorded in the CR on delivery).

## Dependencies

| Artefact | Relationship |
| --- | --- |
| None blocking | Independent of the schema tranche; can proceed in parallel |
| CR0177 | Consumer: positioning mentions lite as the small-repo answer |

## Effort

**M.** No schema work, but profile awareness touches status, hint, reconcile, validate, and
init, each with tests.

## Risk

Profile-conditional logic in four commands is a drift magnet: a future feature that forgets
the lite branch reintroduces nagging and erodes trust in the profile. Mitigation: a lite
fixture project in the test suite so every guard runs both profiles.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Lena Marsh (Product amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Lena Marsh (Product amigo) | Full scope drafted; lite keeps the discipline, drops the ceremony |
