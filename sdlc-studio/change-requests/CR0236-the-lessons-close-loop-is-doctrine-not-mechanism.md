# CR-0236: The lessons close-loop is doctrine, not mechanism: gate the summary at close and the read at start

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren; human; v3

## Summary

Operator directive 2026-07-13: lessons and retro findings must be summarised at the end of every sprint and read at the beginning of the next one. That is already what reference-sprint.md section 7 describes as a five-step loop, but only ONE step is mechanically enforced. gate --require-retro fails loud without the retro artefact; nothing enforces the other four. Regenerating LESSONS-SUMMARY.md from the still-valid lessons, revalidating open lessons, and reading the summary plus lessons recall at sprint start are all prose that an agent under effort pressure simply skips. This is the same class of defect as BG0111, where lessons/_index.md promised that additions are blessed into the next release and no mechanism performed the blessing: a documented intention with no implementation. The sprint close must refuse to complete with a stale summary, and the sprint plan must surface the summary as an input rather than trusting the agent to have read it.

## Acceptance Criteria

- [ ] The sprint close gate fails loud when LESSONS-SUMMARY.md is stale relative to the lessons log (a lesson added or closed since the summary was last regenerated), the same way the retro gate fails loud on a missing retro
- [ ] sprint plan emits the still-valid lessons digest as part of its output, so the plan an agent reads at sprint start CONTAINS the lessons rather than pointing at a file it may not open
- [ ] The revalidate step is gated too: the close cannot complete while an open lesson has gone stale past its validity horizon without an explicit close or an extension
- [ ] A regression test proves the close gate exits 1 on a stale summary, and 0 once the summary is regenerated
- [ ] Mutation-checked: removing the staleness check turns a test red

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Darren | Raised: operator directive - lessons must be summarised at sprint close and read at the next sprint's start, enforced mechanically rather than by doctrine |
