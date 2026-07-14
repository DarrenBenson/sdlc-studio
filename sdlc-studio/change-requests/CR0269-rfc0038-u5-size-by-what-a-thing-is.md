# CR-0269: RFC0038 U5: size by what a thing IS - T-shirt on containers, points on delivery units, and a CR must decompose before it can be planned

> **Status:** Proposed
> **Priority:** P1
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/core/cr.md, .claude/skills/sdlc-studio/scripts/file_finding.py
> **Depends on:** CR0270
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Operator decision. Points belong on the thing that is DELIVERED and MEASURED. A T-shirt belongs on the CONTAINER that must be decomposed first. A CR is a REQUEST - it is not a unit of work until someone breaks it down, and pointing it is guessing at a shape that does not exist yet.

THIS PROJECT ALREADY PREACHES THIS AND DOES NOT DO IT. BG0132 established that only STORIES carry executable acceptance criteria - a CR ACs are prose, and its Done is therefore gated on nothing. `sprint plan` nags about it on every run ("decompose into stories - only a story Done is gated on executable ACs"). We have never once complied: every CR goes straight to a subagent as a single unit. The doctrine says CRs become stories; the practice says CRs are delivered whole. The sizing question is simply where that contradiction finally surfaced.

THE VOCABULARY, BY WHAT A THING IS:

| level | size | why |
| Epic | T-shirt (S/M/L/XL) | a container, sized before its stories exist |
| CR | T-shirt (S/M/L/XL) | a REQUEST, sized before it is broken down |
| Story | Points (Fibonacci) | the delivery unit - measured, and gated on executable ACs |
| Bug | Points (Fibonacci) | delivered directly; it is not a container |

AND IT IS THE SAME LEVER AS THE ABOVE-8 SPLIT RULE, PULLED FROM THE OTHER END. CR0266 as a single 8-point unit is one big job. Decomposed, it is three stories of 3+3+2 - smaller, more uniform, each measured separately. RFC0038 proved that counting is exactly as good as the units are uniform (they vary 5.5x today), and that the estimate breaks above 8. Forcing a CR through decomposition is how units get small enough for the estimate to be worth having.

HONEST CAVEAT, STATED RATHER THAN INHERITED. The r = 0.68 evidence in RFC0038 comes from CR-sized and BUG-sized units. Applying points to STORY-sized units is an extrapolation - a reasonable one, since the scale was most stable at 2-8 and stories are smaller - but there are ZERO story-level actuals. It must be re-validated once story telemetry exists, and until then the confidence is borrowed, not earned.

## Impact

The delivery workflow, not just the templates. Every CR gains a decomposition step, and every story becomes a measured unit gated on executable acceptance criteria - which is what the project has claimed to do since BG0132 and has never done.

**Points:** 5

## Acceptance Criteria

- [ ] A CR carries a T-shirt `Size:` (S/M/L/XL), not points. An epic likewise (CR0268). A story and a bug carry Points on the modified Fibonacci scale.
- [ ] `sprint plan` REFUSES to plan a CR that has not been decomposed into stories, naming it and giving the command that decomposes it. A CR is not a unit of work until it has been broken down.
- [ ] A story carries executable acceptance criteria and its Done is gated on them passing, as BG0132 established. This is the point of decomposing: it is what makes Done checkable rather than asserted.
- [ ] Velocity is measured in story points delivered, from stories and bugs. A T-shirt size is never summed into a velocity figure, because it is not a measurement.
- [ ] The story-level correlation is re-validated against actuals once story telemetry exists, and the RFC0038 evidence is not silently extended to a unit size it never measured.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
