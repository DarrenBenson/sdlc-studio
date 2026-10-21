# US1062: retro.py seats scores each seat on its own verdicts and authored units from the ledger

> **Status:** Draft
> **Delivers:** CR0633
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-retro.md, .claude/skills/sdlc-studio/reference-scripts-create.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py, changelog.d/US1062.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1061, US1030, US1012
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose seats review and build every unit and never hear how their work held up
**I want** `retro.py seats --id RETROxxxx` to list, for each seat the batch's ledger rows name, its verdicts, the rounds its own units took, the defects a later round found on a unit it had approved, and its rows recorded in error, with the count of rows that name no seat
**So that** a seat's record is derived from the ledger, not from its own account, before it is asked what it will do differently

## Acceptance Criteria

- **AC1:** Given a retro whose Batch is US0001 and US0002, and ledger rows by `Sam Eriksson (qa) re-checking the product finding` (REJECT, then APPROVE, on US0001), `Lena Marsh (product)` (APPROVE on US0002) and `independent-critic` (APPROVE on US0002), when `retro.py seats --id RETRO0001` runs, then it lists qa with one REJECT, one APPROVE and US0001 converging in two rounds, product with one APPROVE, and says one of four verdict rows names no seat, naming independent-critic.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py::SeatEvidenceTests::test_each_seat_is_scored_on_the_rows_that_name_it
- **AC2:** Given US0001 approved in round 1 by `Lena Marsh (product)` and rejected in round 2 by `Sam Eriksson (qa)` with a blocking finding citing `scripts/a.py:12` that no round-1 finding cites, and US0002 rejected by qa in round 1 and again in round 2 with a new finding, when `retro.py seats` runs, then product's record lists the US0001 finding as found only after its approval, saying whether `scripts/a.py` changed between the two rows' dates or that it cannot be told, and qa is charged nothing for US0002's round-2 finding.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py::SeatEvidenceTests::test_only_an_earlier_approval_is_charged_with_a_later_rounds_defect
- **AC3:** Given a qa APPROVE later superseded with `critic.py supersede` as recorded against the wrong reviewer, when `retro.py seats` runs, then the row is left out of qa's verdicts and listed as recorded in error with the supersession's reason.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py::SeatEvidenceTests::test_a_superseded_row_is_recorded_in_error_not_overturned
- **AC4:** Given US0001 whose Author cell is `Dani Okafor (engineering)`, rejected twice and then approved, when `retro.py seats` runs, then engineering's record lists US0001 as a unit it built, converging in three rounds, with each round's blocking findings.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py::SeatEvidenceTests::test_an_authoring_seat_is_scored_on_the_rounds_its_units_took

## Notes

- Release: 6.3 (D0388; was 6.2) (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: rows attributed through `critic.seat_for`, which gives Sam's row to product (US1032 AC4's shape, probed), or unattributed rows dropped rather than counted
- AC2 must fail on: a later-round finding charged to every earlier verdict, the seat's own REJECT included, so a reviewer is blamed for a defect the author's repair introduced
- AC3 must fail on: a superseded row read as an overturned finding, or counted as a verdict that stood
- AC4 must fail on: the Author cell never read, so rounds to converge (D4) reach no seat and BG0993's case cannot be learned from
- Serves: Maya Okafor #3.
- Checked at HEAD: retro.py has no seats verb. 51 of 1,552 ledger rows carry a `(role)` or `(role seat)` group; `seat_for` (critic.py:2145) guesses 1,261 by first match, which US1032 records as misattributing. From US1030 and the author-seat story on, every briefed row names both seats.
- Attribution: `critic.recorded_seat` on the Reviewer and Author cells. Rows naming no seat are counted and named, never guessed (LL0009); the close shows the count.
- Later-round defect: a blocking finding of round k whose `file:line` evidence no earlier round's finding on the unit cites, charged only to a seat whose earlier verdict on the unit was an APPROVE. Whether the cited file changed is read with `git log` between the two rows' dates; rows sharing a day read 'cannot be told'.
- Superseded rows: all 11 in this ledger retire APPROVEs recorded against the wrong reviewer; none overturns a finding on its merits. 'Overturned' comes from an operator ruling naming the unit and the seat (the source story), which today holds none: no seat ruling (37) has been superseded.
- Each adverse item carries a key the approve story cites (`round:<unit>r<k>`, `bug:<id>`, `ruling:<Dnnnn>`). Rounds as the ledger numbers them; per-seat lanes are US1032 (later).
- Read-only; `--format json` is the record the learning brief embeds. Provenance per verdict moved to the source story (panel's re-size).

## Triage (2026-10-21)

Kept (D0387). To plan it:

- The D0374 stakeholder consult for EP0287 is owed before build
- Blocked on US1061, US1030 and US1012 (Draft)
- The 'Release: 6.2' note is stale under D0382

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
