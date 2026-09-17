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

### AC1: a non-terminal batch unit refuses the report, with every such unit named in one refusal

- **Given** a run otherwise ready to prepare - retro recorded, goal judged, reviews answered - whose batch holds two non-terminal units, a story at `Review` and a bug at `In Progress`, beside three terminal ones
- **When** `sprint.py close --retro RETRO0001 --principal "Darren Benson"` runs through `main`
- **Then** it exits 2; stderr names BOTH unit ids with their statuses in a single refusal; no file exists under `sdlc-studio/reports/`; and the run state carries no `report` field
- **Mutant:** return at the first non-terminal unit found - the operator clears it, pays the whole of PREPARE again and meets the second, and every assertion about the first unit's name still passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareRefusesTests::test_a_non_terminal_batch_unit_refuses_the_report

### AC2: an unanswered review refuses it, on the one predicate the rest of the close already reads

- **Given** a run whose batch is FULLY terminal - so nothing non-terminal can raise the hold - and one of whose units carries a standing REJECT that no repair record covers, making `sprint.unanswered_units` return that one id
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
