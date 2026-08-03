# BG0503: an epic whose every child is terminal stays Draft, and no reconcile detector says so: 15 of 30 open epics are already delivered

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, sdlc-studio/trd.md
> **Verification depth:** functional
> **Evidence:** Measured against HEAD 4979f93f during the post-close backlog analysis of RUN-01KYZKY5. Fifteen epics enumerated by counting non-terminal children per Draft epic; `reconcile detect` run over the same tree at the same commit returned drift_items=0.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Half the open epics are finished. EP0166, EP0167, EP0168, EP0169, EP0172, EP0175, EP0177, EP0181, EP0190, EP0198, EP0199, EP0200, EP0201, EP0202 and EP0203 each carry a Story Breakdown in which every child story is Done and every box is ticked, and each still reads `Status: Draft`. `reconcile detect` returns `drift_items=0` over all of them.

The cascade only ever ticks a box. `transition._cascade_epic` rewrites the story's line in its parent's Story Breakdown and returns; it never touches the parent's own Status field. `reconcile`'s epic sweeps cover the same ground and no more - `breakdown-unticked` and `breakdown-ticked-early` reconcile the checkboxes, `epic-points-stale` the Derived Point Total, `epic-index-derivable` the index row's derived cells. `DRIFT_KINDS` holds no kind for an epic whose status contradicts its own children, so the one state that matters to a planner is the one nothing derives.

The roll-up direction that masks unfinished work is already detected - a ticked box over a live unit is `breakdown-ticked-early`, and the docstring says it is caught because it masks unfinished work. The opposite direction, a Draft epic over a fully delivered breakdown, masks FINISHED work and is caught by nothing.

## Steps to Reproduce

Run `status.py --root . backlog`: the delivery backlog reports 30 Draft epics. For each, count the child stories that are non-terminal - grep the stories for `**Epic:** <id>` and read their Status. Fifteen have none. Then run `reconcile.py --root . detect`: `scope=all drift_items=0 by_kind={}`. EP0177 is the clearest single case: 15 child stories, all Done, all 15 breakdown boxes ticked, epic Status Draft.

## Proposed Fix

Add an `epic-status-stale` drift kind: an epic whose breakdown units are all terminal, and which is not itself terminal, is drift with the fix naming the transition. Derive it from the same `_breakdown_units` helper `epic_breakdown_drift` already uses, so the two detectors cannot disagree about what an epic's children are. Detect-only is enough to close this - an `apply` that transitions epics would move a status without the gates `transition.py set` runs, and the review-two-role rules an epic close may carry belong on that path. An epic that declares no breakdown asserts no roll-up and must be left alone, the same rule `epic_points_drift` already applies to an epic with no declared point total.

## Acceptance Criteria

- [x] **AC1: a live epic whose every declared breakdown unit is terminal is reported by the DEFAULT sweep, and `detect` exits non-zero on it.**
  - **Verify:** `python3 -m unittest tests.test_reconcile.EpicStatusStaleTests` from the scripts directory
  - **Verified:** yes (2026-08-03) - 9 tests OK. The sweep half is asserted through `reconcile.main(["detect"])`, not only the helper: the defect was never in the comparison, it was that no sweep performed one, so a helper-only test would have passed on the day this was filed

- [x] **AC2: the three states in which an epic asserts nothing are silent - a live child, a `Deferred` child, an unresolvable declared child, and an epic declaring no breakdown at all.**
  - **Verify:** the same class - `test_one_live_child_holds_the_epic_open`, `test_a_deferred_child_is_neither_finished_nor_live`, `test_an_unresolvable_child_is_unknown_not_finished`, `test_an_epic_declaring_no_breakdown_asserts_no_rollup`
  - **Verified:** yes (2026-08-03)

- [x] **AC3: detect-only - `reconcile apply` never writes an epic's status.**
  - **Given** closing an epic is a transition, and `transition.py set` is where the epic's own gates live
  - **Then** a full `apply` that has just seen the drift leaves the status untouched and the drift still reported
  - **Verify:** `test_apply_never_writes_this_one`
  - **Verified:** yes (2026-08-03)

- [x] **AC4: the kind is registered and carries a remediation hint naming the transition.**
  - **Verify:** `test_the_kind_is_registered_and_carries_a_remediation_hint`
  - **Verified:** yes (2026-08-03) - `epic-status-stale` in `DRIFT_KINDS`, hint in `sdlc_md.REMEDIATION`

- [x] **AC5: the detector's verdict over the live tree matches the hand census that filed this bug.**
  - **Verify:** run `epic_status_stale_drift` against the repo root before the repair
  - **Verified:** yes (2026-08-03) - 15 epics, the same fifteen ids enumerated by hand: EP0166, EP0167, EP0168, EP0169, EP0172, EP0175, EP0177, EP0181, EP0190, EP0198, EP0199, EP0200, EP0201, EP0202, EP0203. Two independent methods, one answer

## Verification evidence

Functional, with both mutants executed and killed:

| Mutant | Result |
| --- | --- |
| delete the `epic_status_stale_drift` call from `detect_all` | killed by `test_the_default_sweep_reports_it_and_detect_exits_non_zero` |
| invert `if sdlc_md.is_terminal_status("epic", canon): continue` | killed by 4 of the 9 |

`__pycache__` purged and re-run under `python3 -B` each time; source restored and re-run green.

**What clearing it found.** The fifteen epics were closed with `transition.py set` (the remedy the
finding names, one call each, so every epic's own gates ran). That unblocked a second layer the
stale statuses had been masking: 29 requests - `RFC0056` and 28 CRs - whose every child was now
resolved, reported as `request-derivable` and derived by `reconcile apply`, which routes through
`transition`. The Discovery backlog fell from 60 to 31 and Delivery from 106 to 91. So the
overstatement this bug describes was not confined to the epic layer; it propagated to every
request those epics delivered, and any appetite taken from either number was reading roughly
double the truth.

## Impact

Planning reads a delivery backlog that is overstated by half its epics. `status.py` reported 30 open epics into a themes analysis on 2026-08-03 and 15 of them were already delivered, so appetite, tranche selection and any judgement resting on how much is left were all taken against a number that was wrong by 100%. The same census feeds `backlog_triage.py check`, which passed the backlog as plannable.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
