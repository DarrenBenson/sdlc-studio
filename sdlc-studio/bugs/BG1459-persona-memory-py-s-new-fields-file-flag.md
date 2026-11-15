# BG1459: persona_memory.py's new --fields-file flag is neither judged nor in the unjudged-flags baseline, so test_command_audit's ratchet is red on main

> **Status:** Open
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, sdlc-studio/.unjudged-flags-baseline.txt, sdlc-studio/reviews/command-audit.md, changelog.d/BG1459.md
> **Evidence:** Run thirteen (RUN-01M7EYR3) learn-lane builder hand-back; the test fails at HEAD after the US1058 repair
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run thirteen orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T09:21:54Z

## Summary

US1058's repair gave `persona_memory.py add` a `--fields-file` flag (the prose-writer sweep required it). `test_command_audit.py`::UnjudgedRatchetTests::`test_the_shipped_corpus_matches_its_baseline` now flags `persona_memory.py:fields_file` as not judged, and sdlc-studio/.unjudged-flags-baseline.txt has no entry for it; the land's selected tests did not run that test. US1065 and US1066 add further `persona_memory` flags that need the same treatment.

## Steps to Reproduce

Run pytest .claude/skills/sdlc-studio/scripts/tests/`test_command_audit.py`::UnjudgedRatchetTests at HEAD: `persona_memory.py`:`fields_file` is reported unjudged.

## Proposed Fix

Judge each new `persona_memory` flag the way the ratchet's documentation asks (or record it in the baseline with its reason), so the ratchet test passes.

## Acceptance Criteria

- [ ] **AC1** Given HEAD with `persona_memory.py`'s flags, when the unjudged-flags ratchet runs, then it passes with every `persona_memory` flag judged or baselined with a reason. Fails on: any `persona_memory` flag reported unjudged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::UnjudgedRatchetTests::test_the_shipped_corpus_matches_its_baseline

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run thirteen orchestrator) | Filed |
