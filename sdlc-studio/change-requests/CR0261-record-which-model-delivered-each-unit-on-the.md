# CR-0261: Record which model delivered each unit, on the artefact and in the committed history

> **Status:** Complete
> **Size:** S
> **Priority:** P2
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/templates/core/story.md
> **Depends on:** CR0263
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

telemetry.py already captures a model per unit (15 records carry claude-opus-4-8), but it goes nowhere durable. The model is not on the artefact - you cannot read a bug and see what built it. It is not in the committed history - VELOCITY.md and the retro accuracy block carry seed, estimate, actual, ratio and wall-clock, but no model column. And telemetry.jsonl itself is gitignored, so on a fresh clone the attribution is gone entirely. This matters for three separate reasons. (1) Provenance: which model delivered a change is CAB-grade audit information, and the project sells auditability. (2) Calibration: cost per unit is meaningless without knowing which model paid it, so the whole velocity history is currently comparing numbers from an unstated model - and the moment a second model is used, the history silently mixes them. (3) The benchmark: comparing harness performance across models is the point of the benchmark workstream, and it needs exactly this field. Depends on the .local/ durability defect being fixed first, or the field will be recorded somewhere that does not survive a clone.

## Impact

Every unit, retroactively. Without it the velocity history cannot survive a model change: a sprint delivered by a smaller model would land in the same average as one delivered by a larger, and the mean would describe nothing. It also blocks the routing work - a router cannot be validated against actuals that do not say which model produced them.

**Effort:** S

## Acceptance Criteria

- [ ] A delivered unit records the model that delivered it, on the artefact itself, so a reader of the bug or story can see it without the telemetry log.
- [ ] The committed velocity history and the retro accuracy table carry a model column, and a sprint that mixed models says so rather than averaging them into one meaningless figure.
- [ ] An accuracy or velocity figure computed across two different models is either segmented by model or refused, never silently averaged.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
