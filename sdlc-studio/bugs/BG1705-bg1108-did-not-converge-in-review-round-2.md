# BG1705: BG1108 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_carried_review_base.py, changelog.d/BG1108.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T14:33:41Z

## Summary

BG1108 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] No test pins the guard that carries a REJECT naming no brief at the commit checked out (`_noted_row(repo_root, uid, fp) if fp else None`, critic.py:2125). The mutant `_noted_row(repo_root, uid, fp or None)` reads the unit's latest note whatever brief cut it: the mistake round one's first finding named, for the one REJECT whose row carries no fingerprint. It survives every test module that touches the carry (174 passed across the twelve modules naming `carry_at_cap`, `review_base` or `carried_review_base`, `test_carried_review_base.py` and `test_run_state.py` among them). The case is reachable through the shipped CLI: `critic.py record` at the cap with no `--brief` exits 0 and carries the unit. Re-tested alone, with a qa brief cut at one commit and a later commit to `src/a.py` before that record, the code records the later commit checked out, as the docstring's "when no note names that fingerprint" says. The mutant records the brief's earlier commit. Pin the answer the unit means for a REJECT recorded with no brief; RULINGS: Prior finding "The capping REJECT's commit is read from the brief note its own fingerprint names" CLOSED. `test_the_capping_reject_reads_its_own_briefs_commit_not_the_units_latest_note` briefs qa, commits to `src/a.py`, briefs product at the later commit and records the qa REJECT at the cap with the qa fingerprint. My replay of `_noted_row(repo_root, uid)` is killed by it. Prior finding "`carried_review_base` folds the briefed id" CLOSED. `test_a_carried_unit_is_found_by_its_id_in_lower_case` reads both the carry bug's id and the carried unit's id in lower case, and it briefs the carry bug's lower-case id through the CLI. My replay of `uid = unit` is killed by it. A probe briefing the carried unit's own lower-case id through `critic.py brief` prints the judged commit's diff (rc 0). Prior finding "The `carry_at_cap` docstring (critic.py:2091-2094) and `changelog.d/BG1108.md` say" CLOSED. Both now name the two fallbacks, a fingerprint no note names and a note that records no commit. `test_a_note_that_records_no_commit_carries_at_the_commit_checked_out` pins the second fallback, killing both the mutant that reads the missing commit as "None" and the one that records no commit. Claim inventory: the changelog is TRUE by execution, its "with the id given in either case" included. The `carry_at_cap` docstring and the repair commit's BG1108 paragraph are TRUE. The new test docstrings name mutants each test kills. AC1's Verify passes (`verify_ac.py run --id BG1108 --dry-run`, 1 of 1). Mutation pass, in a throwaway clone with each file's bytes restored, killed these mutants: the fingerprint dropped, the id compared as typed, the missing commit read as "None", no fallback to the commit checked out, the fallback always taken, the first carry winning, and the carry bug's drop left unread. The one survivor is the finding, re-tested alone. No pre-existing finding.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1108 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1108 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] No test pins the guard that carries a REJECT naming no brief at the commit checked out (`_noted_row(repo_root, uid, fp) if fp else None`, critic.py:2125). The mutant `_noted_row(repo_root, uid, fp or None)` reads the unit's latest note whatever brief cut it: the mistake round one's first finding named, for the one REJECT whose row carries no fingerprint. It survives every test module that touches the carry (174 passed across the twelve modules naming `carry_at_cap`, `review_base` or `carried_review_base`, `test_carried_review_base.py` and `test_run_state.py` among them). The case is reachable through the shipped CLI: `critic.py record` at the cap with no `--brief` exits 0 and carries the unit. Re-tested alone, with a qa brief cut at one commit and a later commit to `src/a.py` before that record, the code records the later commit checked out, as the docstring's "when no note names that fingerprint" says. The mutant records the brief's earlier commit. Pin the answer the unit means for a REJECT recorded with no brief
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1108 AC1 still passes: The brief for a carried unit's redelivery names a diff from the commit its capping REJECT judged, and that diff holds the repair landed before the new run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_carried_review_base.py::CarriedReviewBaseTests::test_a_carried_units_brief_diffs_from_the_commit_its_capping_reject_judged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
