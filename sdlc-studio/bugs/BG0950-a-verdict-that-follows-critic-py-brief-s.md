# BG0950: A verdict that follows `critic.py brief`'s return contract to the letter is refused by `critic.py record --from-verdict`

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_verdict_contract_roundtrip.py
> **Evidence:** Found migrating agent-bridge (Engram-Labs-UK) from skill 2.4.1 to the installed 6.1.0 on 2026-10-06; reproduced against sdlc-studio main at aa19a2e3.
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T12:35:17Z

## Summary

The brief's `_RETURN_CONTRACT` (critic.py:2179-2190) tells the reviewer to tag each ISSUES finding with its origin, and asks for `BLOCKING: <the subset that must be fixed before Done, or 'none'>` - a subset, with no instruction to tag it. `parse_verdict_block` (critic.py:2668-2670) then folds the BLOCKING text into the issues string as `BLOCKING: <text>`, and `parse_findings` splits on `;` and requires every item to carry an origin tag. So:

1. A BLOCKING list of more than one item, written as the contract asks, is refused: the first item keeps the tool's `BLOCKING:` prefix but has no tag, and every later item has neither.
2. A semicolon used as ordinary punctuation inside one finding splits it, and the second half is refused as untagged. The `\;` escape exists (critic.py:3429) but only the `--issues` flag help mentions it; the brief a reviewer actually reads does not.
3. Even when the reviewer does tag the BLOCKING items, each blocking finding is recorded twice - once from ISSUES, once from the fold.

In the agent-bridge US0601 review a fresh-context reviewer returned exactly the contract's shape (8 tagged findings, 3 untagged blocking items, one in-finding semicolon) and record refused it. The block had to be hand-edited - `[new]` added to each BLOCKING item and a `\;` inserted - before it would record, which is the author touching the reviewer's verdict.

## Steps to Reproduce

From .claude/skills/sdlc-studio/scripts:

```bash
python3 -c "import sys; sys.path.insert(0,'.'); import critic; v,i=critic.parse_verdict_block('VERDICT: REJECT\nISSUES: [new] AC1 is false (a.ts:10); [new] the doc is wrong (D.md:94)\nBLOCKING: AC1 is false; the doc is wrong\n'); print(critic.unclassified_findings(i))"
```

Observed: ['BLOCKING: AC1 is false', 'the doc is wrong']. The same with `which no test can fail; the AC text was never amended` inside one ISSUES finding returns the second half as unclassified.

## Proposed Fix

Make the contract and the parser agree. Either BLOCKING items inherit their origin from the matching ISSUES finding (they are a subset by definition) or the contract says to tag them; record each blocking finding once, as a flag on its ISSUES entry, not a second copy; and either put the `\;` escape in `_RETURN_CONTRACT` or stop splitting findings on bare semicolons.

## Acceptance Criteria

- [ ] **AC1** A block written exactly to `_RETURN_CONTRACT` - tagged ISSUES and an untagged BLOCKING subset of two or more items - records without edits, shown by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_contract_roundtrip.py -k contract_block_records
- [ ] **AC2** A blocking finding appears once in the recorded row, marked blocking
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_contract_roundtrip.py -k blocking_recorded_once
- [ ] **AC3** A semicolon inside one finding either survives as one finding or the brief's contract states the escape, shown by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_contract_roundtrip.py -k semicolon_in_finding

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | Claude Opus 5.5 | Filed |
