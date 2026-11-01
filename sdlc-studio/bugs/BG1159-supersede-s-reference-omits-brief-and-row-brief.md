# BG1159: supersede's reference omits --brief and row-brief, two of its new guarantees are unpinned, and a no-match refusal contradicts itself

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_supersede_by_brief.py, changelog.d/BG1159.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, BG1135 APPROVE by qa-seat-BG1135-r1 (brief 9192e9938b5c).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T06:16:20Z

## Summary

qa-seat-BG1135-r1's APPROVE of BG1135 (2026-11-01) left: (1) reference-review.md:576, :579-580 and :587-588 still show supersede narrowing by --reviewer and --verdict only and the record naming (date, verdict, reviewer, author), with no --brief and no row-brief, though help/review.md:59 sends readers there. (2) Naming every candidate's fingerprint is pinned only with two candidates: the mutant `candidates[:2]` at critic.py:1203 survives. (3) Nothing pins that `_retires_brief` matches the whole fingerprint: a case-folded prefix match survives (reachable only by a hand-written record). (4) Pre-existing: when no row matches, the refusal reads 'no delivery verdict row for X dated D (that unit has rows dated D)', contradicting itself and naming no fingerprint (critic.py:1194-1196, already at daf2f295). (5) Pre-existing: superseding a row already retired appends a second identical record and exits 0.

## Steps to Reproduce

1. Read reference-review.md:576-588.
2. In a throwaway worktree apply `candidates[:2]` at critic.py:1203 and run `test_supersede_by_brief.py`: green.
3. `critic.py supersede --unit BG0962 --date 2026-10-07 --brief deadbeef0000 ...` on a ledger copy: the contradictory message.
4. Run the same supersede twice: two records.

## Proposed Fix

Document --brief and row-brief in reference-review.md. Add a three-candidate refusal test and an exact-match join test. Make the no-match refusal say which narrowing excluded every row, naming the candidates' fingerprints. Refuse, or report as a no-op, a supersession of a row already retired.

## Acceptance Criteria

- [ ] **AC1** reference-review.md documents --brief and the row-brief field.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_supersede_by_brief.py
- [ ] **AC2** The candidates[:2] and prefix-match mutants each fail a test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_supersede_by_brief.py
- [ ] **AC3** A no-match refusal names the narrowing that excluded every row and the candidates' fingerprints, and a repeated supersession of a retired row writes no second record.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_supersede_by_brief.py

## Impact

The reference undersells the tool, two guarantees can regress silently, and two refusals mislead.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
