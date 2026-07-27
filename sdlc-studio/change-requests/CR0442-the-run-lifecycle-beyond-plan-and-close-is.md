# CR-0442: The run lifecycle beyond plan and close is undocumented: batch mutation, appetite and the rolling policy have no help page

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/SKILL.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (operator-raised, RFC0057 discussion); agent; skill v5.0.0

## Summary

help/sprint.md is 193 lines covering planning a sprint and closing it, and says nothing about living with one. Measured against the shipped surface: `batch add` and `batch drop` are mentioned zero times, `appetite` zero times, and the rolling multi-sprint policy once in passing. SKILL.md instructs an agent to read `help/{type}.md` for the command it was asked about, so an agent told to adjust a running sprint loads the page and finds the verbs absent - they are discoverable only by reading argparse or the source. The operator asks for a sprints page covering the plural, multi-sprint surface; the present gap is narrower and already real, and the two want the same home.

## Impact

Who: any operator or agent whose sprint meets reality, and every consuming project, since these verbs ship. What breaks: the adjustment an operator most often needs mid-sprint is the one the documentation does not admit exists, so work is dropped by hand-editing state or not adjusted at all, and a run diverges from its record. The same class as CR0439, where refine has no help page at all: the command that ships is not the command that is documented, and an agent following the router's own instruction lands on nothing. Documenting the shipped verbs is worth doing on its own; it also becomes the natural home for the multi-sprint surface RFC0057 and CR0441 describe, so the page should be written to be extended rather than replaced.

## Acceptance Criteria

- [ ] The run lifecycle beyond plan and close is documented: adding a unit to an open batch, dropping one with its required reason, stopping a run, and what each does to the run record.
- [ ] The appetite is documented - what it bounds, where it is set, and that it is fixed once the plan is written until CR0441 changes that.
- [ ] The rolling multi-sprint policy is documented as the multi-sprint facility that exists today, including that it regenerates the plan at each boundary rather than queueing plans, so a reader looking for a sprint queue finds the current answer and the reasoning rather than silence.
- [ ] Every verb the page documents is checked against the shipped command surface, so a documented verb that no longer exists, or a shipped verb the page omits, is caught rather than left to drift.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (operator-raised, RFC0057 discussion) | Raised |
