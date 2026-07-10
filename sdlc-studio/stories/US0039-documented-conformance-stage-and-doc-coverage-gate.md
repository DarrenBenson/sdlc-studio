# US0039: documented conformance stage and doc-coverage gate

> **Status:** Done
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Epic:** EP0007

## User Story

**As a** team running autosprint
**I want** documentation to be part of the Definition of Done, enforced deterministically
**So that** docs cannot drift (the gap the self-audit found) - CR0053.

## Acceptance Criteria

### AC1: doc-coverage check - catalogue + reference floor, skill-dev only

- **Given** the skill repo
- **When** `doc_coverage check` runs
- **Then** it hard-fails a Type-Reference command missing from help/help.md or a script missing from reference-scripts.md (a prose backtick does not count), soft-warns an empty CHANGELOG [Unreleased], and no-ops for a consuming repo (no SKILL.md)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py::DocCoverageTests
- **Verified:** yes (2026-06-21)

### AC2: wired into the gate + conformance `documented` stage

- **Given** a missing doc entry
- **When** the gate / conformance run
- **Then** doc-coverage is a blocking gate check and `documented` is a hard-fail conformance stage for Done units; a consuming repo (no SKILL.md) is unaffected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::GateRealWrapperTests::test_default_checks_present
- **Verified:** yes (2026-06-21)

### AC3: the autosprint DoD documents the requirement

- **Given** reference-sprint.md
- **When** read
- **Then** the DoD requires user/operator docs updated, the `documented` stage is in the conformance list, and the final-report + Phase-1-clarify are present
- **Verify:** grep -q "documented" .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-07-10)

## Implementation

`scripts/doc_coverage.py` (catalogue+reference floor, CHANGELOG soft-warn, skill-dev no-op);
wired into `gate.py` (blocking) + `conformance.py` (`documented` stage, repo-global like
`reconciled`); reference-autosprint DoD + documented stage + final report + Phase-1 clarify.
Brought the repo to compliance (15 doc gaps closed). Also fixed `_wire_story_to_epic` to
preserve prose/internal blanks + exact-id idempotency (critic).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0053) | Created by `new`; the new gate forced 15 doc gaps green (dogfood); critic REJECT->fixed (backtick false-pass, disp-substring drop) |
