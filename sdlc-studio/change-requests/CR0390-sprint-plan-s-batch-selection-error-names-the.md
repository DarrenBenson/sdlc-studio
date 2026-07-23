# CR-0390: sprint plan's batch-selection error names the flags but not that each one takes a status, costing two failed invocations to discover

> **Status:** In Progress
> **Decomposed-into:** EP0145
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Running `sprint plan --order wsjf` with no batch prints `specify a batch: --bugs/--crs/--stories (combinable), --worklist, or --prd`. Every flag is written bare, so the natural next attempt is `--bugs`, which fails with the argparse default `argument --bugs: expected one argument` and a nine-line usage block that shows `--bugs STATUS` without saying what a valid STATUS is. It took three invocations to reach `--bugs Open`. The guidance message is doing the right thing - catching a missing batch early and naming the options - and is one word short of being complete: `--bugs Open` in the message instead of `--bugs` would have made the first retry correct. This is small in isolation but it sits on the hottest path in the skill, is paid by every new agent and every context reset, and the cost is paid in failed tool calls rather than in reading.

## Impact

Any agent or operator invoking `sprint plan`, which is the entry point to the whole delivery loop and the first thing run after a context reset. The failure is loud rather than silent, so nothing breaks - the cost is two wasted round-trips each time, and a usage block that answers 'what shape' but not 'what value'.

## Acceptance Criteria

- [ ] The batch-selection message shows a usable example value for each selector, so the first retry after it is a working invocation.
- [ ] The valid status values are discoverable from the failure itself rather than only from the help file.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
