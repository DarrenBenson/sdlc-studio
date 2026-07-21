# BG0246: batch_history excludes every interactive sprint, so the plan's 'real cost input' silently shows only old runner-era sprints

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`sprint.batch_history` requires BOTH a non-zero `actual_tokens` AND a non-zero `measured` column, where `measured` counts units carrying PER-UNIT telemetry. An interactive sprint has no runner and therefore no per-unit records, so measured is 0 even when the sprint-level harness capture recorded a real total. Every interactive sprint is dropped. Observed planning the follow-up batch on 2026-07-21: the plan printed 'batch history (what sprints ACTUALLY cost - the real planning input)' listing RETRO0025 through RETRO0028 at 128,471 to 188,022 tokens per unit, and silently excluded RETRO0060 (2,390,624 tokens over 9 units = 265,625/unit) and RETRO0061 (1,265,392 over 13 units = 97,338/unit) - the two most recent sprints with measured totals. RETRO0060 alone is 1.4x the per-unit cost of the most expensive sprint shown. The rows the planner does display are the OLDEST measured data in the file, from the runner era, and nothing in the output says two newer measured sprints were left out. This is the project's recurring defect class - a number presented as authoritative that quietly omits the most relevant evidence - and it sits in the one block the docstring calls 'what the operator should plan against'. It also interacts with the stalled calibration: the plan says 'this project has 3 unit(s) of its own evidence so far; the rate becomes ITS measurement at 5', and that counter cannot advance while the same filter discards the sprints that would advance it.

## Steps to Reproduce

1. Ensure the velocity history contains at least one interactive sprint with a sprint-level actual and measured=0 (RETRO0060 and RETRO0061 both qualify today). 2. Run sprint.py plan --bugs Open. 3. Read the 'batch history' block. Observed: only RETRO0025-0028 are listed. Expected: the most recent measured sprints, or an explicit statement that N measured sprints were excluded and why. Confirm the cause directly: `batch_history` skips a row unless isinstance(r['measured'], (int,float)) and r['measured'] is truthy, and every interactive sprint records measured=0.

## Proposed Fix

Decide what the block is for. If it is per-unit cost, then a sprint with only a sprint-level total can still contribute tokens/unit as total/units, and `measured` is the wrong gate - use the units column and mark the row as sprint-level rather than per-unit. If per-unit telemetry is genuinely required, then the block must SAY how many measured sprints it excluded and why, because silence here reads as 'this is all the evidence there is'. Either way it must not present the oldest data as the current cost picture. Guard it with a test that puts an interactive-shaped row (actual set, measured 0) in the history and asserts it is either included or explicitly reported as excluded - never simply absent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
