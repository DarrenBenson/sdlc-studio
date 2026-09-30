# BG0829: A unit carried at the review cap is filed as an ungroomed bug that sprint plan cannot take, and every carry prints that the operator was notified

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_carry_bug_groomed.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0829.md
> **Evidence:** soak F40 (website project, round-2 REJECT); HEAD 7e53a438 critic.py carry_at_cap (~1535-1560) and panel_escalation (~1425-1440); sdlc-studio/bugs/BG0775 header
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:31Z

## Summary

`critic.carry_at_cap` files the carried bug with the unit's Affects and Points but no criteria and no Verify lines (placeholder criteria restate the summary), its Proposed Fix is `deliver <unit> again in a later run`, its title and slug spell the unit hyphenless, and it is stamped `Raised-in-batch: none open - raised outside a delivery batch` although it is raised inside the open run (BG0775, carried in Sprint 4, reads the same). It cannot be planned without hand grooming. `panel_escalation` prints `ESCALATED to the operator ... The operator is NOTIFIED` on every carry, and nothing notifies anyone.

## Steps to Reproduce

Re-run at HEAD 46cb9acf on 2026-09-30 in a throwaway git tree: US0001 (Points 3, Affects `src/unit.py`) with two criteria, each carrying a `Verify: pytest ...` line, in an open run's batch.

1. `critic.py record --unit US0001 --verdict REJECT --reviewer rev-a --issues "[new] the parser drops a row"`.
2. The same for round 2 with `--issues "[new] the parser still drops the last row; [new] AC2 test passes with the fix removed"`: `US0001 carried at the review cap: BG0001 holds the findings`, followed by `ESCALATED to the operator - US0001: ... The operator is NOTIFIED and the run continues to its handoff`.
3. BG0001 carries the unit's Points and Affects, but its criteria are two tool-derived restatements ("The behaviour described is corrected: US0001 was rejected at round 2 ...", "The proposed fix lands, pinned by a test: Fix each finding above ...") with no Verify line. Its Proposed Fix reads "Fix each finding above, then deliver US0001 again in a later run".
4. `sprint.py breakdown --bugs Open --stories Ready` in the tree: `BG0001 lacks Acceptance Criteria (every one tool-derived from the finding's own prose - restates the summary, so nothing states what passing is)`, under "`sprint plan` refuses a batch holding any of these".

The `Raised-in-batch: none open` stamp is the same on every finding, carry or not, and belongs to BG0861's batch stamp; it is out of this unit's scope.

## Proposed Fix

`carry_at_cap` files the bug groomed: one criterion per finding of the carrying REJECT (its semicolon-separated items, origin tag kept), each stating that finding no longer holds, and beneath them the unit's own criteria with their `Verify:` lines, which the redelivery must still pass; the unit's Points and Affects as today. `panel_escalation` says the operator reads the escalation on the report rather than claiming a notification nothing sends.

## Acceptance Criteria

- [ ] **AC1** Given a unit with two criteria, each with a `Verify:` line, carried at the cap in an open run by a round-2 REJECT listing two findings, when `critic.py record` writes that REJECT, then the filed bug carries one criterion per finding naming its text, the unit's two criteria with their `Verify:` lines, and the unit's Points and Affects, and `sprint.py breakdown` does not report it ungroomed. Fails on: HEAD, whose tool-derived criteria `breakdown` reports as derived-only; on copying only the findings, as criteria with no `Verify:` line, which `breakdown` reports as no-verifier; and on copying only the unit's criteria, which loses what the reviewer found
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_carry_bug_groomed.py::CarryBugGroomedTests::test_the_carried_bug_is_filed_groomed
- [ ] **AC2** Given the same carry, when `critic.py record` prints the escalation, then no line claims the operator was notified, and the line names where the operator reads it. Fails on: HEAD's "The operator is NOTIFIED"
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_carry_bug_groomed.py::CarryBugGroomedTests::test_no_notification_is_claimed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Regroomed after goal review round 1: premise re-run at HEAD (derived-only criteria, `breakdown` refuses the carried bug; NOTIFIED printed); the Raised-in-batch clause dropped, since it rests on BG0861's batch stamp, out of this sprint; AC1 now pins a groomed filing (findings as criteria, the unit's criteria with their Verify lines, Points and Affects) through `breakdown`; Affects drops file_finding.py and test_file_finding.py, adds test_lean_review_cap.py and keeps test_sprint.py (it asserts NOTIFIED); Points 2 to 3. |
