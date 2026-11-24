# BG1641: A repair's QA brief does not name the reviewer whose REJECT it answers, so a fresh reviewer's round two is refused at record

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_second_seat_brief.py, .claude/skills/sdlc-studio/scripts/lib/resume_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py, changelog.d/BG1641.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T00:35:57Z

## Summary

critic.py record refuses a round-two verdict from anyone but the reviewer who rejected round one (critic.py:1986-1990). The QA brief lane land writes for a repaired unit (lib/lanes.py) quotes the REJECT but never says the round must go back to that reviewer, and lane accept only finds out after the review has run. In RUN-01M7TTK3 the orchestrator briefed fresh qa reviewers for BG1543, BG1525, BG1180 and BG1553 from those briefs; all four APPROVEs were refused at record and the round-one reviewers had to be resumed and briefed again, at the cost of two complete reviews.

## Steps to Reproduce

Record a REJECT on a unit, land its repair with sprint.py lane land, read the QA brief it writes (sdlc-studio/.local/briefs/<ID>-qa.txt): no line names the reviewer round two must come from. Record an APPROVE from another reviewer with lane accept: refused, 're-checks the fixes to <reviewer>'s REJECT'.

## Proposed Fix

When the unit has an unanswered REJECT, have the QA brief open with the reviewer who must judge round two and the instruction to resume that reviewer rather than spawn a new one, and have lane land print the same line beside the brief path.

## Acceptance Criteria

- [ ] **AC1** Given a unit with an unanswered REJECT from reviewer R whose repair is landed with `sprint.py lane land`, when the QA brief `sdlc-studio/.local/briefs/<ID>-qa.txt` is read, then it opens with a line naming R and telling the orchestrator to resume R rather than spawn a new reviewer. Fails on: no line of the brief names the reviewer.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_repair_brief_opens_with_the_reviewer_whose_reject_it_answers
- [ ] **AC2** Given the same landing, when `lane land` prints the brief path, then the same reviewer line is printed beside it. Fails on: the output names only the path.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_lane_land_prints_the_reviewer_beside_the_brief_path
- [ ] **AC3** Given a unit with no REJECT, when its first-round QA brief is written, then no reviewer line is added and the brief is byte-identical to `critic.py brief` output (positive control). Fails on: a fix that adds the line to every brief, which also changes the fingerprint `_brief_of` hashes from the saved text.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_first_round_brief_carries_no_reviewer_line
- [ ] **AC4** Given a landed repair whose saved QA brief opens with the reviewer line and a REJECT recorded against it, when the resume brief reads the lane's state, then it reads the lane as rejected, not landed. Fails on: `resume_brief._approved` hashes the saved brief with its reviewer line, so the fingerprint matches no verdict and the lane reads as landed with the wrong next step.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::RepairBriefApprovalTests::test_a_repair_brief_with_a_reviewer_line_reads_its_reject

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-six: criteria pin the brief line, the printed line and a first-round control; the builder must keep the fingerprint `lane accept` hashes from the saved text (`_brief_of`) valid |
| 2026-11-24 | orchestrator (delegate under D0545) | Affects widened for run twenty-six's LN lane: the reviewer line changes the saved repair brief's hash, which test_lane_accept_second_seat_brief.py:220 and `resume_brief._approved` both read; AC4 added for `_approved` (D0561) |
