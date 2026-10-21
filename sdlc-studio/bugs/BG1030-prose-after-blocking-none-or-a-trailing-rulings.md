# BG1030: Prose after `BLOCKING: none`, or a trailing `RULINGS:` line, is folded into BLOCKING and refused, so an APPROVE carrying rulings cannot be recorded unedited

> **Status:** Open
> **Supersedes:** BG1076
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py, changelog.d/BG1030.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T08:28:48Z

## Summary

`parse_verdict_block` reads BLOCKING to the next contract token or the end of the block (`_block_field`, critic.py). A reviewer who writes `BLOCKING: none` and then a sentence, or a `RULINGS:` line after it (a token the contract does not list), has that text read as BLOCKING content: it is no longer 'none', is split into items, and refused as quoting no ISSUES finding. Found by the round-1 QA review of BG0950 on 2026-10-13, which ruled it pre-existing and outside BG0950's criteria; BG0950's Further evidence records it from BG0989's reviews (2026-10-07/08), where an APPROVE's rulings could not be recorded.

## Steps to Reproduce

Record `VERDICT: APPROVE\nISSUES: none\nBLOCKING: none\nRULINGS: AC2 is satisfied by the CLI test` with `critic.py record --from-verdict`: refused.

## Proposed Fix

Read BLOCKING as none when its first item is `none`, and either accept `RULINGS:` as a contract token or say in the contract where rulings go; never fold text after `none` into blocking items.

## Acceptance Criteria

- [ ] **AC1** Given a block whose BLOCKING is `none` followed by a sentence, when it is recorded, then it records with no blocking finding and the sentence is not lost
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py::TrailingProseTests::test_prose_after_blocking_none_records
- [ ] **AC2** Given a block with a `RULINGS:` line after `BLOCKING: none`, when it is recorded, then it records, and the rulings are kept on the row or the contract names where they go
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py::TrailingProseTests::test_a_rulings_line_records
- [ ] **AC3** Given a rejoinder brief, its return contract names the RULINGS line, and a round-2 verdict that rules each earlier finding CLOSED, OVER-CLAIMED or MOVED there is recorded without re-emitting, with the rulings stored as rulings and not as a [new] finding
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py::TrailingProseTests::test_the_rejoinder_contract_names_rulings_and_they_record_as_rulings

## Impact

An APPROVE with rulings, the shape a careful reviewer returns, is refused and must be re-emitted or edited by the author.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): supersedes BG1076 |
