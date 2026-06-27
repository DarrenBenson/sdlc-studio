# US0048: adopt Dependabot CI action bumps: actions/checkout v7, actions/setup-python v6

> **Status:** Done
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Epic:** EP0010
> **Persona:** Dani (Engineering)
> **Depends on:** US0047

## User Story

**As** the maintainer
**I want** the two Dependabot CI action bumps adopted
**So that** the lint workflow runs on supported action versions

## Context

### Persona Reference

**Dani (Engineering)** - the engineering amigo, owns deterministic skill-internal tooling and the scripts that back the lifecycle.
[Full persona details](../personas.md#dani-engineering)

### Background

Dependabot opened PR #25 (actions/checkout v6 -> v7) and PR #26 (actions/setup-python v5 -> v6), both editing `.github/workflows/lint.yml`. Both PRs are blocked by the red coverage gate (US0047); once that gate is green the bumps can merge. The workflow currently pins `actions/checkout@v6` (two uses) and `actions/setup-python@v5`. This story adopts the two bumps and confirms CI is green on the updated workflow.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type        | Constraint                                                          | AC Implication                                                          |
| ------ | ----------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Epic   | CI hygiene  | The lint workflow must run on supported, maintained action versions | AC1 asserts the bumped versions are referenced; AC2 asserts CI is green |
| PRD    | Performance | Not applicable - CI change                                          | None                                                                    |
| PRD    | Security    | Not applicable - CI change                                          | None                                                                    |

---

## Acceptance Criteria

### AC1: lint.yml references the bumped action versions

- **Given** `.github/workflows/lint.yml` pinning `actions/checkout@v6` (two uses) and `actions/setup-python@v5`
- **When** the Dependabot bumps are adopted
- **Then** the workflow references `actions/checkout@v7` (both uses) and `actions/setup-python@v6`, with no `@v6` checkout or `@v5` setup-python references left
- **Verify:** shell ! grep -qE 'actions/checkout@v6|actions/setup-python@v5' .github/workflows/lint.yml && grep -q 'actions/checkout@v7' .github/workflows/lint.yml && grep -q 'actions/setup-python@v6' .github/workflows/lint.yml
- **Verification target:** functional
- **Verified:** yes (2026-06-27)

### AC2: CI is green and the Dependabot PRs are resolved

- **Given** the coverage gate restored to green (US0047) and the bumped workflow
- **When** the lint workflow runs on the updated `lint.yml`
- **Then** CI is green and the two Dependabot PRs (#25, #26) are merged or closed as superseded
- **Verify:** manual
- **Verification target:** functional
- **Verified:** yes (2026-06-27) - CI run 28283114206 succeeded on the bumped workflow; PRs #25/#26 closed as superseded

> **Verification target tiers:** `functional` (single round-trip – default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- Adopting the two action-version bumps in `.github/workflows/lint.yml`: `actions/checkout` v6 -> v7 (both uses) and `actions/setup-python` v5 -> v6.

### Out of Scope

- The coverage-gate fix that unblocks the bump PRs (US0047).

---

## Technical Notes

Touches `.github/workflows/lint.yml` only. The change is the two version bumps already proposed by Dependabot in PR #25 and PR #26. Preferred path is to let those PRs merge once US0047 turns CI green; the same outcome can be reached by editing `lint.yml` directly and closing the PRs as superseded. Either way the end state is `actions/checkout@v7` on both uses and `actions/setup-python@v6`.

### API Contracts

Not applicable - CI workflow change, no network contract.

### Data Requirements

Not applicable - no data or schema change.

---

## Edge Cases & Error Handling

| Scenario                                                             | Expected Behaviour                                                                   |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| A v6 or v5 reference is left behind after the bump                   | AC1 grep fails, so the story does not reach Done until every reference is on v7 / v6 |
| actions/checkout v7 changes default behaviour the workflow relied on | The lint run is re-run on the bumped workflow; AC2 stays unmet until CI is green     |
| Dependabot rebases #25 / #26 onto a now-green main                   | The bumps merge cleanly via the existing PRs; no manual edit of lint.yml is needed   |

> **Minimum edge cases:** 2 for API stories, 2 for others

---

## Test Scenarios

- [ ] AC1 grep passes only when both checkout uses are `@v7` and setup-python is `@v6`, and fails if any `@v6` checkout or `@v5` setup-python reference remains.
- [ ] The lint workflow run on the bumped `lint.yml` completes green end to end.

> **Minimum test scenarios:** 2 for API stories, 2 for UI

---

## Dependencies

### Story Dependencies

| Story                                                                  | Type     | What's Needed                                                             | Status |
| ---------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------- | ------ |
| [US0047](US0047-restore-the-runtime-scripts-coverage-gate-to-green.md) | blocking | The coverage gate must be green on CI first, or the bump PRs cannot merge | Ready  |

### External Dependencies

| Dependency | Type | Status |
| ---------- | ---- | ------ |
| None       | -    | -      |

---

## Estimation

**Story Points:** 1
**Complexity:** Low

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
| 2026-06-27 | Dani   | Authored to Ready (design rung, Dependabot adoption) |
