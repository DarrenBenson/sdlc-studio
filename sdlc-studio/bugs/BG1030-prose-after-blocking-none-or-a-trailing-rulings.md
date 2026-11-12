# BG1030: Prose after `BLOCKING: none`, or a trailing `RULINGS:` line, is folded into BLOCKING and refused, so an APPROVE carrying rulings cannot be recorded unedited

> **Status:** Fixed
> **Supersedes:** BG1076
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_verdict_contract_roundtrip.py, .claude/skills/sdlc-studio/reference-scripts-review.md, changelog.d/BG1030.md
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

- Checked at HEAD (2026-11-12): the defect still reproduces, and no criterion is met. `parse_verdict_block` (critic.py:3584) reads BLOCKING with `_block_field` (critic.py:3573), bounded only by `_BLOCK_TOKENS` (critic.py:3570), and reads it as none only when the whole field is `none` (critic.py:3607). The Steps block, `BLOCKING: none.` followed by a sentence, and `BLOCKING: none` followed by a blank line and a sentence are each refused by `_mark_blocking` (critic.py:3666) as an untagged item quoting no finding.
- The rejoinder brief (`rejoinder_brief`, critic.py:3540-3566) ends with the unchanged `_RETURN_CONTRACT` and names no RULINGS line. Put the rejoinder's RULINGS line in its own constant printed after `_RETURN_CONTRACT`, so the contract stays one constant: `neutrality_violations` strips it by exact match (critic.py:2204), and US1011 prints the verdict path after it.
- Existing pins: test_verdict_contract_roundtrip.py drives `record --from-verdict` over contract-shaped blocks, runs a rejoinder (line 252) and reads `_RETURN_CONTRACT` (line 342); test_critic.py holds the `--from-verdict` tests (lines 731-857) and the rejoinder tests (lines 882-930). reference-scripts-review.md:107 and :111 describe the parse and the rejoinder's contract. `lib/lanes.py` `_blocking` (lib/lanes.py:380) parses through `parse_verdict_block` and needs no change.
- Builds first in EP0280: US1011 depends on it, and every EP0280 unit changes critic.py.

## Acceptance Criteria

- [ ] **AC1** Given a block whose BLOCKING is `none` followed by a sentence, when it is recorded, then it records with no blocking finding and the sentence is not lost
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py::TrailingProseTests::test_prose_after_blocking_none_records
  - **Verified:** yes (2026-11-12)
- [ ] **AC2** Given a block with a `RULINGS:` line after `BLOCKING: none`, when it is recorded, then it records, and the rulings are kept on the row or the contract names where they go
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py::TrailingProseTests::test_a_rulings_line_records
  - **Verified:** yes (2026-11-12)
- [ ] **AC3** Given a rejoinder brief, its return contract names the RULINGS line, and a round-2 verdict that rules each earlier finding CLOSED, OVER-CLAIMED or MOVED there is recorded without re-emitting, with the rulings stored as rulings and not as a [new] finding
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py::TrailingProseTests::test_the_rejoinder_contract_names_rulings_and_they_record_as_rulings
  - **Verified:** yes (2026-11-12)

## Impact

An APPROVE with rulings, the shape a careful reviewer returns, is refused and must be re-emitted or edited by the author.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): supersedes BG1076 |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: reproduced at HEAD, line references added, Affects gains test_verdict_contract_roundtrip.py and reference-scripts-review.md, the RULINGS line placed after the unchanged contract |
