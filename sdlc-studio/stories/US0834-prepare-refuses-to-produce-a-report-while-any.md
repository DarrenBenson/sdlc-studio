# US0834: PREPARE refuses to produce a report while any batch unit is non-terminal, any review unanswered or any index drifted

> **Status:** Draft
> **Delivers:** RFC0059
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0255
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** PREPARE refuses to produce a report while any batch unit is non-terminal, any review unanswered or any index drifted
**So that** RFC0059 is delivered by work that can be planned and checked

## Acceptance Criteria

Three holds, and what separates them from `close_preflight`'s blockers is that they REFUSE the
report rather than being filed and deferred: `--file-and-close` exists so a run can end honestly
with work outstanding, and a report is exactly the artefact that must not. A report produced
over a non-terminal unit, a live REJECT or an index that disagrees with the tree is a document
whose facts expire before the signature dries. Each hold names every failure at once, because
serial discovery - clear one, re-run the whole of PREPARE, meet the next - is what
`_report_preflight` was built to end. The unanswered-review hold reads US0823's
`sprint.unanswered_units(root, state)` and nothing else, so this story adds no second opinion
about what an unanswered review is (D0193, D0194).

### AC0: PREPARE's bar is the gate, not the status, and a gate-clear run at Review still produces its report

- **Given** a run whose every batch unit is at `Review` or `In Progress` with its terminal gate CLEAR - reviews answered, criteria passed, coverage ruled - which is the state D0213 leaves, since the fan-out belongs to SEAL
- **When** `sprint.py close --retro RETRO0001` runs through `main`
- **Then** it exits 0 and produces the report; no unit has moved; and the report records each unit as having cleared its terminal gate rather than as Done
- **Mutant:** keep the old status test - `Status == Done or Fixed` - and PREPARE refuses the exact state its own split creates, so the split can never produce a report at all
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareRefusesTests::test_a_gate_clear_run_still_at_review_produces_its_report

### AC1: a batch unit whose terminal GATE is unmet refuses the report, with every such unit named in one refusal

- **Given** a run otherwise ready to prepare - retro recorded, goal judged, reviews answered - whose batch holds two units whose terminal gate is UNMET - a story missing a review half and a bug at `In Progress`, beside three terminal ones
- **When** `sprint.py close --retro RETRO0001 --principal "Darren Benson"` runs through `main`
- **Then** it exits 2; stderr names BOTH unit ids with their statuses in a single refusal - the statuses named are the GATE's verdict, not the unit's Status line, because under D0213 no unit is terminal until SEAL; no file exists under `sdlc-studio/reports/`; and the run state carries no `report` field
- **Mutant:** return at the first non-terminal unit found - the operator clears it, pays the whole of PREPARE again and meets the second, and every assertion about the first unit's name still passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareRefusesTests::test_a_non_terminal_batch_unit_refuses_the_report

### AC2: an unanswered review refuses it, on the one predicate the rest of the close already reads

- **Given** a run every one of whose units has a CLEAR terminal gate - so nothing non-terminal can raise the hold - and one of whose units carries a standing REJECT that no repair record covers, making `sprint.unanswered_units` return that one id
- **When** PREPARE runs as in AC1
- **Then** it exits 2, the refusal's unit ids equal the predicate's set compared against the literal, and no report is written; the message names the REJECT's verdict row so the reader knows which review is owed
- **Mutant:** derive the hold from the batch's non-terminal units, as AC1's does - every unit here is terminal, so the hold never fires and a run with a live REJECT produces a signable report, which is the state D0193 was written against
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareRefusesTests::test_an_unanswered_review_refuses_the_report

### AC3: index drift refuses it, and a clean run produces exactly one report - the paired control

- **Given** two fresh copies of a terminal, answered run: in the first an `_index.md` row edited so `reconcile detect` reports drift, the second untouched
- **When** PREPARE runs on each
- **Then** the drifted copy exits 2, names the drifted index path, and writes no report; the clean copy exits 0, writes exactly one report JSON under `sdlc-studio/reports/`, and its stdout names all three holds as passed, each by its own name, rather than passing them in silence
- **Mutant:** register the drift as a deferrable close blocker, so `--file-and-close` files it as a CR and continues - the report then ships describing an index that disagrees with the tree it was derived from, with a filed ticket standing in for the fact being right
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareRefusesTests::test_index_drift_refuses_the_report_and_a_clean_run_produces_one

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-17 | grooming 2026-09-17 | Groomed: three criteria, one per hold. Each names every failure at once rather than the first; the unanswered-review hold reads US0823's `unanswered_units` and nothing else, over a FULLY terminal batch so no other reader could raise it. |
| 2026-09-18 | goal review round 2 | AC0 added and AC1 restated: under D0213 the fan-out belongs to SEAL, so PREPARE's bar is each unit's terminal GATE, never its Status. As written, AC1-AC3 refused the exact state PREPARE creates, so no report could ever have been produced. |
