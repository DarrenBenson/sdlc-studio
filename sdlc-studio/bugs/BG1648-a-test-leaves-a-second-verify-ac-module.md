# BG1648: A test leaves a second verify_ac module in sys.modules, so later tests patch an object the code no longer imports

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/surface.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_surface.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T02:18:22Z

## Summary

BG1647's builder (RUN-01M7TTK3) confirmed that in the gate's parallel suite a freshly loaded `verify_ac` replaces the one tests imported, so a patch on the test's module object never reaches code that imports `verify_ac` at call time (`transition.line_coverage_lane).` BG1647 guarded its own test by holding sys.modules['`verify_ac`'] for the call, but the test that leaves the second module behind was not found: code reading points to lib/`surface._load` or `test_conformance.py`:1555. Any other test that patches `verify_ac` and calls through transition can fail the same way, only in the gate's run.

## Steps to Reproduce

Load `verify_ac` afresh with importlib and put it in sys.modules['`verify_ac`'], then run a test that patches the originally imported `verify_ac.coverage_report` and calls `transition.line_coverage_lane`: the real `coverage_report` runs.

## Proposed Fix

Find the loader that replaces sys.modules['`verify_ac`'] (lib/`surface._load`, `test_conformance.py`:1555) and have it restore the prior entry, or load under a private name; add a suite-level check that sys.modules['`verify_ac`'] is the same object before and after each module that touches it.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1647's builder (RUN-01M7TTK3) confirmed that in the gate's parallel suite a freshly loaded `verify_ac` replaces the one tests imported, so a patch on the...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Load `verify_ac` afresh with importlib and put it in sys.modules['`verify_ac`'], then run a test that patches the originally imported...
- [ ] **AC3** The proposed fix lands, pinned by a test: Find the loader that replaces sys.modules['`verify_ac`'] (lib/`surface._load`, `test_conformance.py`:1555) and have it restore the prior entry, or load under a...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
