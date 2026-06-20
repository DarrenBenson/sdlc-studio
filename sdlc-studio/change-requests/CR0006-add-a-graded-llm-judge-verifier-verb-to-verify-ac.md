# CR-0006: Add a graded/LLM-judge verifier verb to verify_ac DSL for AI-output and qualitative ACs

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** Adversarial Audit
> **Date:** 2026-06-20
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Depends on:** --
> **GitHub Issue:** --

## Summary

verify_ac's DSL is binary exit-code checks only; qualitative or AI-output ACs (faithfulness, helpfulness, on-tone) fall into the un-graded 'manual' bucket, so a skill marketed for AI/agent projects has no executable path to gate on a quality threshold the way DeepEval/promptfoo do.

## Problem

verify_ac's DSL is deterministic exit-code checks (pytest/jest/vitest/go/file/grep/http+jq/shell, unrecognised -> shell), with non-runnable ACs counted as 'manual' and deferred to a human (verify_ac.py:283/303/360/449-453). This is fine for code ACs but cannot verify qualitative or AI-output ACs. Eval-driven tooling (DeepEval, promptfoo) - the benchmark for LLM-backed behaviour - provides rubric/LLM-judge assertions, golden-dataset thresholds, and pytest-integrated CI gates that fail the build below a score. SDLC Studio markets itself for AI/agent projects (agentic-lessons references) yet has no path to gate on a graded threshold; such ACs sit un-graded in 'manual'.

## Proposed Changes

### Item 1: Add a graded/LLM-judge verifier verb to verify_ac DSL for AI-output and qualitative ACs

**Priority:** Medium **Effort:** TBD

Add a graded verifier to the DSL, e.g. 'eval <promptfoo-config> --threshold 0.8' or 'deepeval <test>', that shells to the eval tool, parses its JSON score, and passes only above threshold (a new soft dependency alongside pytest/jest). Bounded: one new DSL verb plus a report field, reusing the existing subprocess/JSON-report plumbing.

## Impact Assessment

### Existing Functionality

For AI-output ACs (a stated target domain) there is currently no executable verification - they sit un-graded as 'manual'. A graded verb closes the gap eval-driven tooling already solves and keeps reconcile --verify meaningful for LLM features. Quality risk medium.

## Acceptance Criteria

- [x] The `verify_ac` DSL accepts a graded verb (e.g. `eval <config> --threshold 0.8`) that shells to the eval tool, parses its JSON score, and passes only at or above the threshold.
- [x] A below-threshold score fails the AC and the score is recorded in the report. Unit-tested against a stub eval tool.

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (backlog-closeout) | Complete - US0020: graded eval verb (pluggable, stubbed); critic-approved after guarding non-numeric threshold |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: external-benchmark; evidence: .claude/skills/sdlc-studio/scripts/verify_ac.py:449-453 (non-runnable ACs counted 'manual', un-graded); benchmark <https://www.promptfoo.dev/docs/intro/>) |
