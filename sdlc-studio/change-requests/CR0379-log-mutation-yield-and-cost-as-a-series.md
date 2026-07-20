# CR-0379: log mutation yield and cost as a series, so the gate can be judged on evidence rather than belief

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py,.claude/skills/sdlc-studio/scripts/sprint_report.py
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Nothing records what a mutation run COST and what it FOUND, so the question "is this gate worth its wall-clock" can only be answered from memory and prose scattered across retros. Asked directly by the operator at the RUN-01KY03GS close, the best available answer had to be reconstructed by hand: RETRO0060 records 2 test gaps found, this run produced 3 survivors that became BG0232 and BG0233, and the per-run cost had to be inferred from timeouts and timestamps. A gate that cannot show its yield gets cut on a bad day and kept on a good one, which is the opposite of an evidence-driven decision. Every input already exists at the point of the run - mutants applied, killed, survived, un-checked beyond the ceiling, wall-clock, and the artefacts subsequently filed from the survivors.

## Impact

This is the measurement that decides whether the most expensive close-time step keeps its place, and it is the one thing the close does not record. Without it the mutation gate is judged on the most recent run rather than on its record, so a single badly-scoped run - like this sprint first attempt, 40 minutes producing nothing - reads as evidence against the technique when it was evidence against the scoping. With it, the trade is legible: this project appears to find 2-3 real test gaps per sprint at roughly 10 minutes when correctly scoped, several of which had already survived the full suite, per-story AC verification and two adversarial review rounds. RFC0048 D2 (retire a test by measured kill yield) is also unanswerable until this series exists, so the series unblocks a decision already recorded as deferred.

## Acceptance Criteria

- [ ] each mutation run records applied, killed, survived, un-checked-beyond-ceiling and wall-clock to a series file, not only to stdout
- [ ] a survivor that is later filed as an artefact links back to the run that found it, so yield is counted in artefacts rather than in survivor counts
- [ ] an equivalent mutant recorded as such is excluded from yield, since counting it would overstate the gate value
- [ ] the sprint report renders cost against yield for the run and the trailing history, so the trade is visible at the close where the decision is actually taken
- [ ] a run killed or timed out records that it produced no evidence, and is never readable as a clean run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
