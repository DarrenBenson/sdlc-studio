# BG0947: reference-outputs.md terminal-status table contradicts sdlc_md.TERMINAL_STATUS

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-outputs.md, .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py
> **Created:** 2026-10-05
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-05T15:44:25Z

## Summary

The Status Vocabulary table in reference-outputs.md disagrees with the code that every gate reads: it lists bug terminal as Closed, Won't Fix, Superseded (code adds Fixed, Verified); story terminal includes Deferred (code does not); CR terminal includes Deferred (code does not); RFC Accepted 'stays live' (code treats it as terminal); and it has no rows for issue or charter. An external reader (sdlc-studio-lens copied its vocabulary) or an agent following the reference gets the wrong answer. Raised from sdlc-studio-lens RV0003 (observability gap analysis, 2026-10-05). BG0001 fixed an earlier divergence; the equality test it proposed would have caught this.

## Steps to Reproduce

1. Read reference-outputs.md, Status Vocabulary table (~line 272). 2. Print `sdlc_md.TERMINAL_STATUS.` 3. Compare bug, story, CR and RFC rows; note issue and charter are missing.

## Proposed Fix

Generate the table from `sdlc_md.STATUS_VOCAB` and `TERMINAL_STATUS`, or add a test asserting the table equals them.

## Acceptance Criteria

- [ ] **AC1** The Status Vocabulary table in reference-outputs.md has a row for every type in `sdlc_md.STATUS_VOCAB` (issue and charter included), and each row's allowed and terminal sets equal `STATUS_VOCAB` and `TERMINAL_STATUS`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py -k table_matches_code
- [ ] **AC2** A table that differs from the code by one terminal status fails the check, naming the type and the status
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py -k divergence_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-05 | Claude Opus 5.5 | Filed |
| 2026-10-06 | Claude Opus 5.5 (triage) | Groomed: reproduced against HEAD (bug terminal lacks Fixed/Verified, story and CR list Deferred as terminal, RFC Accepted read as live, no issue or charter rows); Affects adds the test AC2 needs; Verify lines added |
