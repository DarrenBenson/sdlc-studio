# BG0351: The constitution lane is 81% of the per-commit artefact gate, and the hook documents that gate as ~1s

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/constitution.py, .claude/skills/sdlc-studio/scripts/gate.py, .githooks/pre-commit
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

Measured in fresh processes on this repo: the whole artefact gate is 32.9s cold and the constitution lane alone is 26.6s of it - 81%. .githooks/pre-commit describes that gate to the reader as 'fast, ~1s', which is wrong by a factor of thirty-three. This is pure per-commit cost sitting on top of the suites, and it is the largest single lane by a wide margin.

## Steps to Reproduce

Run the gate with no arguments and it reports its own cost: 33.6s of a 45s budget, dominant lane constitution at 26.5s. Measured again in fresh processes to remove warm-cache confounding: the whole artefact gate 32.9s, the constitution lane alone 26.6s - 81% of it. The pre-commit hook's own comment describes that gate as a comprehensive artefact gate that is fast, about one second, which is wrong by a factor of thirty-three.

## Proposed Fix

See the summary; each cited site names its own remedy.

## Acceptance Criteria

### AC1: the artefact gate's dominant lane is affordable per commit and its cost is stated honestly

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::GateBudgetTests
- **Verified:** yes (2026-07-28, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Filed |
| 2026-07-28 | Claude Fable 5 | Acceptance criterion authored at review - the unit reached Fixed without one, which CR0459 exists to refuse |
