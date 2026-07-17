# BG0162: TSD's per-script test-module gate is a phantom: no conformance sweep exists, and the invariant it claims to enforce is already violated by six modules

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/tsd.md, .claude/skills/sdlc-studio/scripts/conformance.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a
> **Delivered-by:** claude-opus-4-8

## Summary

tsd.md:199-201 states 'Every script and every shared-library module has a dedicated test module... a conformance sweep fails the build on a new script that arrives without one.' No such sweep exists anywhere: conformance.py contains zero test-related checks, `doc_coverage.py` checks docs entries only, and nothing in tools/ or scripts/tests/ asserts a `test_`<script>.py per script. The invariant is violated NOW: autosprint.py, refine.py, triage.py have no dedicated test module, nor do lib/`run_state.py`, lib/tiers.py, lib/xrepo.py - and autosprint.py plus lib/xrepo.py are imported by no test at all. The panel softened the coverage half (refine/triage/`run_state`/tiers are exercised under differently-named modules) but confirmed the phantom-gate claim, squarely LL0010/LL0027 - the repo's own filed-defect class. Verified 3x.

## Steps to Reproduce

grep 'test' over conformance.py - no output; ls scripts/tests/ - no `test_autosprint.py`/`test_refine.py`/`test_triage.py` and no dedicated lib test for `run_state`/tiers/xrepo; grep 'import autosprint' across tests/ - no hits.

## Proposed Fix

Either build the sweep (a test enumerating scripts/*.py and lib/*.py asserting a dedicated test module, with an allowlist for shims and modules covered under a named alternative), or correct tsd.md:199-201 to state the actual contract (dedicated modules for most, named indirect coverage for the rest, no build gate). Give xrepo.py and autosprint.py at least import-level coverage either way.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
