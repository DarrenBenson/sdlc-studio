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

Decide the rule at the write, where the author can still act, the way parity was decided in BG0637. Two candidates, and the choice is the work: pad the span to CommonMark's own form for a leading or trailing space (one extra space at each end, which renders the value and satisfies MD038), or refuse the value naming the span and the space, as parity is refused. Padding keeps the reviewer's words and is invisible to them; refusing is consistent with the parity rule but makes some true statements unrecordable. Measure the corpus first: how many live rows already carry the shape, and whether either answer changes a rendered value.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `critic._clean` neutralises pipes and newlines and refuses odd backtick parity, but it has nothing to say about a code span whose interior begins or ends with...
- [ ] **AC2** The proposed fix lands, pinned by a test: Decide the rule at the write, where the author can still act, the way parity was decided in BG0637.

## Impact

Blocks commits, at a distance from whoever caused it, and silently narrows what a review ledger can say: a reviewer cannot quote a literal whose trailing space is the fact being reported. Four of BG0637's seven blocked commits this week were this class.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-09 | Claude Opus 5 | Filed |
| 2026-09-09 | Claude Opus 5 | Reproduced on the day it was filed, and it blocked this run's commit. Recording BG0608's three delivery verdicts wrote four rows quoting the budget command's own prefix - a code span whose value ends in a space, which is the whole of this bug - and markdownlint refused both ledgers. Repaired by hand to make the tree committable: the span was rewritten to name the dash in prose. That is a fifth reproduction of the class on top of BG0637's four, and the second time this week that a reviewer could not quote a literal the tool itself prints |
