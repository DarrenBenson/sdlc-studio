# US1063: The seat record reads each verdict's source and the operator rulings that name the seat

> **Status:** Draft
> **Delivers:** CR0633
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-retro.md, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_rulings.py, changelog.d/US1063.md
> **Epic:** EP0287
> **Points:** 3
> **Depends on:** US1062, US1012
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, who rules on escalations and authorises rounds past the cap
**I want** the seat record to say where each verdict came from (the reviewer's issued file or a transcription) and to list the operator decisions that name the seat or authorised a round on its review
**So that** a seat's record holds the rulings that followed its verdicts and says which verdicts are the reviewer's own words

## Acceptance Criteria

- **AC1:** Given decisions dated within the run, one whose rationale names the QA seat and US0001 (which qa rejected), one reading 'the product is designed for', and a `ruling: x [seat: qa]` row, when `retro.py seats --id RETRO0002` runs, then qa's record lists the first against its US0001 REJECT and product's lists nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_rulings.py::SeatRulingTests::test_an_operator_decision_naming_the_seat_is_listed_against_its_verdict
- **AC2:** Given one qa row whose Source cell names an issued verdict file and one whose Source is `-`, when `retro.py seats --format json` runs, then each verdict carries its provenance, and the first's findings are read from the file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_rulings.py::SeatRulingTests::test_each_verdict_carries_its_provenance
- **AC3:** Given a qa row whose Source cell carries `authorised:D0001`, when `retro.py seats` runs, then qa's record lists D0001 as an operator ruling on that review.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_rulings.py::SeatRulingTests::test_a_decision_authorising_a_round_is_listed

## Notes

- Release: 6.3 (D0388; was 6.2) (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the bare role word matched (43 decisions here name 'product' in passing), or the seat's own `ruling:` rows counted as operator rulings about it
- AC2 must fail on: provenance dropped, or findings read from the folded ledger cell when the reviewer's own file exists
- AC3 must fail on: Source tokens other than the hash ignored, so a round the operator authorised past the cap leaves no trace on the seat
- Serves: Maya Okafor #3.
- A decision names a seat by `<role> seat`, `(<role>)` or its card holder's full name, never the bare role word (panel: 43 decisions match bare 'product' against 31 for the seat phrase or holder name). The draft's '26 of 363' used first names and is withdrawn. Seat `ruling:` rows (decisions.py:437 grammar) are the seat's own and excluded.
- A decision naming a unit the seat rejected is listed against that REJECT, which is where an overturn would show; the persona and its approver judge it.
- Source grammar is US1012's (`sha256:<16 hex> <basename>`, `-` transcribed) with BG1003's `authorised:<Dnnnn>` token.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- The D0374 stakeholder consult for EP0287 is owed before build
- Blocked on US1062 and US1012 (Draft)
- The 'Release: 6.2' note is stale under D0382

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
