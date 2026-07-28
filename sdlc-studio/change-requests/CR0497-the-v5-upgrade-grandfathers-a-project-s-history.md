# CR-0497: The v5 upgrade grandfathers a project's history silently, so every exemption it grants is a number with no record of what it forgave or why

> **Status:** Proposed
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5; human; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-migrate.md, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py
> **Priority:** High
> **Type:** enhancement
> **Size:** L

## Summary

A project adopting v5 arrives with history that predates every gate v5 enforces: units closed before retros were mandated, stories Done before the two-role rule, bugs fixed before the criteria floor, artefacts written before provenance was stamped. v5 handles that with grandfathering - `close_owed.py baseline` snapshots the terminal set, and `conformance.adopt_after`, `provenance.adopt_after` and `engagement_floor.adopt_after` are id cutoffs in `.config.yaml`.

The mechanism is right. What is missing is the record. Every one of those exemptions is applied as a bare number, and the reasoning - what cohort it covers, what era it belongs to, why that era could not have met the rule, what would re-arm it - survives only if a human writes a YAML comment. In this repo those comments exist because they were hand-written under pressure, one incident at a time. A project upgrading tomorrow gets the numbers and none of the prose.

Two consequences follow. The operator is never ASKED: `migrate --apply` writes the deterministic set, and a grandfathering decision is a judgement about the project's own history that the tool cannot make. And months later nobody can tell an exemption that was reasoned from one that was a default - which is the same failure as a threshold whose restore condition nothing reads (CR0496).

The live instance is close-owed. 59 delivery units read as owing a sprint close; 54 of them were covered by retros that simply never named their unit ids, and the correct repair was to name them. Had they genuinely been pre-mandate work, the only discharge available would have been `close_owed.py baseline`, which forgives silently and writes no explanation anywhere an operator will read.

## Impact

Every project that adopts or upgrades to v5 carries a set of unexplained exemptions from that day forward. An exemption nobody can audit is indistinguishable from a gate that was never switched on, and a permanently undischargeable advisory trains operators to scroll past the surface that exists to be noticed. The cost lands hardest on the projects with the most history - exactly the ones the upgrade path is for.

## Acceptance Criteria

- [ ] The upgrade ENUMERATES the grandfathering it proposes before applying any of it: for each gate, the cohort it would exempt, its size, the date range it spans, and what the project would be held to afterwards. Nothing about a project's own history is decided for the operator.
- [ ] Each granted exemption writes a durable artefact, not a config comment: what was exempted, the era and why that era could not have met the rule, who confirmed it, and the condition that would re-arm it. A machine-readable condition, on the same terms as CR0496.
- [ ] A pre-adoption cohort is discharged by a RECORD rather than by a baseline file. A stub retro naming the cohort and stating that these units closed before the close-down was mandated satisfies `close_owed` the same way a real retro does, and reads as what it is - a stub - rather than as a sprint that happened.
- [ ] A stub is visibly a stub. It states it accounts for no delivery, carries no lessons and contributes nothing to velocity, and the accuracy and velocity paths exclude it from both sides rather than recording it as a sprint with zero cost.
- [ ] The upgrade REPORTS what it grandfathered at the end, and `status` can show the standing exemptions and their re-arm conditions on demand, so an exemption granted at adoption is visible a year later without reading YAML.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Related: CR0496 (a restore condition written as prose no tool reads). AC2 here deliberately reuses its machine-readable-condition requirement rather than inventing a second form - two representations of one rule diverge, and the looser one is the one that runs (L-0249). |
