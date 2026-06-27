# US0049: blocker-sweep detection: now-unblocked units, in-repo census + cross-repo via PVD manifest (CR0130)

> **Status:** Ready
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Epic:** EP0010
> **Persona:** Dani (Engineering)
> **Depends on:** -

## User Story

**As** the operator
**I want** a blocker sweep that finds units whose blockers have cleared - in this repo and across repos in a PVD setup
**So that** freshly-unblocked work is surfaced instead of sitting stale

## Context

### Persona Reference

**Dani (Engineering)** - the engineering amigo, owner of the deterministic
tooling and the mechanical gates that keep a sprint honest. Dani cares that the
backlog tells the truth: a blocker that has cleared should be detected by a
script, not by the operator remembering the link.
[Full persona details](../personas.md#dani-engineering)

### Background

This story implements the detection half of CR0130. The skill tracks what is
blocked but never re-checks whether a blocker has cleared. `audit.py` already
flags `unmet-deps` (a `Depends on:` referent not yet delivered) - the forward
direction. The inverse is missing: a unit sits at Status `Blocked` (or carries
a `Depends on:` field or an epic `Blocked By` row) long after the thing it
waited on reached a terminal state, and nothing surfaces it as now-eligible for
the next sprint.

The sweep collects every blocker signal across the artefacts - Status
`Blocked`, a `Depends on:` field, an epic `Blocked By` row - and resolves each
referent's current status. In-repo referents resolve by the file census
(LL0001). Cross-repo referents resolve by reading the sibling repo named in
`product-manifest.yaml`, reusing `pvd.py`'s manifest read (`repos[].path`), so a
capability marked Done in repo A is detected as clearing a Blocked unit in repo
B. A unit whose every blocker is terminal/delivered is reported as a
now-unblocked candidate; a still-blocked unit is reported with its outstanding
referent.

Per LL0008 the sweep fails loud and never false-clears: a referent that is
missing, unreadable, or in an unknown status is reported still-blocked or as an
error, never silently treated as cleared. This story is detection and reporting
only. Wiring the sweep into the pre-plan gate and the reconcile lane is US0050,
and auto-transitioning `Blocked -> Ready` is out of scope - the gated
`transition` call stays the actor.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type        | Constraint                                                                                                                                          | AC Implication                                                         |
| ------ | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Epic   | Determinism | Detection is script-backed and stable across runs; the sweep never reports a unit unblocked while any referent is unresolved or unreadable (LL0008) | AC4 reports such referents still-blocked or as an error, never cleared |
| PRD    | Performance | Not applicable - skill-internal change                                                                                                              | None                                                                   |
| PRD    | Security    | Not applicable - skill-internal change                                                                                                              | None                                                                   |

---

## Acceptance Criteria

### AC1: the sweep collects every blocker signal and reports referent status

- **Given** a repo whose artefacts carry blocker signals (units at Status `Blocked`, `Depends on:` fields, epic `Blocked By` rows)
- **When** the blocker sweep runs
- **Then** it collects every unit with a blocker signal and reports, per unit, each referent with its current status
- **Verify:** pytest -k test_blocker_sweep_collects_signals
- **Verification target:** functional
- **Verified:** no

### AC2: in-repo referents resolve by the file census

- **Given** a Blocked unit whose every referent resolves in-repo to a terminal/delivered status by the file census
- **When** the sweep resolves the referents
- **Then** the unit is reported as a now-unblocked candidate
- **Verify:** pytest -k test_blocker_sweep_in_repo_unblock
- **Verification target:** functional
- **Verified:** no

### AC3: cross-repo referents resolve through the PVD manifest

- **Given** a Blocked unit whose referent lives in a sibling repo named in `product-manifest.yaml` `repos[].path`, where the referent is now Done
- **When** the sweep resolves referents across repos
- **Then** the cleared cross-repo blocker is detected and the unit is reported as a now-unblocked candidate
- **Verify:** pytest -k test_blocker_sweep_cross_repo_unblock
- **Verification target:** functional
- **Verified:** no

### AC4: fail loud, never false-clear

- **Given** a referent that is missing, unreadable, or in an unknown status, including an unreadable cross-repo path
- **When** the sweep resolves it
- **Then** the unit is reported still-blocked or as an error and never silently treated as cleared, and the unreadable cross-repo path is named (LL0008)
- **Verify:** pytest -k test_blocker_sweep_failloud
- **Verification target:** functional
- **Verified:** no

> **Verification target tiers:** `functional` (single round-trip – default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- A blocker-sweep module under `.claude/skills/sdlc-studio/scripts/` (or an
  `audit.py` extension) that collects blocker signals, resolves referents
  in-repo by the file census and cross-repo through the PVD manifest, and
  reports now-unblocked candidates and still-blocked units.
- Reusing `pvd.py`'s manifest read (`repos[].path`) for cross-repo resolution.
- Deterministic, fail-loud reporting per LL0008.

### Out of Scope

- Wiring the sweep into the pre-`plan` gate and the reconcile lane - US0050.
- Auto-transitioning `Blocked -> Ready` - the gated `transition` call stays the
  actor; the sweep only proposes.
- The forward `unmet-deps` check, which `audit.py` already provides.

---

## Technical Notes

This touches `.claude/skills/sdlc-studio/scripts/`: a new blocker-sweep module
or an extension to `audit.py`. It reuses `pvd.py`'s manifest read to resolve
`repos[].path` for cross-repo referents, so the manifest contract has a single
reader. Blocker signals are three: Status `Blocked`, a `Depends on:` field, and
an epic `Blocked By` row; the sweep must gather all three. In-repo referent
status comes from the file census (LL0001); cross-repo status comes from reading
the sibling repo's artefacts at the manifest path. The report is deterministic
and stable across runs. Carry the CHANGELOG `[Unreleased]` entry in the same
commit (LL0004).

### API Contracts

Not applicable - skill-internal change, no external API.

### Data Requirements

None - no persisted state; the sweep reads the existing artefacts and the PVD
manifest and emits a report.

---

## Edge Cases & Error Handling

| Scenario                                                                   | Expected Behaviour                                                                                         |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| A unit has two referents and only one has cleared                          | Reported still-blocked, naming the outstanding referent; not a now-unblocked candidate                     |
| A cross-repo path named in `product-manifest.yaml` is absent or unreadable | The path is named and the unit is reported still-blocked or as an error, never treated as cleared (LL0008) |

> **Minimum edge cases:** 2 for API stories, 2 for others

---

## Test Scenarios

- [ ] Run `pytest -k test_blocker_sweep_in_repo_unblock` against a fixture where a Blocked unit's only referent is Done in-repo, and confirm it is reported as a now-unblocked candidate (AC2).
- [ ] Run `pytest -k test_blocker_sweep_cross_repo_unblock` against a fixture manifest where the referent is Done in a sibling repo, and confirm the cleared cross-repo blocker is detected (AC3).

> **Minimum test scenarios:** 2 for API stories, 2 for UI

---

## Dependencies

### Story Dependencies

None.

### External Dependencies

None.

---

## Estimation

**Story Points:** 5
**Complexity:** High

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
