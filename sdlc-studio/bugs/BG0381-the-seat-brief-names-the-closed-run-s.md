# BG0381: The seat brief names the CLOSED run's goal, so the seats are briefed on a goal that is not the one under review

> **Status:** Open
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5; human; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Severity:** High
> **Points:** 3

## Summary

`sprint.py goal-review brief --goal '<new goal>' --brief-worklist <file>` renders its header as the PREVIOUS run's goal. `seat_brief()` takes no goal parameter, so the CLI's `--goal` never reaches it; and both of its branches then do `goal = (run_state.read(root) or {}).get('sprint_goal') or goal`, which lets the run state override the plan's goal unconditionally - including when that run is closed.

The stale-plan guard next to it (`_persisted_plan_is_stale`) exists for exactly this hazard and states the reasoning: on a new sprint the persisted plan is the previous sprint's by construction. The goal is read from a different source and is not held to the same rule.

## Steps to Reproduce

1. Close a run whose Sprint Goal is G1.
2. Run `sprint.py goal-review brief --goal 'ZZZ-UNIQUE-PROBE-GOAL' --brief-worklist <a worklist of the NEW batch>`.
3. The batch, the clusters and the carried lessons are all correctly derived from the new worklist. The header reads `Sprint Goal: G1`. The string passed on the command line appears nowhere.

## Proposed Fix

Thread the goal through: `seat_brief(root, worklist=..., goal=...)`, with the caller's goal taking precedence over the run state. Fall back to the run state only for an OPEN run, on the same reasoning the stale-plan guard already records - and render an absent goal as absent rather than substituting a neighbouring one.

## Acceptance Criteria

- [ ] A goal passed to the brief is the goal the brief names, whatever the run state holds.
- [ ] A brief requested while the last run is closed does not name that run's goal; with no goal supplied it says no goal is under review rather than substituting one.
- [ ] The run state supplies the goal only for an OPEN run, pinned by a test that closes a run and asserts the goal does not survive into the next brief.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Acceptance criteria back-filled. They were supplied at filing and neither creation path wrote them: `artifact.py` has no Acceptance Criteria section for a bug, and `file_finding.py` rendered the STATED ABSENCE over them. Both are repaired under BG0384; these four documents are the evidence of the defect and are restored from the fields files they were filed from, not re-invented. |
