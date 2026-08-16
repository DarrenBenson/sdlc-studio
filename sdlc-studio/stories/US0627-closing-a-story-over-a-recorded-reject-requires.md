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
- **Mutant:** stop reading recorded REJECT verdicts at all - the guard has nothing to refuse on, which is the change this criterion's own Given (a REJECT with NO answer) can actually reach
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_recorded_reject_blocks_done

### AC2: a filed artefact id discharges it

- **Given** the same story, with the REJECT's findings filed as a Bug or CR and its id recorded
- **When** the same transition runs
- **Then** it proceeds - the finding survives as its own tracked artefact, which is the point of filing
- **Mutant:** refuse every id, valid or not - the positive path this criterion asserts stops working, which is a change it can reach
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_filed_artefact_id_discharges_the_reject

### AC3: an explicit stop-ship ruling discharges it too

- **Given** the same story with a recorded stop-ship ruling instead of a filed id
- **When** the same transition runs
- **Then** it proceeds - a judgement made on the record is an answer, and refusing it would force a bug to be filed for a decision somebody already took
- **Mutant:** require the filed id and nothing else - a legitimate ruling has no route and gets worked around
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_stop_ship_ruling_discharges_the_reject

### AC4: an id that resolves to no artefact is refused

- **Given** a story whose REJECT is answered with an id naming no artefact that exists
- **When** the transition runs
- **Then** it is REFUSED - a discharge nobody can follow is not one, and without this criterion an implementation accepting the string "x" satisfies every other criterion in this batch
- **Mutant:** accept any non-empty string as the id - the negative case this criterion exists for stops being refused
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_an_id_naming_no_artefact_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
