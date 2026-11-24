# BG1589: A run closed to await the operator's signature is stamped 'closed running' on reviews/LATEST.md, because the anchor prints the raw outcome the record keeps until sign seals it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_awaiting_signature_status.py, changelog.d/BG1589.md
> **Evidence:** Close of RUN-01M7NTY5, 2026-11-18; sdlc-studio/reviews/LATEST.md close-status block.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T10:26:05Z

## Summary

Since D0503 (US1290) a closed run keeps outcome 'running' and no `ended_at` until `sprint sign` seals it. `anchor_status_block` in sprint.py prints that outcome verbatim, so the close of RUN-01M7NTY5 stamped '> **RUN-01M7NTY5 closed running.**' on the page every fresh session reads first. The owed-signature sentence beside it is right; the outcome word contradicts it and hides the goal verdict (partial) the close recorded.

## Steps to Reproduce

Close a run under the deferred-signature default (D0503) and read the close-status block of sdlc-studio/reviews/LATEST.md: it reads 'closed running'.

## Proposed Fix

Stamp an awaiting run as 'closed, awaiting signature' with the recorded goal verdict, and pin it with a test beside the signed case.

## Acceptance Criteria

- [ ] **AC1** Given a run closed under the deferred-signature default (outcome `running`, no signature, goal verdict partial), when `sprint close` stamps the anchor, then the block in `sdlc-studio/reviews/LATEST.md` reads `closed, awaiting signature` and carries the recorded goal verdict, and never the words `closed running`. Fails on: `anchor_status_block` prints the raw outcome, so the block reads `RUN-X closed running.` with no verdict.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_the_close_anchor_of_an_awaiting_run_says_awaiting_signature_and_the_verdict
- [ ] **AC2** Given the same run, when `sprint sign` seals it, then the block reads `closed <outcome>` with the sealed outcome (the signed case, the control beside AC1) and `closed, awaiting signature` is gone. Fails on: a fix that rewords the signed block too, or leaves the awaiting wording after the seal.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_the_sealed_anchor_says_the_sealed_outcome_not_awaiting
- [ ] **AC3** Given a `design` rung run (no Done sign-off owed), when the anchor is stamped, then it still carries no owed-signature wording and no `closed running`. Fails on: a fix that applies the awaiting wording to a rung that owes no signature.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_awaiting_signature_status.py::AwaitingSignatureStatusTests::test_a_design_rung_anchor_owes_no_signature_and_never_reads_running

## Impact

The anchor tells the next session a closed run is still running, in the one file it is ordered to read first.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-six: replaced the three restated-defect criteria with executable ones, one per anchor case (awaiting, sealed, non-done rung); Affects gains the awaiting-status test module; the fix passes the goal verdict to `anchor_status_block`, a new parameter |
