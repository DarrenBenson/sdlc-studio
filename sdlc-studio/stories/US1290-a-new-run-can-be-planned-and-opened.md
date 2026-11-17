# US1290: A new run can be planned and opened while a closed run awaits signature, and status names each one waiting

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0729
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_awaiting_signature_status.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py
> **Epic:** EP0366
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A new run can be planned and opened while a closed run awaits signature, and status names each one waiting
**So that** CR0729 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A fresh checkout can plan and open a run over one awaiting signature

- **Given** a run closed and its tracked record committed, unsigned, and a fresh clone holding that record
- **When** `sprint.py plan --write` runs in the clone over a batch sharing no unit with the waiting run
- **Then** it exits 0, a new run with its own run id is open in the clone, the waiting run's tracked record is byte-identical, and the plan names the run and report still awaiting a signature. Fails on: the refusal the plan gives today ('a project holds one run at a time'), or a plan that opens the new run by discarding or sealing the waiting record
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py::RunOpenAcrossCheckoutsTests::test_plan_opens_a_run_over_an_unsigned_committed_run

### AC2: The checkout that closed the run can open the next

- **Given** the checkout that closed a run, its report filed and not yet signed
- **When** `sprint.py plan --write` runs there over a disjoint batch
- **Then** it exits 0 and opens a new run, the closed run stays awaiting its signature in its tracked record, and a run that is open and not yet closed still refuses a disjoint batch as it does today. Fails on: the '<run> is already open' refusal for a closed run, or the one-run guard lost for a run that was never closed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py::RunOpenAcrossCheckoutsTests::test_the_closing_checkout_opens_the_next_run_and_an_unclosed_run_still_refuses

### AC3: A waiting run is still signed while a later run is open

- **Given** a checkout holding a later run open, with an earlier closed run awaiting its signature
- **When** `sprint.py sign --report <the earlier report> --principal <operator>` runs there
- **Then** the earlier run is sealed with its signature in its tracked record, and the later run is still open with its run id, batch and start time unchanged. Fails on: the 'cannot be taken up here without discarding it' refusal sign gives today, which would leave a waiting run unsignable for as long as delivery continues, or a sign that replaces the open run's live state
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py::RunOpenAcrossCheckoutsTests::test_sign_seals_a_waiting_run_without_disturbing_the_open_one

### AC4: Status names every run awaiting signature

- **Given** a project with two closed runs awaiting signature and a third run open, and a second project with none waiting
- **When** `status.py` runs in each
- **Then** the first names both waiting runs, each with its run id and report id, apart from the open run, and the second prints no awaiting-signature line. Fails on: status naming only the most recent waiting run, or counting the open run as waiting
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_awaiting_signature_status.py::AwaitingSignatureStatusTests::test_status_names_every_run_awaiting_signature

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
