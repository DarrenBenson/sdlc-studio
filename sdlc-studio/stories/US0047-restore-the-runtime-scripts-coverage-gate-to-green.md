# US0047: restore the runtime-scripts coverage gate to green on CI (blocks all PR merges)

> **Status:** Ready
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Epic:** EP0010
> **Persona:** Dani (Engineering)
> **Depends on:** -

## User Story

**As** the operator
**I want** the runtime-scripts coverage gate green on CI
**So that** pull requests (including the open Dependabot bumps) can merge

## Context

### Persona Reference

**Dani (Engineering)** - the engineering amigo, owns implementation quality and the deterministic, fail-loud tooling the skill ships and dogfoods.
[Full persona details](../personas.md#dani-engineering)

### Background

The CI step `Coverage gate (runtime scripts, >= 80%)` in `.github/workflows/lint.yml`
fails on `main`, which is why the open Dependabot PRs #25 and #26 are red and cannot
merge. Locally `coverage report` shows TOTAL 83% (passes), so there is a CI-versus-local
discrepancy: some tests likely skip in the CI environment - no `gh` CLI, no git identity,
no external tools - which lowers coverage on files that are already weak: `status.py`
(~51%), `decisions.py` (~55%), `telemetry.py` (~55%), and `autosprint.py` (0%). When
those suites skip on the runner, total coverage drops below the `--fail-under=80`
threshold and the gate fails even though the same command passes on a developer machine
that has the tools installed.

The gate command is:

```sh
coverage run --source=.claude/skills/sdlc-studio/scripts -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
coverage report --omit='*/tests/*' --fail-under=80
```

This story restores the gate to green by making the silently-skipped tests run in the CI
environment (or covering those code paths another way), and records the root cause of the
local-versus-CI gap here so it does not recur.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type        | Constraint                                                                      | AC Implication                                          |
| ------ | ----------- | ------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Epic   | Tech Stack  | Deterministic tooling that fails loud; script changes carry unit tests (LL0008) | New/adjusted tests must execute in CI, not only locally |
| PRD    | Performance | Not applicable - CI/test change                                                 | None                                                    |
| PRD    | Security    | Not applicable - CI/test change                                                 | None                                                    |

---

## Acceptance Criteria

### AC1: Coverage gate passes under the CI environment

- **Given** the runtime-scripts coverage gate currently fails on the CI runner
- **When** the gate command runs in the CI environment (no `gh`, no git identity, no external tools), not only on a developer machine
- **Then** runtime-scripts coverage is >= 80% and the gate exits zero
- **Verify:** bash -lc "cd /home/darren/code/DarrenBenson/sdlc-studio && coverage run --source=.claude/skills/sdlc-studio/scripts -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests && coverage report --omit='*/tests/*' --fail-under=80"
- **Verification target:** functional
- **Verified:** no

### AC2: Local-versus-CI discrepancy identified and removed

- **Given** coverage passes locally (TOTAL 83%) but fails on CI because some tests skip on the runner
- **When** the cause is investigated and addressed
- **Then** the tests that silently skip on CI are made to run (or those code paths are covered another way), and the root cause of the gap is noted in this story so the gate is honest on both local and CI runs
- **Verify:** manual
- **Verification target:** functional
- **Verified:** no

> **Verification target tiers:** `functional` (single round-trip - default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- Getting the runtime-scripts coverage gate green on CI: making the suites that skip on the runner (`status.py`, `decisions.py`, `telemetry.py`, `autosprint.py`) run there - via stubs, fixtures, or mocks - so coverage clears `--fail-under=80` in the CI environment, and recording the root cause of the local-versus-CI gap in this story.

### Out of Scope

- The action-version bumps for the Dependabot PRs (`actions/checkout` and friends); that work is US0048. This story only unblocks the gate so those PRs can go green.

---

## Technical Notes

The change touches `.claude/skills/sdlc-studio/scripts/tests/` (added or adjusted tests
that no longer skip when external tools are absent) and possibly
`.github/workflows/lint.yml` if the runner needs an environment fix to make a suite run.
The weak files are `status.py`, `decisions.py`, and `telemetry.py` (~51-55% each) plus
`autosprint.py` at 0%; the lift comes from covering their currently-skipped paths in the
CI environment rather than lowering the threshold. Prefer injecting fakes or stubbing the
external-tool boundary (`gh`, git identity) over real calls, so the tests are
deterministic on any runner. Do not change `--fail-under=80`. Add the CHANGELOG
`[Unreleased]` entry in the same commit (LL0004).

### API Contracts

Not applicable - CI and test change with no API surface.

### Data Requirements

Not applicable - no production data is read or written.

---

## Edge Cases & Error Handling

| Scenario                                                                                    | Expected Behaviour                                                                                                                                                        |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A test calls out to `gh`, git identity, or another external tool absent from the CI runner  | The test exercises the code path via a stub, fixture, or mock so it runs in CI rather than skipping; coverage no longer drops on the CI runner                            |
| A code path cannot be reached without a real external tool (e.g. live `gh` network call)    | The path is covered another way (injected fake / direct unit call) or, if genuinely unreachable, excluded with a documented `# pragma: no cover` so the gate stays honest |
| Coverage sits just above 80% locally but a single skipped suite tips CI below the threshold | The skip is removed at root cause; the gate is not lowered and `--fail-under=80` is unchanged                                                                             |

---

## Test Scenarios

- [ ] Run the gate command in an environment with `gh`, git identity, and external tools removed (simulating CI) and confirm it exits zero with coverage >= 80%.
- [ ] Confirm the previously-skipped suites for `status.py`, `decisions.py`, `telemetry.py`, and `autosprint.py` now execute (no `SKIPPED` markers from missing tools) and contribute coverage on the runner.

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

| Date       | Author | Change                                                             |
| ---------- | ------ | ------------------------------------------------------------------ |
| 2026-06-27 | Dani   | Authored to Ready (design rung, CI health for Dependabot adoption) |
