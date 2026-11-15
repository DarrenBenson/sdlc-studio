# BG0947: reference-outputs.md terminal-status table contradicts sdlc_md.TERMINAL_STATUS

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-outputs.md, .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py, changelog.d/BG0947.md
> **Created:** 2026-10-05
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-05T15:44:25Z

## Summary

The Status Vocabulary table in reference-outputs.md disagrees with the code that every gate reads: it lists bug terminal as Closed, Won't Fix, Superseded (code adds Fixed, Verified); story terminal includes Deferred (code does not); CR terminal includes Deferred (code does not); RFC Accepted 'stays live' (code treats it as terminal); and it has no rows for issue or charter. An external reader (a consuming project copied its vocabulary) or an agent following the reference gets the wrong answer. Raised from that project's RV0003 (observability gap analysis, 2026-10-05). BG0001 fixed an earlier divergence; the equality test it proposed would have caught this.

## Steps to Reproduce

1. Read reference-outputs.md, Status Vocabulary table (~line 272). 2. Print `sdlc_md.TERMINAL_STATUS.` 3. Compare bug, story, CR and RFC rows; note issue and charter are missing.

## Proposed Fix

Generate the table from `sdlc_md.STATUS_VOCAB` and `TERMINAL_STATUS`, or add a test asserting the table equals them.

## Acceptance Criteria

- [ ] **AC1** Given `sdlc_md.STATUS_VOCAB` and `sdlc_md.TERMINAL_STATUS`, when the Status Vocabulary table in reference-outputs.md is parsed, then it has exactly one row per type in STATUS_VOCAB (issue and charter included) and each row's allowed and terminal sets equal the code's.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py::StatusVocabDocTests::test_the_table_matches_the_code
- [ ] **AC2** Given a copy of the corrected table with one terminal status removed from one row, when the same comparison runs on it, then it fails naming that type and that status.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py::StatusVocabDocTests::test_a_divergence_names_the_type_and_status

## Notes

- AC1 must fail on: the table at HEAD: bug terminal without Fixed and Verified, story allowed without Blocked, Deferred listed as terminal for story and CR, RFC Accepted read as live, no issue or charter row
- AC2 must fail on: a comparison of row counts, or of the allowed column only
- Still true at HEAD: reference-outputs.md:272-281 against sdlc_md.py:1556-1611. Since filing, STATUS_VOCAB's story list gained Blocked, which the table also lacks.
- The filed Verify lines used `-k` patterns; replaced with node ids. The test maps the table's display names (Test Spec, CR, RFC) to the code's keys; the RFC row's 'stays live' parenthetical goes.
- Two new rows shift the page's generated reading guide (docgen.py reading-guides), which lives in the same file. At 871 lines the page stays inside its ALLOWLIST ceiling (869 + 5%), so tools/check_budgets.py is not touched.
- Affects at HEAD are already right (reference-outputs.md, the new test, changelog.d/BG0947.md). The new module carries a `# test-census-subject:` line naming reference-outputs.md.
- End goal 6 (an agent following the reference gets the vocabulary the gates use) and 1.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-05 | Claude Opus 5.5 | Filed |
| 2026-10-06 | Claude Opus 5.5 (triage) | Groomed: reproduced against HEAD (bug terminal lacks Fixed/Verified, story and CR list Deferred as terminal, RFC Accepted read as live, no issue or charter rows); Affects adds the test AC2 needs; Verify lines added |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed for run fourteen: criteria with Verify lines, notes |
