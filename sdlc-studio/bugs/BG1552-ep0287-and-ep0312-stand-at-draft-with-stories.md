# BG1552: EP0287 and EP0312 stand at Draft with stories Done and shipped in 6.4.0, and reconcile detect reports no drift

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/reference-epic.md, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, sdlc-studio/epics/EP0287-personas-become-accountable-team-members-a-review-standard.md, sdlc-studio/epics/EP0312-the-commit-hook-runs-the-cheap-repo-wide.md, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issues.py, sdlc-studio/epics/_index.md, sdlc-studio/epics/archive/v6.1/epic.md, sdlc-studio/epics/EP0284-review-seats-chosen-by-what-a-change-touches.md, sdlc-studio/epics/EP0285-persona-goals-become-checks-the-stories-seats-and.md, sdlc-studio/epics/EP0326-a-sprint-drives-each-unit-s-lane-to.md, sdlc-studio/epics/EP0327-authors-and-reviewers-run-one-shipped-mutation-runner.md, .claude/skills/sdlc-studio/reference-scripts.md, changelog.d/BG1552.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, cross lens, survived 3 of 3 refute votes; observed at sdlc-studio/epics/EP0287-personas-become-accountable-team-members-a-review-standard.md Line 3 (`> **Status:** Draft`) and the Story Breakdown; sdlc-studio/prd.md lines 333-334; sdlc-studio/epics/EP0312-the-commit-hook-runs-the-cheap-repo-wide.md line 3; `epic_status_stale_drift` in .claude/skills/sdlc-studio/scripts/reconcile.py (about line 1032)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:28:28Z

## Summary

An epic's status is derived only when every child is terminal. An epic that is partly delivered keeps the status it was created with, and no detector reports the contradiction: `epic_status_stale_drift` in reconcile.py skips any epic with a non-terminal child, and its docstring says nothing derives the parent's status from its children. EP0287 reads Draft with eight stories Done, one Ready and fourteen Draft; those Done stories are named as delivered in docs/release-notes-v6.4.0.md, and two PRD feature rows cite EP0287 as Complete. EP0312 reads Draft with one of its two stories Done. reconcile detect ends with zero drift items. Anything that reads epic status to decide what is in flight, such as status or backlog triage, sees shipped 6.4 work as not started. reference-epic.md's rule that any In Progress child makes the epic In Progress has no scripted counterpart for children that are already Done.

## Steps to Reproduce

1. Read line 3 of sdlc-studio/epics/EP0287-personas-become-accountable-team-members-a-review-standard.md. Status is Draft.
2. Read the status of each story in its breakdown. Eight are Done, among them US1059, US1061, US1062 and US1064 to US1068.
3. Read sdlc-studio/prd.md lines 333 to 334. Two rows cite EP0287 with the status Complete.
4. Read line 3 of sdlc-studio/epics/EP0312-the-commit-hook-runs-the-cheap-repo-wide.md. Status is Draft with one of two stories Done.
5. Run reconcile.py with the detect verb at the repository root.
6. Observed: zero drift items.
7. Expected: a drift item for each epic saying it reads Draft while it has delivered children.
8. Positive control: an epic whose every child is terminal and whose status disagrees is reported by the existing lane.

## Proposed Fix

Add a detector to reconcile.py that reports an epic at Draft or Ready when any declared child is Done or In Progress, deriving In Progress, and let the apply step write that status as it does for the all-terminal case. State the rule in reference-epic.md beside the existing In Progress line so the prose and the script agree. Add fixture tests in `test_reconcile.py` for a Draft epic with one Done child, with an all-Draft epic as the control. Then run reconcile so EP0287 and EP0312 read In Progress and the epic index follows.

## Acceptance Criteria

- [ ] **AC1** Given a fixture workspace holding an epic at Draft whose breakdown declares one Done story and one Draft story, when `reconcile.py detect` runs, then it reports one drift item naming the epic, its recorded status and the derived status In Progress, and exits non-zero. Fails on: a partly delivered epic passing detect with zero drift items.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EpicPartialDeliveryTests::test_a_draft_epic_with_a_done_child_is_reported_as_in_progress
- [ ] **AC2** Given the same fixture with an epic at Ready whose only moved child is In Progress, an epic whose every child is Draft, and an epic already at In Progress with a Done child, when `reconcile.py detect` runs, then the Ready epic is reported and the other two are not. Fails on: an untouched epic or an epic already In Progress being reported, or a Ready epic with an In Progress child being missed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EpicPartialDeliveryTests::test_an_all_draft_epic_and_an_in_progress_epic_are_not_reported
- [ ] **AC3** Given the Draft epic with a Done child, when `reconcile.py apply` runs and detect runs again, then the epic's Status line reads In Progress, its index row agrees, the second detect reports nothing for it, and an epic whose every child is terminal is still left to the existing lane unchanged. Fails on: apply leaving the epic at Draft, or apply closing an all-terminal epic the existing lane only reports.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EpicPartialDeliveryTests::test_apply_writes_in_progress_and_a_second_detect_is_clean
- [ ] **AC4** Given the fix has landed, when reconcile is applied in this repository, then EP0287 and EP0312 read In Progress in their own files and in the epic index, and reference-epic.md states the derived rule for Done children beside its In Progress line. Fails on: either epic still reading Draft, or the reference page stating a rule the script does not hold.
  - **Verify:** shell grep -q '^> \*\*Status:\*\* In Progress' sdlc-studio/epics/EP0287-personas-become-accountable-team-members-a-review-standard.md && grep -q '^> \*\*Status:\*\* In Progress' sdlc-studio/epics/EP0312-the-commit-hook-runs-the-cheap-repo-wide.md && grep -Eq '^\| \[EP0287\].*\| In Progress \|' sdlc-studio/epics/_index.md && grep -Eq '^\| \[EP0312\].*\| In Progress \|' sdlc-studio/epics/_index.md && python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EpicPartialDeliveryTests::test_reference_epic_states_the_rule_the_script_holds

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Affects widened before landing to what the derived In Progress rule touches: the two close and known-issues tests whose fixtures move a story under a Draft epic, the epic-status-stale hint in lib/sdlc_md.py, the epic index and its v6.1 archive rows, and EP0284, EP0285, EP0326 and EP0327, which detect now reports; found by the REF builder |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | AC4 gains the Verify line the REF builder ran: both epics and their index rows read In Progress, and the reference test pins the rule |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | AC4's Verify line runs through the shell verb: the grep verb reads `&&` and the rest as paths, which made it check only the first grep (BG1024 AC added) |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Affects widened to reference-scripts.md, whose `settle` sentence (closing only finished epics) this unit's partial-delivery move makes untrue |
