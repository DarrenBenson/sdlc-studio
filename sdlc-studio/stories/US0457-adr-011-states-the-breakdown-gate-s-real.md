# US0457: ADR-011 states the breakdown gate's real firing rule, and carries a dated amendment marker so a reader of the block sees it

> **Status:** Review
> **Delivers:** CR0429
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, tools/tests/test_adr011_agreement.py
> **Epic:** EP0168
> **Points:** 3

## User Story

**As an** engineer relying on the ADRs as the record of a deterministic fire/skip rule
**I want** ADR-011 to describe the gate `sprint plan` actually applies, marked as amended in the block itself
**So that** the ADR that ADR-006 makes load-bearing does not present a superseded unconditional rule as an unqualified Accepted decision

## Acceptance Criteria

### AC1: the exempt goal set in the ADR is derived from the gate

- **Given** sprint.GOALS ('triage', 'plan', 'design', 'done') and sprint._ungroomed_blocks_at (sprint.py:3862)
- **When** the guard calls _ungroomed_blocks_at for each goal and derives the set at which an ungroomed batch is accepted
- **Then** the extracted ADR-011 Decision names exactly that set as exempt and no other, so adding or removing an exemption in the code reddens the guard rather than leaving the ADR unchallenged
- **Verify:** pytest tools/tests/test_adr011_agreement.py::Adr011StatesTheFiringRule::test_the_exempt_goal_set_in_the_adr_is_derived_from_the_gate
- **Verified:** yes (2026-07-29)

### AC2: an unreadable goal blocks in both the gate and the ADR

- **Given** an args object with no goal attribute, an empty goal and a goal outside the ladder
- **When** the guard checks _ungroomed_blocks_at for each and reads what ADR-011 says about those cases
- **Then** the gate refuses in all three and the ADR says so, so the escape cannot be documented as opening when the rung cannot be read - the exact property the function's own docstring commits to
- **Verify:** pytest tools/tests/test_adr011_agreement.py::Adr011StatesTheFiringRule::test_an_unreadable_goal_blocks_in_both_the_gate_and_the_adr
- **Verified:** yes (2026-07-29)

### AC3: the ADR records the counterweight the close really emits

- **Given** sprint.grooming_report (sprint.py:3903) and sprint.render_grooming_report (sprint.py:3925), called directly over a fixture batch holding one groomed and one ungroomed story - no end-to-end close harness, because these are the pure functions the close calls
- **When** the guard renders the report and separately asserts that sprint._close_review_anchor invokes them on the design rung
- **Then** the rendered text states how many units the rung groomed and says so loudest when it groomed none, ADR-011's Consequences name that close-side report as the counterweight, and removing the call from the close reddens the guard
- **Verify:** pytest tools/tests/test_adr011_agreement.py::Adr011StatesTheFiringRule::test_the_rendered_grooming_report_is_the_counterweight_the_adr_names
- **Verified:** yes (2026-07-29)

### AC4: ADR-011's own block carries the dated amendment marker

- **Given** the ADR-011 block extracted by its heading and the next section boundary, currently carrying a bare `**Status:** Accepted` with no amendment line (trd.md:957-999)
- **When** the guard reads the Status line inside that extracted block
- **Then** it records the amendment and cites D0062 with a date, so a reader who opens ADR-011 sees the decision is qualified; an unmarked Accepted status fails, which is the state the guard exists to catch
- **Verify:** pytest tools/tests/test_adr011_agreement.py::Adr011AmendmentIsMarked::test_the_extracted_adr_block_carries_the_dated_d0062_amendment
- **Verified:** yes (2026-07-29)

### AC5: the Revision History row cites the decision and an absent D0062 fails loud

- **Given** the D0062 row in sdlc-studio/decisions.md with its recorded date of 2026-07-24
- **When** the guard resolves that row and then reads the TRD Revision History for the row covering this amendment
- **Then** the history row cites D0062 and carries a date no earlier than the decision's, and a decisions.md from which D0062 has been removed or renumbered fails naming the row it could not resolve rather than passing over it
- **Verify:** pytest tools/tests/test_adr011_agreement.py::Adr011AmendmentIsMarked::test_the_history_row_cites_d0062_and_a_missing_row_fails_loud
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
