# BG1769: US1339 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/reference-prd.md, .claude/skills/sdlc-studio/reference-pvd.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/help/pvd.md, .claude/skills/sdlc-studio/templates/personas/amigo-template.md, .claude/skills/sdlc-studio/templates/personas/review-seat-charter.md, tools/tests/test_lean_ownership_wording.py, changelog.d/US1339.md
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-26T08:27:49Z

## Summary

US1339 was rejected at round 2, the review cap, by agent-a5d91f1fac34c64de (qa), so it was carried as a known issue rather than reviewed again. Filed at Low rather than the carry's default Medium: the release bar (`review.blocking_priority`) bars Medium, and Low is the most severe level it allows. The findings still open: BLOCKING: [new] the repaired header check misses "Ownership" though its comments say it catches any wording: tools/tests/test\_lean\_ownership\_wording.py:43 says the pattern catches "a table column headed by ownership, in any wording" and :196 says "A column headed by ownership is caught in any wording", but `OWNS_HEADER` (:44) admits only own, owns, owned, owner and owners as whole words, so it does not match "Ownership" or "Owning" (re.search printed False for both). Applied alone in a detached worktree at ead398980, a seats-table header row whose second cell reads Ownership (reference-workflow-personas.md:125) left all five tests green (5 passed), and one reading Owning did the same, so the round-one exact-cell defect survives in that shape and both comments over-claim (origin ead398980 by `git log -S"in any wording"`); RULINGS: Round-one findings. CLOSED: the PRD leg's completion condition loses "and tracked". reference-review.md:154 and reference-prd.md:204 both read confirmed met or the gaps are named and tracked, and reverting either to the round-one shape (gaps named, each gap is named) now fails the AC2 test. CLOSED: the AC1 and AC4 oracle misses the seats' abbreviations. "(PM owns it)" in help/pvd.md, "It is owned by the PM." in reference-pvd.md and "In practice the PO owns the PRD." in reference-prd.md each fail two tests now, and dropping PO and PM from the seat pattern fails the planted self-test. MOVED: the AC3 header check is an exact-cell match. "Owns (the document)" and "Owner of" now fail, "Ownership" and "Owning" still pass (the ISSUES finding). Checks at ead398980: both unit modules 8 passed, verify\_ac run --id US1339 --dry-run printed ac=5 pass=5, tools/check\_links.py printed "All markdown links resolve", tools/lint-style.sh exit 0, docgen.py reading-guides --check printed 0 drift item(s), the 15 modules that read the touched pages 201 passed. Mutation pass on the repair: 13 mutants on this unit, 9 killed. The survivors are the two headings in ISSUES and two test mutants only a page mutant can kill (the header check reverted to the exact cell, the confirmed met assertion dropped). The repair touched only files the two units declare. D0636 still holds: reference-prd.md step 4 keeps its direct edit.

## Steps to Reproduce

1. Read the round 2 REJECT of US1339 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US1339 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the repaired header check misses "Ownership" though its comments say it catches any wording: tools/tests/test\_lean\_ownership\_wording.py:43 says the pattern catches "a table column headed by ownership, in any wording" and :196 says "A column headed by ownership is caught in any wording", but `OWNS_HEADER` (:44) admits only own, owns, owned, owner and owners as whole words, so it does not match "Ownership" or "Owning" (re.search printed False for both). Applied alone in a detached worktree at ead398980, a seats-table header row whose second cell reads Ownership (reference-workflow-personas.md:125) left all five tests green (5 passed), and one reading Owning did the same, so the round-one exact-cell defect survives in that shape and both comments over-claim (origin ead398980 by `git log -S"in any wording"`)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** US1339 AC1 still passes: No page says a seat owns the PRD or the PVD
  - **Verify:** pytest tools/tests/test_lean_ownership_wording.py::OwnershipWordingTests::test_no_page_says_a_seat_owns_the_prd_or_the_pvd
- [ ] **AC3** US1339 AC2 still passes: The review legs say the seat signs under delegated authority
  - **Verify:** pytest tools/tests/test_lean_ownership_wording.py::OwnershipWordingTests::test_the_review_legs_say_the_seat_signs_under_delegated_authority
- [ ] **AC4** US1339 AC3 still passes: The seats section names the person as owner and the seat as delegate
  - **Verify:** pytest tools/tests/test_lean_ownership_wording.py::OwnershipWordingTests::test_the_seats_section_names_the_person_as_owner_and_the_seat_as_delegate
- [ ] **AC5** US1339 AC4 still passes: No shipped page or template calls a seat a document owner
  - **Verify:** pytest tools/tests/test_lean_ownership_wording.py::OwnershipWordingTests::test_no_shipped_page_calls_a_seat_a_document_owner
- [ ] **AC6** US1339 AC5 still passes: The wording test proves it can fail
  - **Verify:** pytest tools/tests/test_lean_ownership_wording.py::OwnershipWordingTests::test_the_patterns_fail_on_a_planted_owner_sentence

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Filed |
