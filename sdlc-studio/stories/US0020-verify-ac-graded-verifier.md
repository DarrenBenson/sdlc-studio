# US0020: verify_ac graded (eval) verifier verb

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Autosprint (CR0006, backlog-closeout)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As a** story author
**I want** a graded verifier verb for AI-output and qualitative ACs
**So that** an AC can pass on a score threshold from an eval tool, not just a
binary exit code (CR0006).

## Context

Implements CR0006. A new `eval <command> --threshold <float>` verb in the
verify_ac DSL shells to a configurable eval tool (promptfoo/deepeval/...), parses
a numeric `score` from its JSON stdout, and passes only when score >= threshold.
The tool is a soft dependency (like pytest/jest); tests stub it. Documented in
`reference-verify.md`.

## Acceptance Criteria

### AC1: Passes at or above threshold, fails below

- **Given** an eval tool emitting `{"score": 0.9}` and a threshold 0.8
- **When** the verifier runs, and again with score 0.5
- **Then** the first passes (score recorded) and the second fails
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EvalVerbTests::test_passes_at_or_above_threshold
- **Verified:** yes (2026-06-20)

### AC2: Below-threshold fails with the score

- **Given** a score below the threshold
- **When** the verifier runs
- **Then** it fails and the score is captured on the result
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EvalVerbTests::test_fails_below_threshold
- **Verified:** yes (2026-06-20)

### AC3: Malformed input fails cleanly

- **Given** a missing `--threshold`, or non-numeric tool output
- **When** the verifier runs
- **Then** it fails as kind `eval` (no crash)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EvalVerbTests::test_non_numeric_score_fails
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/verify_ac.py`: `_run_eval` dispatched from `run_verifier`;
`VerifierResult.score`; the score recorded in the report. DSL row in
`reference-verify.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0006) | Decomposed from CR0006 (backlog-closeout) |
