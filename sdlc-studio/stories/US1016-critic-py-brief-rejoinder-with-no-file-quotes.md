# US1016: critic.py brief --rejoinder with no file quotes the seat's standing REJECT from the ledger

> **Status:** Draft
> **Delivers:** CR0615
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-review.md, changelog.d/US1016.md
> **Epic:** EP0280
> **Points:** 3
> **Depends on:** US1012, BG0950
> **Persona:** Maya Okafor

## User Story

**As** the operator taking a rejected unit into its second review round
**I want** `critic.py brief --rejoinder` with no file to quote the briefed seat's standing REJECT from the verdict ledger
**So that** round 2 re-checks the findings as the reviewer recorded them, not a copy somebody saved by hand and paraphrased

## Acceptance Criteria

- **AC1:** Given a round-1 REJECT recorded from an issued file, when `critic.py brief --unit US0001 --seat qa --rejoinder` runs with no value, then the brief quotes that file's bytes verbatim beneath the RE-REVIEW mark, found through the row's `Source` cell, and its fingerprint equals the one `--rejoinder <that file>` prints.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_the_ledger_rejoinder_quotes_the_issued_file_verbatim
- **AC2:** Given a REJECT recorded by `--verdict` and `--issues` with no file, when the ledger rejoinder is printed, then it rebuilds VERDICT, ISSUES and BLOCKING from the row's cells with every finding as recorded, and labels the quotation as rebuilt from the ledger's fields.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_a_transcribed_reject_is_rebuilt_from_its_cells_and_labelled
- **AC3:** Given no unanswered REJECT in the unit's current delivery from a reviewer of the briefed seat (none recorded, or every one answered by that reviewer's APPROVE), when `brief --rejoinder` runs with no file, then it exits 2, names the unit and the seat, and prints nothing on stdout.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_no_unanswered_reject_for_the_seat_is_refused

## Notes

- Release: 6.2 (D0355 breakdown G6, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: quoting the row's issues cell instead of the stored file, or fingerprinting the quoted prior verdict as well as the base brief
- AC2 must fail on: dropping the BLOCKING findings the row carries in its issues cell, or presenting the rebuild as the reviewer's own words
- AC3 must fail on: choosing with `standing_rejects`, which returns the latest REJECT even when every one is answered (critic.py:819); falling back to another seat's REJECT; or reading rows from an earlier delivery
- Checked at HEAD: `--rejoinder ledger` refuses with 'No such file or directory: ledger', and a bare `--rejoinder` is an argparse error. `cmd_brief` (critic.py:3095) reads a file or stdin only.
- `--rejoinder` becomes `nargs='?'` with the ledger as its constant, and `ledger` is accepted as a spelling. A file argument and `-` keep working, as the existing rejoinder tests in test_critic.py pin, so CR0615 AC3 needs no new test.
- The REJECT is chosen with `_unanswered_rejects` over `delivery_rounds` (the unit's current delivery), filtered to reviewers that `seat_for` maps to the briefed seat. With no declared seats and exactly one candidate, that one is used; with several, the brief refuses and names them. This stays right under G10's per-seat rounds.
- A plain `brief` for a seat holding an unanswered REJECT prints a notice naming `--rejoinder` (panel, Q7). `rebrief_notice` and the rejoinder footer print the bare `--rejoinder` (critic.py:2519).
- BG0950 changes how a BLOCKING finding is recorded (once, as a flag on its ISSUES entry), so the rebuild reads whatever BG0950 writes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G6 after the refine panel's review |
