# BG1032: BG0950 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_verdict_contract_roundtrip.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/reconcile.py, changelog.d/BG0950.md, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, changelog.d/BG0950.md, changelog.d/BG1032.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_file_history.py
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T09:26:29Z

## Summary

BG0950 was rejected at round 2, the review cap, by qa seat (BG0950 r1), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the return contract's semicolon rule is false inside a CLOSED bracket, and the record it yields is silently wrong. critic.py:2255 tells the reviewer that a `\;` inside parentheses or brackets stays in its finding, but the repair ends the finding there whenever an origin tag follows, at any depth (critic.py:1164). Recorded through `critic.py record --from-verdict` with `BLOCKING: none`, `[new] round 1's first finding (an unclosed bracket\; [regression] per its tag) is still open (critic.py:1160)` records as one new and one regression finding, so the blocking count goes from 1 to 2, and a pre-existing tag quoted the same way moves the rest of a new finding into a pre-existing one. Both are AC3 inputs, a tagged finding whose evidence holds a semicolon, that do not record as one finding in the reviewer's words. The behaviour is the base ref's, but the rule that invites the shape is new: the changelog's closing line, that the contract now states these rules (changelog.d/BG0950.md:20), is false for the tag rule, and its "even inside an unclosed bracket" (lines 12-13) implies a closed one holds. Keep the `\;` when its bracket closes within the finding, or state the tag rule and its escape in the contract, and pin whichever ships [LC-018]; BLOCKING: [new] the repair's code-span carve-out is unpinned. Making a `\;` with an origin tag after it end the finding inside a closed span too (the `not in_code` guard on the tag split, critic.py:1164) survives test\_verdict\_contract\_roundtrip.py, test\_critic.py and test\_lean\_file\_history.py, and under it a finding that quotes a prior finding in a code span, the shape a rejoinder verdict takes, records a phantom regression finding (2 findings become 3, blocking count 1 to 2). The only span test, test\_a\_code\_span\_and\_an\_escape\_keep\_their\_semicolons, quotes `a\; b`, with no tag after its `\;`; [new] a code span opened by two backticks does not hold its `\;`, though the contract now says a code span does. The scanner pairs single backtick characters (critic.py:1143-1144) where the ledger's own `_scan_ticks` pairs runs, so such a span is cut at its `\;` and the tail refused as unclassified, as at the base ref. It fails closed and names the fragment, costing a re-emit rather than a wrong record (non-blocking); [new] the guard that ignores a closer with no opener (critic.py:1161) is unpinned. Dropping it survives all three modules, and under it `[new] two defects: a) the gate skips (gate.py:40\; also 52) and b) nothing warns` is refused, because the `a)` takes the depth below zero (non-blocking); [regression] the brief's history section now quotes identifiers in code spans with the escape backslash for rows written before d309b239. reconcile.py:2099 reads a cell with `_unescape_outside_spans`, which leaves span interiors alone, where the base ref unescaped every backslash pair, so 22 of the 316 units with a REJECT row (BG0644 and US0671 among them) now show `test\_config` where the base showed the bare identifier. parse\_findings reads those legacy rows the same way, and the same change keeps genuine backslashes the base dropped (US0984's `\.local/`), so it is reported, not held. No test pins the reader's unescape: reading the cell raw survives all three modules (non-blocking); [pre-existing] reconcile.blocking\_findings drops any finding whose text holds the literal pre-existing tag (reconcile.py:2101, a substring test since 293a36dd) instead of reading its origin, so a regression or new finding that quotes a pre-existing one never reaches a later brief's history. Now that a quoted finding is read whole, it drops round 1's first blocking finding from BG0950's own history. No open Bug or CR carries it

## Steps to Reproduce

1. Read the round 2 REJECT of BG0950 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0950 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the return contract's semicolon rule is false inside a CLOSED bracket, and the record it yields is silently wrong. critic.py:2255 tells the reviewer that a `;` inside parentheses or brackets stays in its finding, but the repair ends the finding there whenever an origin tag follows, at any depth (critic.py:1164). Recorded through `critic.py record --from-verdict` with `BLOCKING: none`, `[new] round 1's first finding (an unclosed bracket; [regression] per its tag) is still open (critic.py:1160)` records as one new and one regression finding, so the blocking count goes from 1 to 2, and a pre-existing tag quoted the same way moves the rest of a new finding into a pre-existing one. Both are AC3 inputs, a tagged finding whose evidence holds a semicolon, that do not record as one finding in the reviewer's words. The behaviour is the base ref's, but the rule that invites the shape is new: the changelog's closing line, that the contract now states these rules (changelog.d/BG0950.md:20), is false for the tag rule, and its "even inside an unclosed bracket" (lines 12-13) implies a closed one holds. Keep the `;` when its bracket closes within the finding, or state the tag rule and its escape in the contract, and pin whichever ships [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: BLOCKING: [new] the repair's code-span carve-out is unpinned. Making a `;` with an origin tag after it end the finding inside a closed span too (the `not in_code` guard on the tag split, critic.py:1164) survives test\_verdict\_contract\_roundtrip.py, test\_critic.py and test\_lean\_file\_history.py, and under it a finding that quotes a prior finding in a code span, the shape a rejoinder verdict takes, records a phantom regression finding (2 findings become 3, blocking count 1 to 2). The only span test, test\_a\_code\_span\_and\_an\_escape\_keep\_their\_semicolons, quotes `a; b`, with no tag after its `;`
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** The round 2 REJECT finding no longer holds: [new] a code span opened by two backticks does not hold its `;`, though the contract now says a code span does. The scanner pairs single backtick characters (critic.py:1143-1144) where the ledger's own `_scan_ticks` pairs runs, so such a span is cut at its `;` and the tail refused as unclassified, as at the base ref. It fails closed and names the fragment, costing a re-emit rather than a wrong record (non-blocking)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC4** The round 2 REJECT finding no longer holds: [new] the guard that ignores a closer with no opener (critic.py:1161) is unpinned. Dropping it survives all three modules, and under it `[new] two defects: a) the gate skips (gate.py:40; also 52) and b) nothing warns` is refused, because the `a)` takes the depth below zero (non-blocking)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC5** The round 2 REJECT finding no longer holds: [regression] the brief's history section now quotes identifiers in code spans with the escape backslash for rows written before d309b239. reconcile.py:2099 reads a cell with `_unescape_outside_spans`, which leaves span interiors alone, where the base ref unescaped every backslash pair, so 22 of the 316 units with a REJECT row (BG0644 and US0671 among them) now show `test\_config` where the base showed the bare identifier. parse\_findings reads those legacy rows the same way, and the same change keeps genuine backslashes the base dropped (US0984's `\.local/`), so it is reported, not held. No test pins the reader's unescape: reading the cell raw survives all three modules (non-blocking)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC6** The round 2 REJECT finding no longer holds: [pre-existing] reconcile.blocking\_findings drops any finding whose text holds the literal pre-existing tag (reconcile.py:2101, a substring test since 293a36dd) instead of reading its origin, so a regression or new finding that quotes a pre-existing one never reaches a later brief's history. Now that a quoted finding is read whole, it drops round 1's first blocking finding from BG0950's own history. No open Bug or CR carries it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC7** BG0950 AC1 still passes: A block written exactly to `_RETURN_CONTRACT` - tagged ISSUES and an untagged BLOCKING subset of two or more items - records without edits, shown by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_contract_roundtrip.py -k contract_block_records
  - **Verified:** yes (2026-10-13)
- [ ] **AC8** BG0950 AC2 still passes: A blocking finding appears once in the recorded row, marked blocking
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_contract_roundtrip.py -k blocking_recorded_once
  - **Verified:** yes (2026-10-13)
- [ ] **AC9** BG0950 AC3 still passes: Given a tagged finding whose evidence contains a semicolon (`file.json:69; also in the parent commit`), when the verdict is recorded, then it is one finding, recorded with the reviewer's words unchanged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_contract_roundtrip.py -k semicolon_in_finding
  - **Verified:** yes (2026-10-13)

## Planning notes

- Joins RUN-01M4R168 by operator ruling (2026-10-13). Every finding is fixed here, the pre-existing one included: it is one condition in the same reader.
- Finding 1 takes the reviewer's second option: the contract states that a `;` followed by an origin tag ends a finding even inside brackets (not inside a code span), and that `\;` keeps one. Detecting a bracket that closes later was rejected because a bracket opened in one finding can be closed in another, which no scan can tell apart.
- Code spans are found with the ledger's own `_scan_ticks`, so a span opened by two backticks holds its `;` as a one-backtick span does.
- Redelivered, BG0950 reaches its terminal status on an APPROVE from the seat that rejected it (`qa seat (BG0950 r1)`).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | sdlc-studio | Filed |
| 2026-10-13 | Claude Opus 5.5 (planning) | Groomed: Points 2 -> 3; Affects adds the two changelog fragments and the history test module; design notes |
