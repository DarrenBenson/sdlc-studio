# BG1417: CI's lint.yml sets up Node 20 while markdownlint-cli and markdownlint declare node >=22, so the gap is invisible until a dependency uses a Node 22 API

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .github/workflows/lint.yml, .claude/skills/sdlc-studio/scripts/tests/test_ci_node_version.py, changelog.d/BG1417.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: repair verifyfix
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:13:50Z

## Summary

lint.yml uses node-version '20' (lines 35, 127, 192); npm ci only warns.

## Steps to Reproduce

npm ci under Node 20 warns.

## Proposed Fix

Move CI to Node 22.

## Acceptance Criteria

- [ ] **AC1** Given lint.yml and package-lock.json, when compared, then the Node version meets every engines requirement. Fails on: Node 20 against a node >=22 engine.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ci_node_version.py::CiNodeVersionTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
