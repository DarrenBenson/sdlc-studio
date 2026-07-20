# US0042: retro hard close-gate: sprint close fails loud without a batch retro (CR0129)

> **Status:** Done
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Epic:** EP0010
> **Persona:** Dani (Engineering)
> **Depends on:** -

## User Story

**As** the operator
**I want** the sprint close to fail loud when no batch retro exists
**So that** the learning loop cannot be silently skipped

## Context

### Persona Reference

**Dani (Engineering)** - the engineering amigo, owner of the deterministic
tooling and the mechanical gates that keep a sprint honest. Dani cares that a
close path cannot report success it did not earn.
[Full persona details](../personas.md#dani-engineering)

### Background

This story implements part of CR0129. `reference-sprint.md` step 7 calls the
closing retro "unconditional", but that is doctrine in prose, not a mechanical
gate, so it has been skipped on real projects: consuming repos have run sprints
with no `retros/` directory at all. Prose the agent is asked to honour is not a
gate; a gate refuses to pass.

This story turns the closing retro into a real gate, mirroring the existing
reconcile-drift-0 gate. That gate is the LL0008 discipline - a tool must not
report success it did not achieve - applied to the closing step itself. The
sprint, autosprint, and review close paths must refuse to report success until
`retros/RETRO{next}.md` exists for the batch.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type        | Constraint                                                                     | AC Implication                                   |
| ------ | ----------- | ------------------------------------------------------------------------------ | ------------------------------------------------ |
| Epic   | Determinism | Gates must be script-backed and testable, not prose the agent honours (LL0008) | The gate is exercised by unit tests, AC1 and AC2 |
| PRD    | Performance | Not applicable - skill-internal change                                         | None                                             |
| PRD    | Security    | Not applicable - skill-internal change                                         | None                                             |

---

## Acceptance Criteria

### AC1: close fails loud when the batch retro is absent

- **Given** a closing sprint, autosprint, or review batch whose `retros/RETRO{next}.md` does not exist
- **When** the close path runs
- **Then** it returns a non-zero exit and writes no success report
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RetroCloseGateTests::test_close_gate_requires_retro
- **Verification target:** functional
- **Verified:** yes (2026-06-27)

### AC2: close passes when the batch retro is present

- **Given** a closing batch whose `retros/RETRO{next}.md` exists
- **When** the close path runs
- **Then** the gate passes and the close proceeds, mirroring the reconcile-drift-0 gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RetroCloseGateTests::test_close_gate_passes_with_retro
- **Verification target:** functional
- **Verified:** no (2026-07-20)

> **Verification target tiers:** `functional` (single round-trip – default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- The close gate only: the sprint/autosprint/review close path refuses to report success unless the batch retro exists.

### Out of Scope

- The lessons re-validation verb (US0043).
- The rolling Summary of Learnings generator (US0044).

---

## Technical Notes

The gate lives on the sprint close path. Add a small gate helper under
`.claude/skills/sdlc-studio/scripts/` that resolves the batch's expected
`retros/RETRO{next}.md` path, checks for its presence, and returns a non-zero
exit with no success output when it is missing. Wire the close path to call it,
alongside the existing reconcile-drift-0 gate, so the two gates read the same
way. Update `reference-sprint.md` step 7 so the close gate is described as a
mechanical gate, not unconditional prose.

The `{next}` batch index is resolved the same way the rest of the retro path
resolves it, so the gate and the retro writer agree on the path.

### API Contracts

Not applicable - skill-internal change, no external API.

### Data Requirements

Reads the filesystem only: the existence of `retros/RETRO{next}.md` under the
batch root. No new persisted state.

---

## Edge Cases & Error Handling

| Scenario                                                 | Expected Behaviour                                                          |
| -------------------------------------------------------- | --------------------------------------------------------------------------- |
| `retros/` directory does not exist at all                | Treated as retro absent: close fails loud, non-zero, no success report      |
| `retros/RETRO{next}.md` exists but is empty (zero bytes) | Treated as present: presence is the gate, content review is the agent's job |

> **Minimum edge cases:** 2 for API stories, 2 for others

---

## Test Scenarios

- [ ] `test_close_gate_requires_retro`: with no batch retro file, the close path returns non-zero and emits no success report.
- [ ] `test_close_gate_passes_with_retro`: with the batch retro file present, the gate passes and the close proceeds.

> **Minimum test scenarios:** 2 for API stories, 2 for UI

---

## Dependencies

### Story Dependencies

None.

### External Dependencies

None.

---

## Estimation

**Story Points:** 3
**Complexity:** Medium

---

## Rollback Envelope

> Required when `affects_production_runtime: true`; optional otherwise. See `reference-story.md#rollback-envelope`.

**Affects production runtime:** false

*Not applicable - story does not change runtime behaviour.*

---

## Open Questions

None.

---

## Revision History

| Date       | Author | Change                                               |
| ---------- | ------ | ---------------------------------------------------- |
| 2026-06-27 | Dani   | Authored to Ready (design rung, breakdown of CR0129) |
