# US0920: A repair reaches Fixed without registered mutation evidence

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_off.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer committing and closing a fix
**I want** a repair to close on green criteria and its review, with no mutant registration, survivor auto-filing or evidence-drift lane
**So that** 1,033 of 1,043 mutants were killed; the evidence obligation cost more than it found and stops blocking fixes and commits

## Acceptance Criteria

- **AC1:** Given a fixture config setting `review.mutation_evidence: block` and a repair bug with green criteria, an independent APPROVE and no registered mutant, when `transition.py set <id> Fixed` runs, then it succeeds and no survivor bug is filed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py::MutationGatesGoneTests::test_a_repair_needs_no_mutation_evidence
- **AC2:** Given a staged change that drifts a registered mutant row, when `gate.py` runs, then no `evidence-drift` lane runs or refuses, and the gate's lane list names none
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py::MutationGatesGoneTests::test_no_evidence_drift_lane
- **AC3:** Given the same repair bug with a red criterion, when it is moved to Fixed, then it is still refused, so the verify gate survives
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py::MutationGatesGoneTests::test_fixed_still_needs_green_criteria
- **AC4:** Given config-defaults.yaml, then it carries no `review.mutation_evidence`, no shipped script reads it and the close names no mutation-evidence mode; a Definition of Done line tagged `[check: repair.mutation-evidence]` is reported as a retired tag naming `migrate`, never refused as an unknown id
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py::MutationGatesGoneTests::test_the_mutation_evidence_key_and_tag_are_retired
- **AC5:** Given every criterion whose stamped Verify selector names a test this story deletes (the survivor, repair-mutation-gate, repair-scope, mutation-evidence-lane and measured-evidence classes in `test_transition.py`, EvidenceDriftTests in `test_gate.py` and the evidence-drift tests in `test_lean_mutation_off.py`; at least those on BG0541, BG0651, BG0655, US0564, US0565, US0566, US0660, US0661, US0822, US0882), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py::MutationGatesGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
