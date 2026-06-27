# US0044: rolling LESSONS-SUMMARY generator + sprint-start read (CR0129)

> **Status:** Ready
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Epic:** EP0010
> **Persona:** Dani (Engineering)
> **Depends on:** US0040, US0043

## User Story

**As** the operator
**I want** a script-backed rolling summary of still-valid lessons that a new sprint reads at the start
**So that** the loop learns cheaply without loading the full log

## Context

### Persona Reference

**Dani (Engineering)** - the engineering amigo, owns deterministic skill-internal tooling and the scripts that back the lifecycle.
[Full persona details](../personas.md#dani-engineering)

### Background

Implements part of CR0129. The retro lifecycle accrues lessons, but the full log grows
and is expensive to load every sprint. This story applies progressive disclosure to
lessons: the full log stays the archive and `retros/LESSONS-SUMMARY.md` becomes the loaded
digest, the same token-vs-context trade-off as the index-archive work in US0040 / CR0125.
A script-backed generator refreshes the committed summary from the still-valid lesson set,
and the sprint-start step reads the summary plus `lessons recall` instead of the whole log.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type        | Constraint                                                    | AC Implication                                       |
| ------ | ----------- | ------------------------------------------------------------- | ---------------------------------------------------- |
| Epic   | Determinism | Lifecycle steps are script-backed, not prose an agent honours | The generator is a `lessons.py` verb with unit tests |
| PRD    | Performance | Not applicable - skill-internal change                        | None                                                 |
| PRD    | Security    | Not applicable - skill-internal change                        | None                                                 |

---

## Acceptance Criteria

### AC1: script-backed generator refreshes the committed summary

- **Given** a still-valid lesson set
- **When** the summary generator runs at retro close
- **Then** `retros/LESSONS-SUMMARY.md` is refreshed from the still-valid lessons and committed (unlike the gitignored `.local/lessons.md`)
- **Verify:** pytest -k test_lessons_summary_generator
- **Verification target:** functional
- **Verified:** no

### AC2: summary regenerates deterministically

- **Given** a fixture lesson set
- **When** the generator runs twice over the same input
- **Then** the produced summary is byte-identical, so the refresh is deterministic and idempotent
- **Verify:** pytest -k test_lessons_summary_deterministic
- **Verification target:** functional
- **Verified:** no

### AC3: sprint start reads the summary, not the full log

- **Given** a new sprint starting
- **When** it loads prior learning
- **Then** it reads `LESSONS-SUMMARY.md` plus `lessons recall` instead of the full log, and `reference-sprint.md` step 7 is updated to describe the lifecycle
- **Verify:** manual
- **Verification target:** functional
- **Verified:** no

> **Verification target tiers:** `functional` (single round-trip – default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- The summary generator that refreshes `retros/LESSONS-SUMMARY.md` from the still-valid lessons.
- The sprint-start read wiring that loads the summary plus `lessons recall`.

### Out of Scope

- The retro hard close gate (US0042).
- The lessons re-validation verb (US0043).

---

## Technical Notes

Touches `.claude/skills/sdlc-studio/scripts/lessons.py` (the generator verb) and
`.claude/skills/sdlc-studio/reference-sprint.md` (step 7 lifecycle description and the
sprint-start read wiring). The generator reads the still-valid lesson set produced by the
re-validation pass (US0043) and writes a committed digest; the full log remains the archive.

### API Contracts

Not applicable - the generator is a CLI verb on `scripts/lessons.py`, no network contract.

### Data Requirements

Reads the existing lesson records (status/origin fields already on each lesson); writes
`retros/LESSONS-SUMMARY.md`. No new schema.

---

## Edge Cases & Error Handling

| Scenario                                           | Expected Behaviour                                                                                                      |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| No still-valid lessons remain                      | The generator writes a summary with an explicit empty marker rather than failing or leaving a stale file.               |
| `retros/` directory does not yet exist             | The generator creates it before writing the summary.                                                                    |
| Every open lesson was just closed by re-validation | The summary contains only closed/superseded context as needed and reflects the empty still-valid set deterministically. |

> **Minimum edge cases:** 2 for API stories, 2 for others

---

## Test Scenarios

- [ ] `test_lessons_summary_generator`: a populated lesson set produces a committed `LESSONS-SUMMARY.md` containing the still-valid lessons.
- [ ] `test_lessons_summary_deterministic`: regenerating from a fixture lesson set yields byte-identical output.
- [ ] Empty still-valid set produces a summary with the empty marker, no crash.

> **Minimum test scenarios:** 2 for API stories, 2 for UI

---

## Dependencies

### Story Dependencies

| Story                                                                    | Type     | What's Needed                                                | Status |
| ------------------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------ |
| [US0040](US0040-index-archive-writer-terminal-status-vocab-flag-dry.md)  | blocking | The archive/summary-vs-detail pattern this generator mirrors | Ready  |
| [US0043](US0043-lessons-re-validation-verb-close-obsolete-lessons-by.md) | blocking | The still-valid lesson set the summary distils               | Ready  |

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

- None

---

## Revision History

| Date       | Author | Change                                               |
| ---------- | ------ | ---------------------------------------------------- |
| 2026-06-27 | Dani   | Authored to Ready (design rung, breakdown of CR0129) |

</content>
</invoke>
