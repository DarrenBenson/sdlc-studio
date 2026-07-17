# CR-0340: Gate: track test-suite runtime, warn before a long run, and skip the unit suite for test-irrelevant changes

> **Status:** In Progress
> **Decomposed-into:** EP0072
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, tools/lint-style.sh
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The pre-commit gate runs the full skill+tool unit suite (~2,800 tests, ~2.5 min) on EVERY commit, exceeding common tool timeouts (the 2-min default) so each commit needs a manual long timeout - and it pays that cost even for a README/CHANGELOG/docs-only change that cannot affect a test outcome. Three improvements: measure it, warn about it, and skip the suite when nothing test-relevant changed.

## Impact

Every committer (human or agent) pays ~2.5 min per commit and must pre-set a long timeout; a docs-only fix pays the same as a code change. The runtime is untracked, so no one can warn about it or see it drift.

## Acceptance Criteria

- [ ] The gate records each run's test-suite wall-time to a rolling local history.
- [ ] Before running the suite the gate estimates duration from that history and prints a warning when it exceeds a configurable threshold (e.g. `gate.warn_seconds)`, so a long run is expected, not a surprise timeout.
- [ ] When the changed set contains NO file that can change a unit-test outcome (no scripts/**/*.py, no tracked artifact/config a test loads - e.g. only README/CHANGELOG/docs/reference-*/help/*), the gate SKIPS the Python unit suite while STILL running style/links/markdown/doc-coverage; the skip is named in the output, never silent, and any code/artifact/test change forces the full suite.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
