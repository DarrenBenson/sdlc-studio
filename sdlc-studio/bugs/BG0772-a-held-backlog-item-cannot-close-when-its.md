# BG0772: A held backlog item cannot close when its closing story ships

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py, sdlc-studio/reviews/backlog-sweep-2026-09-24.md, sdlc-studio/change-requests/CR0554-a-plan-row-whose-recorded-kill-node-is.md, sdlc-studio/change-requests/CR0556-a-bug-reaches-a-terminal-status-with-no.md, sdlc-studio/epics/EP0241-a-kill-recorded-against-a-node-the-criterion.md, sdlc-studio/epics/EP0242-a-bug-s-plan-or-evidence-gets-an.md, sdlc-studio/epics/EP0227-a-broken-unit-and-an-under-evidenced-one.md, sdlc-studio/stories/US0731-evidence-debt-is-recorded-against-the-criterion-it.md, sdlc-studio/stories/US0793-a-row-whose-ledger-kill-node-is-not.md, sdlc-studio/stories/US0794-a-row-whose-kill-node-is-named-reads.md, sdlc-studio/stories/US0795-a-verify-line-naming-a-whole-file-is.md, sdlc-studio/stories/US0796-the-corpus-count-of-killed-elsewhere-rows-is.md, sdlc-studio/stories/US0800-a-bug-whose-declared-mutant-was-killed-by.md, sdlc-studio/bugs/BG0679-with-review-repair-plan-gate-on-a-repair.md, sdlc-studio/bugs/BG0683-repair-gate-s-review-before-repair-ordering-check.md, sdlc-studio/bugs/BG0684-transition-s-two-role-gate-ignores-a-definition.md, sdlc-studio/bugs/BG0685-project-upgrade-reads-plan-review-verdicts-with-no.md, sdlc-studio/bugs/BG0693-testplan-derive-and-the-plan-review-brief-still.md, sdlc-studio/bugs/BG0697-the-repair-plan-gate-fails-open-on-a.md, sdlc-studio/bugs/BG0698-repair-plan-rounds-can-be-overwritten-by-concurrent.md, sdlc-studio/change-requests/CR0543-plan-review-has-no-adoption-cutoff-so-the.md, sdlc-studio/change-requests/CR0555-the-expensive-half-of-the-test-plan-gate.md, sdlc-studio/change-requests/CR0558-the-derived-depth-lane-checks-each-span-against.md, sdlc-studio/change-requests/CR0582-no-command-closes-a-plan-review-reject-s.md, sdlc-studio/change-requests/CR0583-no-command-applies-a-unit-s-authored-test.md, sdlc-studio/epics/EP0218-the-plan-review-binds-where-the-code-is.md, sdlc-studio/epics/EP0243-the-derived-depth-lane-re-derives-rather-than.md, sdlc-studio/stories/US0682-review-mutation-evidence-stays-independent-of-the-test.md, sdlc-studio/stories/US0683-the-close-reports-which-units-the-test-plan.md, sdlc-studio/stories/US0685-the-entry-gate-keeps-the-demand-that-a.md, sdlc-studio/stories/US0686-the-entry-refusal-names-when-the-independent-approval.md, sdlc-studio/stories/US0687-the-terminal-transition-demands-the-independent-plan-review.md, sdlc-studio/stories/US0689-the-move-binds-behind-the-existing-dated-cutoff.md, sdlc-studio/stories/US0690-the-close-names-which-units-had-the-approval.md, sdlc-studio/stories/US0733-a-unit-carrying-evidence-debt-is-still-refused.md, sdlc-studio/stories/US0801-a-unit-whose-stamped-derived-half-no-longer.md, sdlc-studio/stories/US0802-a-unit-whose-span-matches-a-fresh-derivation.md, sdlc-studio/stories/US0803-an-eviction-of-a-unit-s-ledger-rows.md, sdlc-studio/bugs/_index.md, sdlc-studio/change-requests/_index.md, sdlc-studio/stories/_index.md, sdlc-studio/epics/_index.md, changelog.d/BG0772.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T13:09:43Z

## Summary

D0264 holds 47 backlog items open until the EP0263 story named in each item's 'Closes with:' field ships. `test_lean_backlog_sweep.py`::BacklogSweepTests::`test_held_items_stay_open_naming_their_closing_story` asserts every HELD item is non-terminal unconditionally, so closing one after its story is Done turns the push red. At RUN-01M3BK9Y's close 25 items whose stories had shipped (US0909, US0910/US0934, US0911, US0912, US0913, US0916, US0935, and EP0218 with US0909 and US0911) were closed as superseded and 25 subtests failed at the push boundary; the closure was reverted and waits on this.

## Steps to Reproduce

1. Supersede BG0685 (Closes with: US0909; US0909 is Done). 2. pytest .claude/skills/sdlc-studio/scripts/tests/`test_lean_backlog_sweep.py`: the BG0685 subtest fails 'held open under D0264'.

## Proposed Fix

Assert a held item non-terminal only while any story its Closes-with field names is not yet Done, with a mutant that closes an item whose story is still open; then re-apply the 25 closures (revert of the revert of 3efa27e9).

## Acceptance Criteria

- [ ] **AC1** Given a HELD row in the sweep record, when the item reads terminal, then the test passes only if every story its `Closes with:` field names is Done, and a held item that reads terminal while a named story is Draft fails the test naming the item and the story. Fails on: deleting the non-terminal assertion for every held item, which lets a hold close while its code still ships (D0264)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_a_hold_closes_only_after_its_story_ships
- [ ] **AC2** Given CR0554, CR0556, EP0241, EP0242, US0731, US0793, US0794, US0795, US0796 and US0800, then each `Closes with:` field and its sweep-record row name US0936 in place of US0921, EP0227's name US0918, US0920 and US0936, and the test's EP0263 set includes US0934, US0935 and US0936; each stays open while US0936 is not Done. Fails on: landing AC1 alone, which reads US0921 as Done and closes the ten while `mutation.py register` and the ledger still ship
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_ledger_holds_name_us0936
- [ ] **AC3** Given the 25 held items whose closing stories are Done (BG0679, BG0683, BG0684, BG0685, BG0693, BG0697, BG0698, CR0543, CR0555, CR0558, CR0582, CR0583, US0682, US0683, US0685, US0686, US0687, US0689, US0690, US0733, US0801, US0802, US0803, with EP0218 and EP0243 derived from their children), then each is Superseded through `transition.py set`, carries a revision row citing D0264 and its closing story, and its `_index.md` row reads the same status as its file. Fails on: re-applying 3efa27e9 with `git revert`, which restores status lines and index rows written against an older index and skips the transition's cascade
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_the_due_holds_are_closed
- [ ] **AC4** Given a held item whose `Closes with:` field is missing, names a story outside EP0263, or disagrees with its record row, then the test still fails on it. Fails on: loosening the field checks while adding AC1's condition
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_held_items_stay_open_naming_their_closing_story

## Notes

- Amended by the QA seat for Sprint 5 (measured at 013a46d0). By field, 35 holds name a Done story, not 25: the other ten name US0921, whose ledger half was split into US0936 (Draft, whose own Notes claim CR0556, EP0242 and US0800). AC2 re-points them so AC1's rule cannot close live defects. The sweep record's Action cells for those eleven rows are amended in place with a one-line amendment note under the table citing the US0921/US0936 split, because the test requires each field to equal its record row. Keep `test_held_items_stay_open_naming_their_closing_story` under its name so its stamp survives. `transition.py requirements` reports no unmet requirement for BG0679, CR0543 and US0682 -> Superseded.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | sdlc-studio v6 planning | QA seat: criteria regroomed for Sprint 5 - conditional hold rule, the ten US0921 holds (and EP0227) re-pointed to US0936, the 25 due holds closed through transition.py rather than git revert; 2 -> 3 points |
