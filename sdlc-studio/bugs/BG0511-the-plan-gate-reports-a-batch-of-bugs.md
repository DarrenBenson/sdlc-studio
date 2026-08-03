# BG0511: the plan gate reports a batch of bugs groomed when the transition gate refuses them outright

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Evidence:** Reproduced by the author against the live tree: breakdown over the 17-unit run-1 worklist printed `breakdown: 17 unit(s), 0 ungroomed`, while `transition.py set --status Fixed --dry-run` refused BG0488, BG0491, BG0493, BG0495 and BG0497 for having no acceptance criteria. Independently found by the engineering and QA seats at the goal review.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint.py breakdown` and `sprint.py plan --write` compute their ungroomed census over STORIES only. A bug with no `## Acceptance Criteria` section at all, or one carrying only `refine`-minted placeholder text, passes the plan gate silently. A 17-unit batch containing five bugs with no criteria section was reported as `0 ungroomed` and was plannable; the same five are refused by `transition.py set --status Fixed` with `no acceptance criteria; Fixed requires at least one`. So the planner admits work the deliverer cannot terminate, and the operator learns this at delivery rather than at planning - which is the whole reason the ungroomed census exists. Found at the plan-time goal review for the run-1 batch, by two independent seats, each by reading the bugs rather than trusting the census. It is adjacent to BG0491 (lane-check scans only stories) but is a separate gate on a separate command: BG0491 is about the duplicate-verifier number, this is about whether a batch is plannable at all.

## Steps to Reproduce

1. Build a worklist naming BG0488, BG0491, BG0493, BG0495 and BG0497.
2. Run `sprint.py breakdown --worklist <file>` - it reports `0 ungroomed`.
3. Run `transition.py set --id BG0493 --status Fixed --dry-run` - it refuses with `no acceptance criteria; Fixed requires at least one`.
4. The same unit is simultaneously plannable and unterminable.

## Proposed Fix

Extend the ungroomed census to every unit type the batch can contain, not stories alone. Two shapes must both count: an absent Acceptance Criteria section, and a section whose every criterion is a `refine` placeholder - `conformance.story_is_ungroomed` already knows the second shape and is only ever asked about stories. Then pin the census with a bug fixture, so the check cannot regress to story-only again.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `sprint.py breakdown` and `sprint.py plan --write` compute their ungroomed census over STORIES only.
- [ ] The proposed fix lands, pinned by a test: Extend the ungroomed census to every unit type the batch can contain, not stories alone.

## Impact

A batch is admitted to a run that cannot reach terminal, so the run's first honest signal is a refusal at delivery. In the batch that exposed this, 21 of 58 points were unterminable and a further 12 carried placeholder criteria - over half the run, invisible to the command whose job is to say whether the backlog is worth planning from.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
