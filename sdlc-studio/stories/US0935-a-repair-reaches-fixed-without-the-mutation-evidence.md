# US0935: A repair reaches Fixed without the mutation-evidence gate, survivor filing or evidence mode

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/reference-doctrine.md, tools/tests/test_check_spec_claims.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_integrity.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_mutation_gate.py, changelog.d/US0935.md
> **Epic:** EP0263
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer closing a repair
**I want** a repair to reach Fixed on green criteria and its review, with no registered mutant demanded, no survivor bug auto-filed and no evidence mode to configure
**So that** a fix is judged by its tests and its reviewer: 1,033 of 1,043 mutants were killed, so the evidence obligation cost more than it found

## Acceptance Criteria

- **AC1:** Given a fixture config setting `review.mutation_evidence: block` and a repair bug with green criteria, an independent APPROVE, a `Verification depth` line (needed only until US0934 lands) and no registered mutant, when `transition.py set <id> Fixed` runs, then it succeeds; given `report` with a ledger holding a live survived row for the unit, then no survivor bug is filed; and the same bug with a red criterion is still refused, so the verify gate survives. Fails on: HEAD's `repair_mutation_gate`, which refuses the missing mutant, and on HEAD's survivor filing under `report`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_mutation_gate.py::RepairMutationGateGoneTests::test_a_repair_needs_no_mutation_evidence
- **AC2:** Given config-defaults.yaml, then it carries no `review.mutation_evidence`, no shipped script reads it and `mutation.evidence_mode` is gone; a Definition of Done line tagged `[check: repair.mutation-evidence]` is reported by `validate.py` as a retired tag naming `migrate`, through the retired-check-id registry US0916 built, never refused as an unknown id. Fails on: deleting the id from `DOR_DOD_CHECK_IDS` without adding it to the registry
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_mutation_gate.py::RepairMutationGateGoneTests::test_the_mutation_evidence_key_and_tag_are_retired
- **AC3:** Given the scripts tree, then `transition.py` defines none of `is_repair_unit`, `mutation_evidence_lane`, `_ledger_contradiction`, `repair_mutation_gate` or `_file_surviving_mutants`, and `reference-doctrine.md` rule 21 names no enforcing gate for mutation evidence. Fails on: unwiring the gate at `_pre_write_gates` but leaving the functions, which `test_lean_verdict_integrity.py` still mocks
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_mutation_gate.py::RepairMutationGateGoneTests::test_the_repair_lane_is_deleted
- **AC4:** Given the criteria whose stamped Verify selector names a test this story deletes (the survivor, repair-mutation-gate, repair-scope, mutation-evidence-lane, no-surface-exemption and measured-evidence classes in `test_transition.py`, `DoctrineTests` in `tools/tests/test_check_spec_claims.py` and `CrossProvenanceContradictionTests` in `test_mutation.py`): BG0541 (7), BG0655 (3), US0564 (3), US0565 (4), US0566 (4), US0567 (5), US0660 (4) and US0661 (4), then each is retired in the D0259 pattern (`Verify: manual - retired by US0935: <why>`, `Verified: manual (<date>) - retired, superseded by US0935`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_mutation_gate.py::RepairMutationGateGoneTests::test_no_stamp_names_a_deleted_test

## Notes

- Split from the original US0920 as its "b" half: the old AC1 (amended), AC3, AC4 and AC5. The old AC3 (a red criterion is still refused) passed at HEAD, so it is the control in AC1. The close-note clause of the old AC4 went to US0920 with `sprint.py`.
- Deletes, in `transition.py`: survivor filing (1776-2031), `is_repair_unit` (2496-2601; its last reader after US0913), `mutation_evidence_lane` and `_ledger_contradiction` (2602-2848), `repair_mutation_gate` (2849-2979) and the wiring at 1197-1215 and 1759-1768. Also `mutation.evidence_mode` (111-155).
- Engineering call: Affects adds `config-defaults.yaml` (AC2 reads it) and `test_transition.py` (it holds the deleted classes), and corrects the DoD template path to `templates/core/definition-of-done.md`.
- `test_lean_verdict_integrity.py` mocks `_file_surviving_mutants`; edit it, do not delete it.
- Lands after US0934, US0916 and US0920, and before US0936.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: the US0920b half (8 points); user story written; takes the old AC1 as amended (depth line, survivor under `report`) with the old AC3 as its control, the key and DoD tag, and the stamps; new AC3 for the deleted repair lane; stamps measured (34 criteria); Affects adds config-defaults.yaml, test_transition.py, the new module and the changelog fragment, and corrects the DoD template path |
