# BG0453: sprint lane return tracebacks on an unreadable run state AFTER running the unit's acceptance criteria, discarding the verification result - the third occurrence of a finding rejected twice

> **Status:** Fixed
> **Severity:** Critical
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** This arrived from the last of seven closing reviewers, after the operator had already ruled which stop-ships to fix before the close. It is filed rather than fixed so the ruling stays the operator's, and it is recorded here as the reason a third repair round did not close BG0405.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** independent round-2 reviewer, bug-repair batch (isolated worktree); agent; v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

BG0405 was filed because an unguarded run-state read made `sprint lane` traceback on a corrupt state. The round-1 repair put the guard in `lane_dispatch`; the round-2 review rejected it because the identical unguarded read sat three statements later in `cmd_lane`. The round-2 repair guarded the BRIEF branch. The identical unguarded read is still in `cmd_lane`'s RETURN branch, twenty lines below the one that was fixed. This is the same defect, in the same function, in the same command, rejected in two consecutive review rounds and still live in the third. It is worse on the return path than on the brief path: `lane return` has already RUN the unit's acceptance criteria before it reaches the unguarded call, so the traceback discards a completed verification rather than merely refusing to start one.

## Steps to Reproduce

Executed at 33f41388, 2026-07-30, by an independent round-2 reviewer in an isolated worktree, using the artefact's own Steps to Reproduce with `return` substituted for `brief`. With a truncated `sdlc-studio/.local/run-state.json`:

The repaired path, which now behaves correctly:

```text
$ python3 sprint.py lane brief --units US0553 --root .
WARNING the run state could not be read, so whether any lane never returned is UNKNOWN, not none
```

The unrepaired sibling, one argument word changed:

```text
$ python3 -B sprint.py lane return --units US0553 --claimed done --root .
  File ".../sprint.py", line 6504, in cmd_lane
    run_state.record_lane_return(root, res["unit"])
lib.run_state.RunStateError: the run state at .../run-state.json is not valid JSON
```

The acceptance criteria are run at line 6499, five lines before the traceback.

## Proposed Fix

Guard the return branch as the brief branch is guarded, and report the unknown rather than raising - the same shape the repair already applied twenty lines up.

The more useful fix is the one that stops the fourth occurrence. Three rounds of review have each found one more unguarded copy of the same read in the same function, because each repair fixed the line the reviewer named rather than the class the reviewer described. Enumerate every `run_state` read in `cmd_lane` and route them through one guarded helper, then pin it with a test that asserts NO unguarded call remains - a test over the call sites rather than over one command's output. Guarding one more line by hand invites the same review to reject it a fourth time.

Severity is Critical rather than High because of the order of operations: on the return path the failure discards work already done. A refusal before starting costs a retry; a traceback after the criteria have run loses the result of running them, and the operator cannot tell from the traceback whether the unit passed.

> **Verification depth:** functional - all three call sites driven through the real `sprint lane` CLI over a corrupt run state, not through the library function (a library test is not a lane test). Three mutants KILLED with unique anchors asserted, `__pycache__` purged and `python3 -B`, including a straight revert of the defect itself.

## Acceptance Criteria

### AC1: lane return no longer tracebacks, and its verification result survives

- **Given** a corrupt run state and a unit whose acceptance criteria have just been run
- **When** `sprint lane return --units <id> --claimed done` runs
- **Then** the command reports rather than raising, and the unit's result is still printed - the read sat AFTER the criteria were executed, so a raise discarded a completed verification and the operator could not tell whether the unit passed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheLaneCommandIssuesABriefOverACorruptStateTests::test_lane_RETURN_does_not_traceback_and_keeps_the_verification_result
- **Verified:** yes (2026-07-30)

### AC2: no run-state call in cmd_lane bypasses the guard, asserted over the call sites

- **Given** cmd_lane's syntax tree, read with AST because the guarded form spans several lines and puts the call inside a lambda
- **When** the call sites are enumerated
- **Then** every `run_state.x(...)` sits inside a lambda handed to `_lane_run_state`, and at least three such calls remain - the count matters, or the test would pass over a function that had simply stopped touching the run state; this is what stops a fourth occurrence, since three rounds each fixed the line the reviewer named rather than the class they described
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheLaneCommandIssuesABriefOverACorruptStateTests::test_no_run_state_call_in_cmd_lane_bypasses_the_guard
- **Verified:** yes (2026-07-30)

### AC3: the brief path is asserted behaviourally, replacing a window search that proved nothing

- **Given** the same corrupt run state on the brief path
- **When** `sprint lane brief` runs
- **Then** the brief is still issued - the previous assertion searched a 400-character window for `except Exception` and reached the end of the function, so it could not tell WHICH read was guarded and passed only because a sibling test fired
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheLaneCommandIssuesABriefOverACorruptStateTests::test_recording_a_lane_start_cannot_withhold_the_brief
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | independent round-2 reviewer, bug-repair batch (isolated worktree) | Filed |
