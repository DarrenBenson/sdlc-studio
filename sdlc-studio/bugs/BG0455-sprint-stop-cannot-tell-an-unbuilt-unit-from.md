# BG0455: sprint stop cannot tell an unbuilt unit from one the two-role gate holds at Review, so it reports work nobody can do as work that could have proceeded

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Verification depth:** functional (5 criteria red-first, including two positive controls - a genuinely unbuilt unit still refuses, and a project with no cutoff treats Review as ordinary remaining work. Three mutants applied singly, purged, restored byte-identical - the awaiting set emptied, the numeric cutoff ignored, and every status treated as Review: all KILLED)
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`sprint stop` refuses while any unit no pending question blocks remains, and names them as able to proceed. Its notion of remaining is status-based, so a unit standing at Review counts as buildable. On a project that sets `review.two_role_after`, a unit at Review is NOT buildable by anyone in the authoring session: Done needs a reviewer-of-record sign-off that the session is explicitly refused. Stopping RUN-01KYPZ1G named 14 such units as `could have proceeded` and required --force, when nothing the run could do would have moved one of them.

## Steps to Reproduce

On a project with `review.two_role_after` set, open a run whose batch holds units at Review with no recorded sign-off, then `sprint.py stop --reason '...'`. It refuses, naming those units, and the remedy it offers (build them, or defer them behind an operator question) fits neither case: the work is finished and the only thing outstanding is a signature.

## Proposed Fix

Read the same rule `reachable_end_state` already applies: a unit at Review, on a project past `review.two_role_after`, with no independent sign-off recorded, is AWAITING SIGN-OFF, not remaining. Report those separately from the units that genuinely could have proceeded, and do not refuse on them - the honest line is `N unit(s) await a sign-off this session cannot give`, which is a fact for the operator rather than a refusal aimed at the agent.

## Acceptance Criteria

- [x] The behaviour described is corrected: `sprint stop` refuses while any unit no pending question blocks remains, and names them as able to proceed.
- [x] Following the recorded steps no longer reproduces the defect: On a project with `review.two_role_after` set, open a run whose batch holds units at Review with no recorded sign-off, then `sprint.py stop --reason '...'`.
- [x] The proposed fix lands, pinned by a test: Read the same rule `reachable_end_state` already applies: a unit at Review, on a project past `review.two_role_after`, with no independent sign-off recorded...

## Impact

Two costs, and the second is the worse one. The operator is pushed to --force, whose whole purpose is to record the cost of parking work that could have proceeded - so the run record now overstates what was left on the table, and the figure is wrong in the direction that makes the run look worse than it was. And the refusal trains the habit of reaching for --force, which is exactly the escape that must stay expensive. `reachable_end_state` already computes this distinction at plan time and states it plainly; stop does not read it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Filed |
