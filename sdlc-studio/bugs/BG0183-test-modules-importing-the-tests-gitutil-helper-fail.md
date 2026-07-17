# BG0183: Test modules importing the tests/gitutil helper fail under single-module unittest invocation

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py, .claude/skills/sdlc-studio/scripts/tests/gitutil.py
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

scripts/tests/`test_telemetry.py` does 'from gitutil import git' (a helper at scripts/tests/gitutil.py). It resolves under 'unittest discover -s tests' (tests/ is the discovery root, on sys.path) but NOT under 'python3 -m unittest `tests.test_telemetry`' from the scripts dir (only scripts/ is on sys.path), where 3 ProjectStampTests raise ModuleNotFoundError: No module named 'gitutil'. Every dogfood run and all three fan-out subagents had to special-case 'ignore the 3 gitutil failures', which masks real regressions in those tests.

## Steps to Reproduce

cd .claude/skills/sdlc-studio/scripts && python3 -m unittest `tests.test_telemetry.ProjectStampTests` -> 3 errors, ModuleNotFoundError: No module named 'gitutil'. The same tests pass under 'python3 -m unittest discover -s tests'.

## Proposed Fix

Import the helper package-relatively (from tests.gitutil import git) or add a path shim, so a single test module runs green both ways. Audit other tests for the same tests/-root-only import assumption.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
