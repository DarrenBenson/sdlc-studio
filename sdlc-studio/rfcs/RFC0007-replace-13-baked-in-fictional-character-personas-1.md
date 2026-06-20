# RFC-0007: Replace 13 baked-in fictional-character personas (~1680 lines) with template plus generate-on-demand

> **Status:** Accepted
> **Priority:** Medium
> **Author:** Adversarial Audit
> **Date:** 2026-06-20
> **Spans:** sdlc-studio skill
> **Related:** RV0002 (audit run)
> **Supersedes / Superseded by:** --

## Summary

templates/personas/ ships 13 full fictional characters (~1680 lines of invented biography) sharing one scaffold, baked into every install rather than a single template plus a generator - contrary to the skill's own Create-vs-Generate philosophy.

## Context & Problem

templates/personas/ ships 13 complete fictional characters under stakeholders/ and team/, ~108-112 lines each, ~1680 lines total, each near-identical in structure (Quick Reference, Identity, Personality Traits, ... Backstory) populated with invented prose (e.g. Marcus 'lived through the JS framework wars', Kai 'graduated from a bootcamp two years ago'). They are wired in as archetypes (reference-persona.md:39-67) and used by consult/chat, but as full prose characters in every install rather than a single template plus a generator. persona-template.md (108 lines) is the same scaffold; a short archetype seed list already exists at reference-persona.md:42-66.

## Design Options

### Option A - act on the finding

Replace the 13 baked-in character files with persona-template.md plus the existing short archetype seed list (role + one-line disposition) and let 'persona create' generate the full character on demand for the consuming project. If pre-built archetypes are a deliberate product decision that is a legitimate RFC outcome, but the trade (1680 lines of invented backstory in every install vs generate-on-demand) should be an explicit call, not the default.

### Option B - status quo

Keep the current behaviour and accept the trade-off described above.

## Recommendation

TBD - pending the Open Decision below.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Act on this finding or keep status quo | Option A / Option B | Operator | spike or operator call | Resolved |

## Evidence

`templates/personas/stakeholders/**` and `templates/personas/team/**` = 13 character files, ~1680 lines, sharing the persona-template.md (108-line) scaffold; referenced reference-persona.md:39-67

## Impact

Every install carries ~1680 lines of fictional biography most consuming projects will replace or ignore; the shared scaffold means a persona-format change must be propagated 13 times. Removing them aligns personas with the skill's Create-vs-Generate philosophy and cuts the templates corpus materially. Token/repo-weight risk medium.

## Decision

**Outcome:** Accepted (Option A)

**Rationale:** Low-effort alignment win with the Create-vs-Generate philosophy; deletion must follow a confirmed generator path, not precede it.

**Spawned CRs:** One CR: confirm `persona create` generates from template + seed, remove the 13 baked character files, wire reference-persona to the seed, add a migration note. Created when picked up.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (rfc-decide session) | Accepted in the RFC decision session - Accepted (Option A) |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: over-engineering) |
