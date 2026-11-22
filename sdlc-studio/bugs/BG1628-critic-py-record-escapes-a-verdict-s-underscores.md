# BG1628: critic.py record escapes a verdict's underscores but not its asterisks, so a ledger row reads a glob such as `name_*` or `other_*` as emphasis and markdownlint (MD037) refuses the commit

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, sdlc-studio/reviews/critic-verdicts.md, changelog.d/BG1628.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_record_asterisk_escape.py
> **Evidence:** file_finding's own markdown-safing has the same blind spot: filing this bug wrapped the underscore part of each glob in a code span and left the asterisk outside it, so the bug's summary failed MD037 until hand-corrected
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T18:30:39Z

## Summary

`_escape_outside_spans` (critic.py around 297) escapes bare underscores and a linking bracket outside code spans, and `_unescape` inverts only those. A verdict naming globs outside a code span, such as `no author_mutants_* or mutation_edits_* folder`, is written to critic-verdicts.md as `author\_mutants\_* or mutation\_edits\_*`, which markdownlint reads as emphasis with inner spaces (MD037), so the next paperwork commit is refused. Run eighteen's US1202 round-two row (critic-verdicts.md line 2045) was the first; the ledger now disables MD037 as an interim (D0543), the same pattern BG1073 used for MD034.

## Steps to Reproduce

Record a verdict whose findings say `a_* or b_*` outside backticks, then run markdownlint on sdlc-studio/reviews/critic-verdicts.md: MD037 at that row.

## Proposed Fix

Escape a bare asterisk outside code spans in `_escape_outside_spans` and undo it in `_unescape`, pinned by a round-trip test, then drop MD037 from the ledger's disable line.

## Acceptance Criteria

- [ ] **AC1** Given a verdict whose findings say `a_* or b_*` outside backticks, when `critic.py record` writes it and markdownlint runs on sdlc-studio/reviews/critic-verdicts.md, then the row passes MD037 and reads back as the original text, asterisks and underscores intact. Fails on: `a\_* or b\_*` read as emphasis, refusing the commit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_asterisk_escape.py::CriticRecordAsteriskEscapeTests

- [ ] **AC2** Given the ledger's markdownlint disable line, when markdownlint runs on the ledger, then MD037 is no longer disabled and the ledger still passes. Fails on: MD037 disabled as an interim.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_asterisk_escape.py::CriticLedgerMd037Tests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-22 | Claude Sonnet 5.5 (qa seat, groom) | Acceptance criteria authored for planning (run twenty-two) |
