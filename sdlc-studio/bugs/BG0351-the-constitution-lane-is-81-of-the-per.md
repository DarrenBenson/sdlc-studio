# BG0351: The constitution lane is 81% of the per-commit artefact gate, and the hook documents that gate as ~1s

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/constitution.py, .claude/skills/sdlc-studio/scripts/gate.py, .githooks/pre-commit
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

Measured in fresh processes on this repo: the whole artefact gate is 32.9s cold and the `constitution` lane alone is 26.6s of it - 81%. `.githooks/pre-commit` describes that gate to the reader as 'fast, ~1s', which is wrong by a factor of thirty-three. This is pure per-commit cost sitting on top of the suites, and it is the largest single lane by a wide margin.

## Steps to Reproduce

`python3 .claude/skills/sdlc-studio/scripts/gate.py --root .` -> `gate cost: 33.6s of a 45s budget; dominant lane: constitution at 26.5s`. `--only constitution` on its own: 24.5s then 23.2s. `gate._constitution` calls `c;`.githooks/pre-commit`, the comment beginning "# Comprehensive artefact gate (fast, ~1s): conformance, reconcile drift, validate, ...". Measured:`time python3 .claude/skills/sdlc-studio/scripts/gate.py --root .` -> real

## Proposed Fix

See the summary; each cited site names its own remedy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Filed |
