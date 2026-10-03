# BG0929: migrate does not report the retired handoff surface in a project's own docs

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/retired_surface.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_retired_handoff_surface.py, changelog.d/BG0929.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T11:42:06Z

## Summary

6.1 retires the handoff writers, artifact.py new --type handoff and gate.py --require-handoff, but migrate's retired-surface scan (lib/`retired_surface.py`, fed by each script's `RETIRED_VERBS`, the changelog's retired flags and `sdlc_md`'s retired keys) names none of them in a consuming project's docs, so a 6.0 user upgrading is not told their runbook calls a removed command. Found while grooming US0983/US0984 for v6.1.0 (D0326).

## Steps to Reproduce

1. A consuming README whose code spans and fences use the handoff writers, artifact.py new --type handoff and gate.py --require-handoff. 2. Run migrate. 3. None of them is named.

## Proposed Fix

Register the retired handoff surface where the scan already reads retirements (the scripts' `RETIRED_VERBS`, the retired-flag source), so migrate names it; no new check.

## Acceptance Criteria

- [ ] **AC1** Given a consuming document that uses the retired handoff writers, artifact.py new --type handoff and gate.py --require-handoff in code, and names handoffs in prose, when migrate's retired-surface scan runs, then each retired command is named with its replacement and the prose line is not. Fails on: the current scan, which names none of them
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retired_handoff_surface.py::RetiredHandoffSurfaceTests::test_the_retired_handoff_surface_is_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
