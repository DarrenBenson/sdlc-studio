# US0043: lessons re-validation verb: close obsolete lessons by validity (CR0129)

> **Status:** Ready
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Epic:** EP0010
> **Persona:** Dani (Engineering)
> **Depends on:** -

## User Story

**As** the operator
**I want** a re-validation verb that lists open lessons and records closing the obsolete ones
**So that** the lessons log does not grow into stale noise

## Context

### Persona Reference

**Dani (Engineering)** - the engineering amigo who owns the deterministic tooling in `scripts/`, and holds the line that a tool must do what it claims (LL0008).
[Full persona details](../personas.md#dani-engineering)

### Background

Implements part of CR0129. The sprint retro is meant to re-validate accumulated lessons and close the ones no longer valid, but today `lessons.py prune` only closes by epic age. This story generalises that closure from age-based to validity-based: the verb lists the open lessons so the agent can confirm which are still valid, then records the closure (status transition) deterministically. The validity judgement stays the agent's; the recording is mechanical and repeatable.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type        | Constraint                                                                       | AC Implication                                      |
| ------ | ----------- | -------------------------------------------------------------------------------- | --------------------------------------------------- |
| Epic   | Determinism | Lifecycle steps are script-backed, not left to an agent honouring prose (LL0008) | The closure is recorded by the script, not narrated |
| PRD    | Performance | Not applicable - skill-internal change                                           | None                                                |
| PRD    | Security    | Not applicable - skill-internal change                                           | None                                                |

---

## Acceptance Criteria

### AC1: re-validation verb lists open lessons and records closure

- **Given** a lessons log with open entries
- **When** the operator runs the re-validation verb and confirms which open lessons are obsolete
- **Then** `lessons.py` lists the open lessons for confirm/close and records the closure as a status transition, generalising `prune --older` from age-based to validity-based closure
- **Verify:** pytest -k test_lessons_revalidate
- **Verification target:** functional
- **Verified:** no

### AC2: the verb is idempotent

- **Given** a re-validation pass has already closed the obsolete lessons
- **When** the verb is run again with no newly obsolete lessons
- **Then** it closes nothing new and leaves the log unchanged
- **Verify:** pytest -k test_lessons_revalidate_idempotent
- **Verification target:** functional
- **Verified:** no

> **Verification target tiers:** `functional` (single round-trip - default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- The re-validation verb in `lessons.py`: list open lessons, accept the agent's confirm/close decision, record the closure as a status transition, generalising `prune --older`.

### Out of Scope

- The sprint/autosprint/review close gate (US0042).
- The rolling Summary of Learnings generator (US0044).

---

## Technical Notes

Touches `.claude/skills/sdlc-studio/scripts/lessons.py`. The existing `prune --older <epic>` closes lessons whose source epic is older than a cutoff. The new verb keeps the same closure mechanic (status transition on the entry) but selects by continued validity rather than age: it emits the open lessons for the agent to judge, takes the set to close, and records that closure. Reuse the existing status-transition path so closed entries stay queryable rather than being deleted. The selection of which lessons are obsolete is the agent's; the script's job is the deterministic list-and-record.

### API Contracts

Not applicable - this is a CLI verb in a skill-internal Python helper, no network or service contract.

### Data Requirements

Operates on the existing lessons log entries (`.local/lessons.md` plus the skill-tier registry); reads open entries, writes the status transition on the confirmed-obsolete ones. No new schema; the entry status field already exists for `prune`.

---

## Edge Cases & Error Handling

| Scenario                                                         | Expected Behaviour                                                                     |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| No open lessons exist                                            | The verb reports nothing to re-validate and exits cleanly (non-error), closing nothing |
| Agent confirms an empty close set (all open lessons still valid) | The verb records no transition and leaves the log unchanged                            |
| A lesson id passed for closure is already closed                 | Treated as a no-op for that id (idempotent), not an error                              |
| A lesson id passed for closure does not exist                    | Fails loud with a clear error naming the unknown id, recording no partial closure      |

---

## Test Scenarios

- [ ] `test_lessons_revalidate`: a log with open lessons; the verb lists them and, given a confirmed obsolete set, records the closure as a status transition; the closed entries are no longer listed as open.
- [ ] `test_lessons_revalidate_idempotent`: after a closing pass, re-running the verb with no newly obsolete lessons closes nothing new and leaves the log byte-identical.
- [ ] `test_lessons_revalidate_empty`: a log with no open lessons; the verb exits cleanly and records nothing.
- [ ] `test_lessons_revalidate_unknown_id`: closing an unknown lesson id fails loud and records no partial closure.

---

## Dependencies

### Story Dependencies

None

### External Dependencies

| Dependency | Type | Status |
| ---------- | ---- | ------ |
| None       | -    | -      |

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

None

---

## Revision History

| Date       | Author | Change                                               |
| ---------- | ------ | ---------------------------------------------------- |
| 2026-06-27 | Dani   | Authored to Ready (design rung, breakdown of CR0129) |
