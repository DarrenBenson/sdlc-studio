# BG0659: a code span whose value ends in a space cannot be recorded in any review ledger - markdownlint MD038 refuses the row

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** BG0637 revision history, reproductions four to seven (2026-09-09). Delivery review of BG0637, product seat, tagged [pre-existing]: `_clean` returns a span with a trailing space verbatim and .markdownlint.json sets default true.
> **Created:** 2026-09-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`critic._clean` neutralises pipes and newlines and refuses odd backtick parity, but it has nothing to say about a code span whose interior begins or ends with a space. Markdownlint's MD038 refuses exactly that, and `.markdownlint.json` sets default true, so the row reaches the ledger and the NEXT commit that touches the file is blocked - by a rule about a row somebody else wrote. Four of BG0637's seven recorded reproductions are this class, not the parity class BG0637 fixed: a reviewer quoting a bare word with a trailing space, the withdrawal sentinel literal whose trailing space is part of the value, an http verifier with a trailing ellipsis, and a level-two heading marker whose trailing space is the whole point of the quote. There is no way to write any of those in a ledger row today, so the writer refuses to record facts about its own siblings' contracts. BG0634 is Won't Fix on a different premise (a fixed-width truncation that does not exist) and does not discharge this.

## Steps to Reproduce

1. Record a verdict whose finding quotes a literal ending in a space, inside a code span - the withdrawal sentinel is the live example.
2. The row is written: no refusal, no rewrite.
3. Run markdownlint over the ledger. MD038 fires on that row.
4. The next commit touching that file is blocked, naming a row the committer did not write.

## Proposed Fix

Refuse at the write, where the author can still act, the way parity was decided in BG0637: a finding carrying a code span whose interior begins or ends with a space is refused, naming the span and which edge carries the space, and nothing is written. The other candidate - padding the span to CommonMark's form - is REFUTED by execution (2026-09-15, the repository's own markdownlint 0.49.1 with `.markdownlint.json`): `` `budget: ` ``, `` ` budget:  ` ``, `` `  x` `` and `` `  x ` `` each raise MD038, and only a span with no edge space passes. Padding would have shipped a fix that still blocks the next commit. The refusal's remedy names the two ways that do lint: quote the value without the space and state the space in prose, or move the literal out of the span.

## Acceptance Criteria

- [ ] **AC1** `critic.py record` refuses a finding whose code span ends in a space, naming the span and the trailing edge, and writes no row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CodeSpanEdgeSpaceTests::test_a_trailing_space_span_is_refused_by_the_cli
- [ ] **AC2** `critic.py record` refuses a finding whose code span begins with a space, naming the span and the leading edge, and writes no row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CodeSpanEdgeSpaceTests::test_a_leading_space_span_is_refused_by_the_cli
- [ ] **AC3** A finding whose code spans carry no edge space records byte for byte as today - the paired control
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CodeSpanEdgeSpaceTests::test_a_clean_span_records_unchanged
- [ ] **AC4** Every span the writer admits passes markdownlint's MD038 under the repository's own config, measured through the linter rather than restated
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CodeSpanEdgeSpaceTests::test_every_admitted_span_passes_md038

## Impact

Blocks commits, at a distance from whoever caused it, and silently narrows what a review ledger can say: a reviewer cannot quote a literal whose trailing space is the fact being reported. Four of BG0637's seven blocked commits this week were this class.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-09 | Claude Opus 5 | Filed |
| 2026-09-09 | Claude Opus 5 | Reproduced on the day it was filed, and it blocked this run's commit. Recording BG0608's three delivery verdicts wrote four rows quoting the budget command's own prefix - a code span whose value ends in a space, which is the whole of this bug - and markdownlint refused both ledgers. Repaired by hand to make the tree committable: the span was rewritten to name the dash in prose. That is a fifth reproduction of the class on top of BG0637's four, and the second time this week that a reviewer could not quote a literal the tool itself prints |
| 2026-09-10 | Claude Opus 5 | Ruled OPEN for v5.1 on 2026-09-10, under D0186's disclosure half. It is a defect in what a reviewer can RECORD, not in what the tool decides: a value whose code span ends in a space is refused by markdownlint after `_clean` writes it, and the reviewer's remedy - trim the span or restate the value - costs one edit and loses nothing. Three points against a run already over its appetite, in the same function BG0637 has just been through twice; changing `_clean` again in the same week is how the third round of a repair gets shipped untested. It ships disclosed, and it is the first Medium on the next batch. |
| 2026-09-15 | sprint planning 2026-09-15 | Groomed for the next batch: the design choice the bug left open is decided by execution. Padding a code span to CommonMark's form still raises MD038 under the repository's markdownlint 0.49.1, so the fix is to refuse at the write, naming the span and the edge, as parity is refused. Four real criteria replace the two tool-derived ones. |
