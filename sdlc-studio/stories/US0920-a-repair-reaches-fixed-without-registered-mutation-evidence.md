# US0920: The gate runs no evidence-drift lane and the close names no mutation-evidence mode

> **Status:** In Progress
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_off.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py, changelog.d/US0920.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, sdlc-studio/bugs/BG0651-a-later-commit-that-changes-a-target-file.md, sdlc-studio/bugs/BG0747-the-evidence-drift-lane-still-enforces-mutation-evidence.md, sdlc-studio/stories/US0660-a-surviving-mutant-becomes-a-severity-rated-bug.md, sdlc-studio/stories/US0822-a-ledger-row-records-the-anchor-it-was.md, sdlc-studio/stories/US0882-mutation-evidence-that-is-switched-off-stops-blocking.md
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer committing and closing units
**I want** no `evidence-drift` lane on the commit gate and no mutation-evidence mode stated or checked at the close
**So that** a commit is not refused over mutant rows in a ledger that 1,033 of 1,043 kills showed was not catching defects

## Acceptance Criteria

- **AC1:** Given a staged change that drifts a registered mutant row, when `gate.py` runs, then no `evidence-drift` lane runs or refuses, and the gate's lane list names none. Fails on: HEAD's `gate._evidence_drift`, which refuses the drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py::MutationGatesGoneTests::test_no_evidence_drift_lane
- **AC2:** Given a fixture config setting `review.mutation_evidence: blcok` (a typo), when `sprint.py close` runs, then the close neither refuses on the value nor names a mutation-evidence mode in its output, and `sprint.mutation_evidence_note` is gone. Fails on: HEAD, whose close refuses the unrecognised mode by name, and on keeping the note while dropping only its refusal
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py::MutationGatesGoneTests::test_the_close_names_no_mutation_evidence_mode
- **AC3:** Given the criteria whose stamped Verify selector names a test this story deletes (EvidenceDriftTests in `test_gate.py` and `test_lean_mutation_off.py`, and MutationEvidenceModeTests in `test_sprint.py`): BG0651 (2), US0660 (1), US0822 (1) and US0882 (3), then each is retired in the D0259 pattern (`Verify: manual - retired by US0920: <why>`, `Verified: manual (<date>) - retired, superseded by US0920`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_mutation_gates.py::MutationGatesGoneTests::test_no_stamp_names_a_deleted_test

## Notes

- Split from the original US0920 (5 points) as its "a" half: the old AC2 and the close-note part of the old AC4. The repair lane, its gate, survivor filing, the `review.mutation_evidence` key, the DoD tag and `mutation.evidence_mode` moved to US0935.
- AC2 removes an existing refusal (an unrecognised mode stops the close), so it retires a check rather than adding one.
- Lands before US0935, which deletes `mutation.evidence_mode` once this story has removed its last close-side reader.
- AGENTS.md's lane roster still names `evidence-drift` until US0926.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: split 5 -> 3 + 8 (US0935 takes the repair lane, gate, survivor filing, key, DoD tag and `evidence_mode`); retitled to the drift lane and close note; user story rewritten for this half; new AC2 for the close note; stamps measured (7 criteria); Affects narrowed to gate.py, sprint.py and their tests plus the changelog fragment |
