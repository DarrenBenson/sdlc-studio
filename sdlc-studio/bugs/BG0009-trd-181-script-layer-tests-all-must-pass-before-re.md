# BG-0009: TRD '181 script-layer tests, all must pass before release' gate fails in the installed copy

> **Status:** Closed
> **Severity:** High
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

The TRD frames the 181-test suite as the script layer's release gate, but the suite includes ~19 tests for repo-root tools/ resolved via parents[5], so the documented gate command yields 154 tests and 4 errors in the installed copy the TRD names as the production-fix source.

## Problem

trd.md:116/164/468 frame the unittest suite as the script-layer gate ('181 passing', 'all must pass before a release is tagged'). But test_check_budgets/links/versions.py and test_validate_skill.py resolve targets via Path(**file**).parents[5]/tools/..., which exists only in the dev repo. Running the gate command in ~/.claude/skills/sdlc-studio (the declared back-port/production source) yields 'Ran 154 tests ... FAILED (errors=4)' with FileNotFoundError on the tools/ paths.

## Proposed Fix

State the gate honestly: the 181-count is the dev-repo suite, which includes ~19 tests for repo-root tools/ that are not part of the shipped 10-script layer. Either describe the script-layer subset count separately, or make the tools-tests skip cleanly when tools/ is absent so the documented command passes in an installed copy. Correct the 'for the script layer' wording.

## Evidence

scripts/tests/test_check_versions.py:15 (parents[5]/'tools') and installed-copy run 'Ran 154 tests ... FAILED (errors=4)' vs trd.md:116 '181 passing for the script layer'

## Impact

A maintainer back-porting a fix into the installed copy and running the TRD's documented release gate gets 4 errors and a non-181 count exactly where the TRD says production fixes land; a harness migrator inherits hard-coded parents[5]/tools paths that break outside this repo layout.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: trd) |
