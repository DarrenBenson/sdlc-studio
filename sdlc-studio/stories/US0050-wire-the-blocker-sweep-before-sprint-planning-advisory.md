# US0050: wire the blocker sweep before sprint planning + advisory reconcile lane (CR0130)

> **Status:** Done
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Epic:** EP0010
> **Persona:** Dani (Engineering)
> **Depends on:** US0049

## User Story

**As** the operator
**I want** the blocker sweep run before sprint planning and available as a reconcile lane
**So that** newly-unblocked work enters the batch and stale-blocked units surface in routine drift checks

## Context

### Persona Reference

**Dani (Engineering)** - the engineering amigo, owns implementation quality and the deterministic, fail-loud tooling the skill ships and dogfoods.
[Full persona details](../personas.md#dani-engineering)

### Background

This story implements the wiring half of CR0130, consuming the detection engine
delivered in US0049. US0049 builds the sweep that collects every unit carrying a
blocker signal (Status `Blocked`, a `Depends on:` referent, or an epic `Blocked By`
row), resolves each referent's current status (in-repo by the file census, cross-repo
through the PVD manifest), and reports the units now fully unblocked as `Blocked ->
Ready` candidates. Detection alone is inert until it runs at the right moments.

This story adds those two moments. First, the sweep runs as a pre-`plan` step so
newly-unblocked units are eligible for the next batch, mirroring the existing
reconcile-before-plan gate: planning should never overlook work whose blocker has just
cleared. Second, the sweep is exposed as an advisory reconcile lane, so routine drift
checks report stale-blocked units (those still sitting at `Blocked` long after their
referent reached a terminal state).

Per the determinism directive and LL0008, the sweep only proposes. The `Blocked ->
Ready` transition stays the gated `transition` call - the operator or loop makes the
state change, never the sweep. The advisory lane reports; it never blocks the reconcile
result.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type        | Constraint                                                                      | AC Implication                                                         |
| ------ | ----------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Epic   | Tech Stack  | Deterministic tooling that fails loud; script changes carry unit tests (LL0008) | The wiring is script-backed and stable across runs; each AC has a test |
| PRD    | Performance | Not applicable - skill-internal change                                          | None                                                                   |
| PRD    | Security    | Not applicable - skill-internal change                                          | None                                                                   |

---

## Acceptance Criteria

### AC1: The blocker sweep runs before sprint planning

- **Given** a backlog where a unit became unblocked after its referent reached a terminal state
- **When** sprint planning runs, the sweep fires as a pre-`plan` step before the batch is selected
- **Then** the newly-unblocked unit is surfaced and eligible for the batch, the same way the reconcile-before-plan gate runs ahead of planning
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_blocker_sweep.py::WiringTests::test_blocker_sweep_runs_before_plan
- **Verification target:** functional
- **Verified:** yes (2026-06-27)

### AC2: The sweep is available as an advisory reconcile lane

- **Given** a backlog containing units still at `Blocked` after their referent has cleared
- **When** reconcile runs with the blocker-sweep lane enabled
- **Then** the lane reports those stale-blocked units as advisory output and never blocks the reconcile result (reconcile still succeeds or fails on its own checks)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_blocker_sweep.py::WiringTests::test_blocker_sweep_reconcile_lane
- **Verification target:** functional
- **Verified:** yes (2026-06-27)

### AC3: The sweep proposes but never auto-transitions

- **Given** a unit whose every blocker is terminal/delivered
- **When** the sweep reports it as a `Blocked -> Ready` candidate
- **Then** the unit's status is unchanged on disk; the sweep proposes the candidate only, and the gated `transition` call stays the sole actor that moves state
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_blocker_sweep.py::WiringTests::test_blocker_sweep_no_auto_transition
- **Verification target:** functional
- **Verified:** yes (2026-06-27)

> **Verification target tiers:** `functional` (single round-trip - default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- The wiring only: a pre-`plan` hook in `sprint.py` that runs the US0049 detection engine before the batch is selected and surfaces newly-unblocked units, and an advisory lane in `reconcile.py` that reports stale-blocked units without affecting the reconcile result. Documentation updates to `reference-sprint.md` (pre-plan step) and `reference-reconcile.md` (advisory lane), plus the CHANGELOG `[Unreleased]` entry.

### Out of Scope

- The detection engine itself - referent collection, in-repo census resolution, and cross-repo resolution through the PVD manifest - which is US0049.
- Auto-transitioning `Blocked -> Ready`; that stays the gated `transition` call.

---

## Technical Notes

The change touches `.claude/skills/sdlc-studio/scripts/sprint.py` (a pre-`plan` hook
that invokes the US0049 sweep before batch selection, mirroring the existing
reconcile-before-plan gate) and `.claude/skills/sdlc-studio/scripts/reconcile.py` (an
advisory lane that calls the same sweep and folds its report into reconcile output
without changing the reconcile exit status). Both call the detection engine from US0049
rather than re-implementing detection. Docs land in `reference-sprint.md` and
`reference-reconcile.md` in the same change. The lane must be advisory: its findings are
reported, but a non-empty stale-blocked list never flips reconcile to a failure. The
sweep proposes candidates only - no path in either site calls `transition` or writes a
status. Add the CHANGELOG `[Unreleased]` entry in the same commit (LL0004).

### API Contracts

Not applicable - skill-internal wiring with no external API surface.

### Data Requirements

Not applicable - no production data is read or written.

---

## Edge Cases & Error Handling

| Scenario                                                                              | Expected Behaviour                                                                                                                                       |
| ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The pre-`plan` sweep finds no newly-unblocked units                                   | Planning proceeds normally with no added candidates; the hook is silent rather than emitting noise or blocking the batch                                 |
| The reconcile lane finds stale-blocked units                                          | The units are reported as advisory output and reconcile still returns its own pass/fail result; the lane never changes the reconcile exit status         |
| The sweep reports a `Blocked -> Ready` candidate during either run                    | The candidate is listed only; no status is written and `transition` is not called, so the unit stays `Blocked` until the operator or loop transitions it |
| The underlying US0049 detection engine reports a referent as unresolved or unreadable | The wiring surfaces that as still-blocked (never as a cleared candidate), preserving the fail-loud, never-false-clear contract                           |

---

## Test Scenarios

- [ ] Run sprint planning against a backlog with one newly-unblocked unit and confirm the pre-`plan` sweep fires before batch selection and the unit is eligible for the batch (`test_blocker_sweep_runs_before_plan`).
- [ ] Run reconcile with the blocker-sweep lane against a backlog with stale-blocked units and confirm the lane reports them advisorily while reconcile returns its own unaffected result (`test_blocker_sweep_reconcile_lane`).
- [ ] Run the sweep over a fully-unblocked unit and confirm it is reported as a candidate while its on-disk status stays `Blocked` and no `transition` is invoked (`test_blocker_sweep_no_auto_transition`).

---

## Dependencies

### Story Dependencies

| Story                                                                   | Type     | What's Needed                                                                  | Status |
| ----------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------ | ------ |
| [US0049](US0049-blocker-sweep-detection-now-unblocked-units-in-repo.md) | blocking | The detection engine: referent collection, status resolution, candidate report | Ready  |

### External Dependencies

| Dependency | Type | Status |
| ---------- | ---- | ------ |
| None       | -    | -      |

---

## Estimation

**Story Points:** 2
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
| 2026-06-27 | Dani   | Authored to Ready (design rung, breakdown of CR0130) |
