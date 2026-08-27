# EP0230: The planner answers whether a batch is parallelisable, rather than which files collide

> **Status:** Draft
> **Derived Point Total:** 12
> **Parent:** CR0530
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0530. Delivers the work CR0530 requested.

## Story Breakdown

- [ ] [US0745: `sprint breakdown` reports the number of INDEPENDENT components over the declared Affects graph](../stories/US0745-sprint-breakdown-reports-the-number-of-independent-components.md)
- [ ] [US0746: It reports the CONCENTRATION: the largest component in units and points, and its share of the batch](../stories/US0746-it-reports-the-concentration-the-largest-component-in.md)
- [ ] [US0747: The two measures are distinguished in the wording, because they answer different questions](../stories/US0747-the-two-measures-are-distinguished-in-the-wording.md)
- [ ] [US0748: A runbook row names the command, so the parallelisable question has a command behind it](../stories/US0748-a-runbook-row-names-the-command-so-the.md)
- [ ] [US0749: The `--agentic` safety rule is UNCHANGED and is not made the default](../stories/US0749-the-agentic-safety-rule-is-unchanged-and-is.md)

## Acceptance Criteria (Epic Level)

- [ ] `sprint breakdown` reports the number of INDEPENDENT components over the batch's declared Affects graph, not only the shared-file clusters, so a batch that is one serial mass and a batch that is several parallel lanes read differently.
- [ ] It reports the concentration, not just the count: the size of the largest component in units and points, and that as a share of the batch. Over today's 42 open units the answer is 36 units and 145 of 163 points, 88 percent, and no current output says so.
- [ ] The two measures are distinguished in the wording, because they are both true and answer different questions - a file-shared cluster says which units collide, a component says how many lanes exist. Reporting one under the other's name is what made `2 clusters` read as two comparable halves.
- [ ] A runbook row names the command, so the question `is this batch parallelisable` has a command behind it rather than four judgement steps read out of a reference file and executed by hand.
- [ ] The `--agentic` safety rule is UNCHANGED and is not made the default. The measurement that motivated this showed the flag would correctly decline 88 percent of the current backlog, which is the guarantee holding rather than a gap.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
