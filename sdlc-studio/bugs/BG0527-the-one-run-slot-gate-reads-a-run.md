# BG0527: the one-run-slot gate reads a run as history the moment its goal verdict is recorded, so the next plan can open over a run whose close has 20 unmet prerequisites

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py,.claude/skills/sdlc-studio/scripts/tests/test_run_state.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Evidence:** Found while planning the EP0207 sprint on 2026-08-06 at 9dc330f5, by testing the premise 'the previous run must close before the next can open' rather than assuming it. The premise is false today. `run_state.py:476-498` (`_is_spent`, `_disjoint`), `sprint.py:8296-8305` (the one-run-slot gate that calls it).
> **Created:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`run_state._is_spent` returns True when any of `sprint_goal_verdict`, `ended_at` or `handoff` is set, on the stated ground that 'a judged run is history regardless of the string'. But the goal verdict is recorded by `sprint goal-verdict`, which runs BEFORE the close chain, not after it. So every run passes through a window - between its goal verdict and its close - in which its outcome still says `running`, its units are still at Review, and the one-run-slot gate has already stood down. `sprint plan --write` accepts a disjoint batch in that window and `open_run` replaces the run state, stranding the previous run's units at Review with no close, no cascade to Done and no record that a close was ever owed.

Two readers of the same run disagree about whether it is finished, which is LL0016. `_is_spent` says history; `close_preflight` on the identical state says 20 unmet prerequisites, all of them - review coverage on 12 of 12 units, no retro named, a stale review anchor, a drifted installed copy, and a blocked Done gate on eight stories. The guard whose whole purpose is to protect an open run's close is off for precisely the run most likely to lose it.

## Steps to Reproduce

Observed live on RUN-01KZ9315 while planning the next sprint, 2026-08-06, at commit 9dc330f5.

1. The run state reads `outcome: running`, `ended_at: null`, `handoff: null`, and carries a `sprint_goal_verdict` recorded at the goal-verdict step.
2. `sprint.py preflight` exits 1 and reports `20 unmet prerequisite(s) - ALL of them`.
3. In the same tree, `run_state._is_spent(run_state.read('.'))` returns `True`, and `run_state.disjoint_refusal('.', ['US0629','US0630','US0631','US0632','US0633','US0634'])` - a batch sharing no unit with the open run - returns `None`, meaning ACCEPTED.
4. `sprint.py plan --write` consults exactly that predicate at the one-run-slot gate and would therefore have opened a second run over the first.

The filing session stopped at step 3 rather than running step 4, so the orphaning is demonstrated by the predicate rather than by damage.

## Proposed Fix

Separate the two questions `_is_spent` currently answers with one boolean. `ended_at` and `handoff` are written BY the close and are sound evidence that a run is finished. `sprint_goal_verdict` is written BEFORE it and is evidence only that the run has been judged, not that it has been closed - so it must not, on its own, release the slot.

Drop `sprint_goal_verdict` from `_CLOSE_ARTEFACTS` and let the close's own artefacts speak for the close. The existing comment already reasons this way about `close_attempts` - a failed close attempt is deliberately excluded because 'a run whose only close artefact is a FAILED close attempt is still running, so it stays open and protected - the disjoint guard covers it rather than exempting it, which is the run most likely to be worked around'. A recorded goal verdict with no close is the same run and deserves the same protection; the exclusion list simply stopped one item short.

## Acceptance Criteria

> Authored as `### ACn` headings with a bold `**Verify:**`, which is the only shape
> `verify_ac` parses. The house bug template's prose-title form is invisible to it and
> reports `ac=0` as a clean pass - BG0530, found while delivering this bug.

### AC1: a recorded goal verdict alone does not release the run slot

- **Given** a run whose `outcome` is `running`, carrying a `sprint_goal_verdict` and neither `ended_at` nor `handoff`
- **When** `disjoint_refusal` is asked about a batch sharing none of its units
- **Then** it returns a refusal naming that run, and `open_run` raises rather than replacing the state
- **Mutant:** put `sprint_goal_verdict` back in `_CLOSE_ARTEFACTS` - this reddens and nothing else in the tree does, which was the state of the repository when it was found
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::SlotReleaseTests::test_a_goal_verdict_alone_does_not_release_the_slot
- **Verified:** yes (2026-08-06)

### AC2: the positive control - a run the close finished does release it

- **Given** the same run with `ended_at` set, and separately with `handoff` set
- **When** the next batch is planned
- **Then** no refusal is raised, a fresh run is minted and the finished one is archived
- **Mutant:** refuse whenever the outcome string reads `running` - AC1 still passes while every legitimate next sprint is refused, so only this criterion tells the repair from an over-correction
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::SlotReleaseTests::test_a_closed_run_still_releases_the_slot
- **Verified:** yes (2026-08-06)

### AC3: the refusal reaches through the shipped command, and writes nothing

- **Given** a judged-but-unclosed run
- **When** `sprint.py plan --write` is driven over a disjoint worklist
- **Then** it exits non-zero, names the open run so the operator knows which to close, and leaves `run-state.json` and `sprint-plan.json` byte-identical
- **Mutant:** consult the predicate and ignore its answer, or consult it after the sibling artefacts are written - the library criteria stay green while the run is orphaned anyway, which is LL0040
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SlotGateLaneTests::test_the_slot_gate_refuses_through_plan_write_and_writes_nothing
- **Verified:** yes (2026-08-06)

### AC4: an overlapping re-plan is accepted while the run is UNJUDGED, and refused once it is not

> **RESTATED at review.** The delivered version said an overlapping re-plan is always accepted.
> An independent seat showed what that costs: removing `sprint_goal_verdict` from
> `_CLOSE_ARTEFACTS` shut the disjoint door and opened the overlapping one, so a re-plan sharing
> a unit ACCUMULATED onto the batch the goal verdict had already judged - BG0188's own harm
> arriving by the other door, and previously masked because that path minted a fresh run. A
> judged batch is now frozen; an identical re-plan is still a no-op.

- **Given** the same run and a worklist naming one of its own units
- **When** the same command runs
- **Then** it exits zero and stays on the same run id, because re-planning an open run is the documented path
- **Mutant:** refuse on any open run regardless of overlap - re-planning an in-flight run becomes impossible and the fix trades one stranding for another
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SlotGateLaneTests::test_an_overlapping_replan_still_reaches_exit_zero_through_the_verb
- **Verified:** yes (2026-08-06)

### AC6: BG0188's property survives the change of remedy

- **Given** BG0188, which established that a judged-but-unclosed run must not have a new batch accumulated onto it, and whose remedy was to mint a fresh run
- **When** the same scenario runs under this fix
- **Then** the batch is still not accumulated and the verdict is still not clobbered - but the run is REFUSED rather than replaced, so the owed close is not silently discarded either
- **Mutant:** restore BG0188's remedy (mint a fresh run) - the units of the judged run are stranded, which is the defect this bug was filed for, and the refusal assertion reddens
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::RunStateTests::test_a_judged_run_left_running_is_refused_not_accumulated
- **Verified:** yes (2026-08-06)

### AC5: the rule behind the list is asserted, not left to the comment

- **Given** the membership of `_CLOSE_ARTEFACTS`
- **When** it is checked against the fields written before the close
- **Then** no member is one of them, and the list is non-empty
- **Mutant:** add any pre-close field - `sprint_goal_verdict`, `goal_content_review`, `appetite`, `token_forecast` - and this reddens naming it. This is the check the original list lacked, so nothing objected when a pre-close field was put into it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::SlotReleaseTests::test_the_close_artefacts_are_all_written_by_the_close
- **Verified:** yes (2026-08-06)

## Impact

Every run in this repository passes through the affected window, because recording the goal verdict before closing is the shipped order, not a deviation from it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
| 2026-08-06 | sdlc-studio | Groomed at plan time: the tool-derived criteria replaced with four decidable ones naming their mutants, plus the lane test and the over-correction control |
| 2026-08-06 | sdlc-studio | Affects corrected to name test_sprint.py (the lane test) and test_handoff.py (BG0188 supersession) - the ratchet caught the understated footprint the seats caught by hand last run |
