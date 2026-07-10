# BG0104: legacy Verify lines rotted through renames and reached the v4.0.0-rc.1 tag

> **Status:** Fixed
> **Verification depth:** functional (all 43 stale Verify lines repaired against current truth and individually re-run; full verify pass exit 0; critic spot-checked every judgement repair against AC text and git history, confirmed the 5 manual demotions and the mode-only chmod)
> **Severity:** Medium
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

The pre-tag verify pass surfaced 50 failing executable ACs across 33 old stories (autosprint->sprint file renames, refactored test class/-k names, evolved reference content, two prose-in-Verify lines). The tool behaved correctly (`verify_ac` exited 1 and printed every failure); the orchestrator piped output through tail and misparsed the report JSON, declared failures: 0, and tagged. Payload code is green (1632-test suite, gate PASS) - the rot is in the story artefacts' verify layer, i.e. Done stopped meaning done for pre-v4 stories. Fix forward: repair every Verify line to current truth (or demote to manual where the check became prose), `verify_ac` fail=0, and close the ritual gap so this cannot recur.

## Steps to Reproduce

python3 scripts/`verify_ac.py` run --root . -> exit 1, 43 failures after the mechanical rename fixes; the tag exists at a780302

## Proposed Fix

repair each stale Verify line against current tests/content and re-run to green; ritual gap filed separately (gate --release)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Filed |
