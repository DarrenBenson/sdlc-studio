# BG0700: The doctrine stop-ship guard passes inverted sentences and a second rule under the same anchor

> **Status:** Won't Fix
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/tests/test_doctrine_stop_ship.py, changelog.d/US0625.md
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/US0625-delivery-qa.txt (qa seat); verdicts/US0625-delivery-engineering.txt (engineering seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md. The unenforced 'never by the session that did the work' clause is CR0571's scope.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The AC1 and AC4 probes check only that keywords appear in one sentence, with no negation guard (AC2 has one): 'is never filed as its own bug or CR' (reference-doctrine.md:288) and 'The ruling is never made by the operator or a recorded delegate' (reference-doctrine.md:306) both pass every test (tools/tests/`test_doctrine_stop_ship.py`:47-52, 74-81). `stop_ship_passage` returns the first rule carrying the stop-ship anchor (lines 96-105), so a second rule with the same anchor naming the critic ledger as a store passes every probe (in memory, `store_problems` returned an empty list). changelog.d/US0625.md says the guard goes red 'if a second store is named', but 'Rulings are also written to the verdicts page.' passes, because `RECORDING_RE` knows only recorded, stored, kept, logged and lives in (lines 66-67), which is AC3's own defined shape. The in-memory controls are tied to exact doctrine phrases through `_replace_once` (lines 205-211, 237-238, 300, 314, 343), so a legitimate rewording fails with 'occurs 0 times' rather than a failed claim.

## Steps to Reproduce

1. In a copy, rewrite the doctrine sentence at reference-doctrine.md:288 as 'is never filed as its own bug or CR' and run tools/tests/`test_doctrine_stop_ship.py` - green. 2. Append a second rule carrying the stop-ship anchor that names the critic ledger as the store - green. 3. Add 'Rulings are also written to the verdicts page.' to the rule - green.

## Proposed Fix

Apply AC2's negation guard to the AC1 and AC4 probes; refuse more than one rule under the anchor; widen `RECORDING_RE` or narrow the changelog claim; anchor the controls on the rule's structure rather than on exact phrases.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The AC1 and AC4 probes check only that keywords appear in one sentence, with no negation guard (AC2 has one): 'is never filed as its own bug or CR'...
- [ ] **AC2** The proposed fix lands, pinned by a test: Apply AC2's negation guard to the AC1 and AC4 probes; refuse more than one rule under the anchor; widen `RECORDING_RE` or narrow the changelog claim; anchor...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - prose-keyword test of a doctrine rule D0257 rewrites |
