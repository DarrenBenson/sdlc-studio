# US0627: closing a story over a recorded REJECT requires a filed artefact id or an explicit stop-ship ruling

> **Status:** Ready
> **Delivers:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0206
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reviewer of record
**I want** a story carrying a recorded REJECT to refuse Done unless a filed artefact id or an explicit stop-ship ruling is given
**So that** a rejection is answered on the record rather than outlived by the unit that earned it

## Acceptance Criteria

### AC1: a recorded REJECT blocks Done on its own

- **Given** a story with a recorded REJECT verdict and no answer to it
- **When** `transition.py set --status Done` runs
- **Then** it is refused and the refusal names the REJECT - a verdict the unit outlived is one nothing acted on
- **Mutant:** ignore the REJECT once any later APPROVE exists - the rejection is cancelled by a verdict that never addressed it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_recorded_reject_blocks_done

### AC2: a filed artefact id discharges it

- **Given** the same story, with the REJECT's findings filed as a Bug or CR and its id recorded
- **When** the same transition runs
- **Then** it proceeds - the finding survives as its own tracked artefact, which is the point of filing
- **Mutant:** accept any non-empty string as the id - a discharge nobody can follow is not one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_filed_artefact_id_discharges_the_reject

### AC3: an explicit stop-ship ruling discharges it too

- **Given** the same story with a recorded stop-ship ruling instead of a filed id
- **When** the same transition runs
- **Then** it proceeds - a judgement made on the record is an answer, and refusing it would force a bug to be filed for a decision somebody already took
- **Mutant:** require the filed id and nothing else - a legitimate ruling has no route and gets worked around
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_stop_ship_ruling_discharges_the_reject

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
