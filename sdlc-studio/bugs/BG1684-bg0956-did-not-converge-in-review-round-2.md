# BG1684: BG0956 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, changelog.d/BG0956.md, .claude/skills/sdlc-studio/reference-scripts-create.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/reference-outputs.md
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T15:55:40Z

## Summary

BG0956 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The archive writer's `applied /= done` (reconcile.py:3121) is unpinned, and the author's recorded survivor `applied /= set(here)` is not equivalent through the shipped entry point: with one archive sub-index holding a header-less BG0003 row ahead of a headed table holding BG0001, both drifted to Closed with no live row, `reconcile apply` on the shipped code exits 1, names BG0003 "row not in a rewritable layout" and reports "changed 1 row(s), 1 could not be applied", while under the mutant it exits 0, prints "set bug BG0003: Fixed -> Closed" and "changed 2 row(s)" with the BG0003 row still reading Fixed. That is the claimed sync AC4 rules out, and test\_an\_unplaceable\_row\_still\_reports\_unsynced (one id per sub-index) does not catch it; [pre-existing] the rewritten comment at transition.py:1297-1299 still gives "a target status with no summary row" as a cause of residual drift, false since CR0159 (c78bfae9, before the base) made apply insert a missing summary row, as test\_status\_without\_summary\_row\_now\_syncs\_by\_insertion pins\; no open bug covers it; RULINGS: Round-1 "the archive writer's call to `align_padded_tables` is unpinned" CLOSED: my mutant writing the text unaligned is killed by test\_a\_hand\_aligned\_archive\_table\_stays\_aligned. Round-1 "the archive writer's trailing-newline branch is unpinned" CLOSED: dropping the final newline and always adding one are each killed by test\_the\_archived\_file\_keeps\_its\_final\_newline\_or\_its\_lack\_of\_one. Round-1 "transition.py:1285-1287 still explains a residual drift" CLOSED for the archived-row clause, which now names the header-less table and is TRUE against HonestSyncTests (its other clause is the pre-existing finding above). Round-1 "reference-scripts-verify.md:183" CLOSED: both pages now say reconcile rewrites an archived row's Status cell and moves no row, TRUE by AC2, AC3 and a probe. verify\_ac dry run 4/4 pass, tools/lint-style.sh clean. Claim inventory: the changelog fragment and the `_rewrite_archived_rows` docstring are TRUE (aligned table kept aligned, final newline kept or kept absent, live row wins, header-less row unsynced). A probe writing "Won't Fix" into a six-wide Status column re-pads the whole column, header and separator included, which the docstring names as re-padding and the changelog's "keeping a hand-aligned table aligned" covers, so read as TRUE. The survivor above was re-tested in isolation, as the standing practice asks, and is decided by that probe, not by the replay alone. DraftToDoneReadyTests and the transition.py readiness gate are BG0954's and are not judged here.

## Steps to Reproduce

1. Read the round 2 REJECT of BG0956 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0956 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The archive writer's `applied /= done` (reconcile.py:3121) is unpinned, and the author's recorded survivor `applied /= set(here)` is not equivalent through the shipped entry point: with one archive sub-index holding a header-less BG0003 row ahead of a headed table holding BG0001, both drifted to Closed with no live row, `reconcile apply` on the shipped code exits 1, names BG0003 "row not in a rewritable layout" and reports "changed 1 row(s), 1 could not be applied", while under the mutant it exits 0, prints "set bug BG0003: Fixed -> Closed" and "changed 2 row(s)" with the BG0003 row still reading Fixed. That is the claimed sync AC4 rules out, and test\_an\_unplaceable\_row\_still\_reports\_unsynced (one id per sub-index) does not catch it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] the rewritten comment at transition.py:1297-1299 still gives "a target status with no summary row" as a cause of residual drift, false since CR0159 (c78bfae9, before the base) made apply insert a missing summary row, as test\_status\_without\_summary\_row\_now\_syncs\_by\_insertion pins; no open bug covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG0956 AC1 still passes: Given a bug whose row `archive.py` moved into `archive/<release>/bug.md`, when `transition.py set` moves it Fixed -> Closed, then the archived row reads Closed, the summary counts agree, the output reports `index synced=True`, and `reconcile detect` reports no drift for it. Fails on: writing only the live index (today), or setting the flag without writing the row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ArchivedRowSyncTests::test_closing_an_archived_bug_rewrites_its_archive_row
- [ ] **AC4** BG0956 AC2 still passes: Given an archived row already out of step with its file, when `reconcile apply` runs, then it rewrites that row and counts it as changed, never "row not in a rewritable layout". Fails on: the apply path still skipping archive sub-indexes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::ArchivedRowApplyTests::test_apply_rewrites_a_stale_archived_row
- [ ] **AC5** BG0956 AC3 still passes: Given an artefact with both a live row and an archived row, then the live row is the one written and the archived row is left as it is, as the census reads them (live wins). Fails on: rewriting both, or the archive first
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::ArchivedRowApplyTests::test_a_live_row_wins_and_the_archive_is_untouched
- [ ] **AC6** BG0956 AC4 still passes: Given a row no writer can place (a header-less table), then `transition.py set` still reports `index synced=False` and `reconcile apply` still names it. Fails on: the archive search turning an unplaceable row into a claimed sync
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::ArchivedRowApplyTests::test_an_unplaceable_row_still_reports_unsynced

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (run twenty-one orchestrator) | Fixed: BG0956 was reviewed again in round three under D0569 and its qa seat (Sam Eriksson) approved, closing the round-two findings this bug carried; BG0956 is Fixed |
