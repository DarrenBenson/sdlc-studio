# BG0962: closing-review reads a unit's latest verdict only from the frozen sprint-review ledger, so a frozen batch REJECT outlives a later per-unit APPROVE and blocks the close as a hard correctness gate

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_closing_review_per_unit_verdicts.py, changelog.d/BG0962.md
> **Evidence:** Found closing a consuming project's RUN-01M4APNQ on 2026-10-07 with the installed 6.1.0; reproduced against sdlc-studio main at fb1ce886 by reading the code path.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T11:00:15Z

## Summary

`_ck_closing_review` (`sprint_report.py` ~1157) decides which units are unresolved from `latest[unit]`, folded by `_verdict_entries` (~1078) over `ctx['sprint_reviews']` - which `critic.sprint_reviews` (critic.py ~1371) reads from `reviews/sprint-review-record.md` ONLY. That ledger is frozen history in 6.x (migrate reports it as 'frozen history, left as written'; the lean loop records each unit with `critic.py record` into `critic-verdicts.md`). So a unit REJECTed in a pre-6.x batch review keeps that REJECT as its 'latest verdict' forever: its later per-unit rounds in critic-verdicts.md - however many APPROVEs - never enter the fold.

The row's own coverage reading (`review_coverage`) reads both ledgers and reports the unit covered; the verdict fold then marks it 'unresolved' anyway, because the frozen REJECT is the only verdict it can see.

Consequences: (1) `sprint close` refuses; (2) `--file-and-close` refuses too, because closing-review is classed a hard correctness blocker; (3) the only remaining exit is a `rule:sprint-checklist:closing-review` waiver, which cannot be scoped to a unit (`closing-review:BG0460` is refused as 'not a checklist item') and has no expiry, so it would switch the check off for every future run. A run whose every unit is independently approved therefore cannot close honestly.

Concrete case: the consuming project's BG0460 was REJECTed in the 2026-09-16 frozen batch review (RUN-01KY7P5Y) and in RUN-01M4APNQ received a full-tier per-unit REJECT, a round-2 APPROVE from the same reviewer, and a post-approval confirmation APPROVE (critic-verdicts.md, 2026-10-07). `critic.py show --unit BG0460` reports APPROVE; review-coverage reports 10/10; closing-review reports '1 unresolved: BG0460'.

## Steps to Reproduce

1. A unit has a REJECT row in reviews/sprint-review-record.md (a pre-6.x batch review).
2. In a later run it is reviewed per-unit with `critic.py record` - REJECT then APPROVE by the same reviewer.
3. `sprint.py close --retro <id> --dry-run` -> `STOP checklist: closing-review: ... 1 unresolved ... no APPROVE covers: <unit>`, while `review-coverage: N/N covered` passes and `critic.py show --unit <unit>` reports APPROVE.
4. `--file-and-close` -> refused (hard correctness blocker).

## Proposed Fix

Fold the per-unit verdict ledger (critic-verdicts.md) into `_verdict_entries` alongside the frozen batch ledger, ordered by date with the append-order tiebreak, so a later per-unit APPROVE supersedes an earlier frozen batch REJECT (and a later per-unit REJECT still supersedes an earlier APPROVE - keep US0593's 'a non-APPROVE is terminal for that revision' semantics by time, not by ledger). Alternatively scope checklist waivers to a unit and give them an expiry, so a defect like this has a bounded exit.

## Acceptance Criteria

- [ ] **AC1** A unit whose frozen batch REJECT predates a per-unit APPROVE is not reported unresolved by closing-review, shown by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_closing_review_per_unit_verdicts.py -k frozen_reject_then_per_unit_approve
  - **Verified:** yes (2026-10-07)
- [ ] **AC2** A per-unit REJECT recorded after an APPROVE still makes the unit unresolved (US0593 kept), shown by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_closing_review_per_unit_verdicts.py -k later_per_unit_reject_wins
  - **Verified:** yes (2026-10-07)
- [ ] **AC3** On a batch whose verdicts span both ledgers, closing-review never clears a unit `review_coverage` reports uncovered (a per-unit REJECT after a frozen APPROVE; a per-unit self-review APPROVE after a frozen REJECT), and clears a covered unit whose latest verdict across both ledgers is an APPROVE (a per-unit APPROVE after a frozen REJECT). It is deliberately stricter than coverage in AC4 and AC5
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_closing_review_per_unit_verdicts.py -k agrees_with_review_coverage
  - **Verified:** yes (2026-10-07)
- [ ] **AC4** A per-unit APPROVE dated before a frozen batch REJECT does not clear the unit (US0593's later-REJECT rule, across the ledgers)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_closing_review_per_unit_verdicts.py -k earlier_per_unit_approve_does_not_clear
  - **Verified:** yes (2026-10-07)
- [ ] **AC5** A per-unit APPROVE and a frozen batch REJECT on the same day hold the unit, since the ledgers record days and cannot order them
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_closing_review_per_unit_verdicts.py -k same_day_tie
  - **Verified:** yes (2026-10-07)
- [ ] **AC6** A same-day per-unit REJECT after a frozen APPROVE is labelled unresolved: a same-day per-unit non-APPROVE sorts after the batch rows
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_closing_review_per_unit_verdicts.py -k same_day_per_unit_reject_reads_unresolved
  - **Verified:** yes (2026-10-07)
- [ ] **AC7** An unreadable per-unit ledger is read as no verdict: the checklist still answers and the frozen verdict decides
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_closing_review_per_unit_verdicts.py -k unreadable_per_unit_ledger
  - **Verified:** yes (2026-10-07)

## Triage

- Reproduced at fb1ce886 by the code path: `_ck_closing_review` (sprint_report.py:1157) folds each unit's latest verdict from `_verdict_entries`, which reads only `ctx['sprint_reviews']`, the rows `critic.sprint_reviews` keeps from the frozen batch ledger. A frozen REJECT therefore holds a unit open after any number of per-unit APPROVEs. The fold dates from US0593 (75c17d01, 2026-08-07) and broke when the lean loop moved verdicts to `critic-verdicts.md`; not a regression of a recent run.
- `reconcile detect` suggests US0914 may already deliver this. It does not: US0914 made a round-2 APPROVE from the rejecting reviewer the exit from a REJECT, which is the case recorded here, but the closing-review fold never reads the ledger that APPROVE is in.
- High holds: a run whose every unit is independently approved cannot close, and the only exit switches the check off for every later run. Prefer the fold over scoped waivers; a waiver with a unit scope and an expiry is a separate change.

## Review round 1 (REJECT, 2026-10-07)

- BLOCKING, closed: AC3 said the row clears a unit exactly when coverage calls it covered, which AC4 and AC5 contradict by design. AC3 is reworded to what the row does, and its test now holds a frozen REJECT followed by a self-review APPROVE, so the fold-alone mutant fails it.
- Docstrings: the AC2, AC4 and AC5 tests now carry their right labels and name only the mutants they kill.
- Comment claims: the same-day ordering (AC6) and the unreadable-ledger guard (AC7) are pinned. The claim that per-unit verdicts come from `verdict_for` is not pinnable with product-shaped rows: the only case that tells it from the latest row is a second reviewer's APPROVE after a REJECT, and `record_verdict` now refuses that round. It stays a comment.
- Label changes accepted, the row held either way: a frozen REJECT then a self-review or empty-author APPROVE now reads `unreviewed` where it read `unresolved` (no independent pass answers the REJECT), and a unit whose only verdict is a self-review reads `unreviewed` where it read `none recorded`.
- The pre-existing finding (coverage reads a unit's whole ledger, not its current delivery) is filed as its own bug.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Groomed: reproduced at fb1ce886 by the code path (`_ck_closing_review` folds `latest` from `critic.sprint_reviews`, the frozen batch ledger, only); consuming-project name generalised for the neutrality lane; reconcile's US0914 advisory dismissed; changelog fragment added to Affects |
| 2026-10-07 | Claude Opus 5.5 (engineering seat) | Built on the fast-track (D0348): per-unit verdicts from `critic.verdict_for` merged into the closing-review fold by date. AC3 made precise; AC4 (US0593 kept across the ledgers) and AC5 (a same-day tie fails closed) added; Affects trimmed to the files changed, `critic.py` needing none |
| 2026-10-07 | Claude Opus 5.5 (engineering seat) | Repaired after the round-1 REJECT: AC3 reworded, AC6 and AC7 added, test docstrings corrected, the fold-alone mutant killed by AC3's own test |
