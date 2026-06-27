# US0046: pre-deploy readiness checklist doc (CR0127)

> **Status:** Done
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Epic:** EP0010
> **Persona:** Dani (Engineering)
> **Depends on:** -

## User Story

**As an** operator deploying any consuming project
**I want** a pre-deploy readiness checklist in the skill
**So that** the recurring deploy-time failure classes are caught before production

## Context

### Persona Reference

**Dani (Engineering)** - the engineering amigo, owns implementation quality and the deploy-readiness doctrine the skill ships to consuming projects.
[Full persona details](../personas.md#dani-engineering)

### Background

Implements CR0127. This is a documentation change to `reference-deploy-readiness.md`,
distilled from a consuming repo's release lessons (v1.2.1-v1.4.0) plus a durability
incident. The same deploy-time failures recur across projects because the skill
describes post-deploy verification but has no pre-deploy checklist that catches these
classes before they reach production: env-var default drift, durability contracts
betrayed by non-persistent paths, remote-command quoting footguns, and ops helpers that
diverge from a canonical crypto serialisation format. A reusable checklist (and, where
mechanisable, a gate) means a consuming project inherits the defences instead of
rediscovering them in production.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type          | Constraint                                                         | AC Implication                                                   |
| ------ | ------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Epic   | Documentation | Skill reference docs stay tool-neutral and progressively disclosed | Checklist is generic deploy-readiness wisdom, not a project fact |
| PRD    | Performance   | Not applicable - skill-internal change                             | None                                                             |
| PRD    | Security      | Not applicable - skill-internal change                             | None                                                             |

---

## Acceptance Criteria

### AC1: Pre-Deploy Checklist section added

- **Given** `reference-deploy-readiness.md` describes only post-deploy verification
- **When** the operator reads the doc before a release
- **Then** it contains a Pre-Deploy Checklist covering the env-key diff (refuse on missing required keys), the persistent-volume assertion for filesystem durability contracts (with the "restart the container; verify data survives" AC pattern), the remote-command heredoc discipline, and the crypto serialisation round-trip for ops helpers
- **Verify:** manual
- **Verification target:** functional
- **Verified:** no

### AC2: Links and style pass

- **Given** the doc has been edited with new anchors and cross-links
- **When** the repo lint suite runs
- **Then** the anchor links resolve and the style guard passes
- **Verify:** shell npm run lint:links
- **Verification target:** functional
- **Verified:** yes (2026-06-27)

> **Verification target tiers:** `functional` (single round-trip - default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- The Pre-Deploy Checklist documentation in `reference-deploy-readiness.md`, with cross-links to [[LL0006]] and `reference-operator-heuristics.md`, marking mechanical checks (env-key diff, persistent-volume assertion) versus advisory ones (crypto round-trip discipline).

### Out of Scope

- Wiring a release-script gate in any specific consuming project; the doc specifies the check so a project can wire it, but no consuming repo is touched here.

---

## Technical Notes

Touches a single file: `.claude/skills/sdlc-studio/reference-deploy-readiness.md`. No
scripts, schema, or runtime code change. The env-key diff and persistent-volume
assertion are written as mechanical checks a project wires into its release script or
startup (refuse / abort on failure), per [[LL0008]]; the crypto round-trip is named as
advisory with the reason. Add the CHANGELOG `[Unreleased]` entry in the same commit
([[LL0004]]).

### API Contracts

Not applicable - documentation-only change with no API surface.

### Data Requirements

Not applicable - no data is read or written.

---

## Edge Cases & Error Handling

| Scenario                                                                                                               | Expected Behaviour                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| A reader checks the env-key item but finds no refuse-on-missing instruction                                            | Documentation defect; the item must state the release script refuses deploy when required keys are absent |
| A reader checks the persistent-volume item but the "restart the container; verify data survives" AC pattern is missing | Documentation defect; the item must prescribe that AC pattern for any filesystem durability contract      |

---

## Test Scenarios

- [ ] Read the Pre-Deploy Checklist and confirm all four classes (env-key diff, persistent-volume assertion, remote heredoc discipline, crypto round-trip) are present and each names whether it is mechanical or advisory.
- [ ] Run `npm run lint:links && npm run lint:style` and confirm both pass, including the new anchors and the [[LL0006]] / `reference-operator-heuristics.md` cross-links.

---

## Dependencies

### Story Dependencies

None.

### External Dependencies

| Dependency | Type | Status |
| ---------- | ---- | ------ |
| None       | -    | -      |

---

## Estimation

**Story Points:** 2
**Complexity:** Low

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
| 2026-06-27 | Dani   | Authored to Ready (design rung, breakdown of CR0127) |
