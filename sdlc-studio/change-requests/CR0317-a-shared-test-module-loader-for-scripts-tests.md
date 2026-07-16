# CR-0317: A shared test-module loader for scripts/tests: forty files duplicate the importlib spec dance and every new module re-trips on it

> **Status:** Complete
> **Decomposed-into:** EP0060
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/gitutil.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; sprint-run retro RUN-01KXGPBN

## Summary

L-0048/L-0051 (extract the shared definition) applied to the test suite's own convention: add a tiny shared helper beside the existing tests/gitutil.py - `load_script(name)` performing the `spec_from_file_location` + sys.modules registration - and adopt it in new test modules (existing files migrate opportunistically, no big-bang rewrite). One authority instead of ~40 copies, and the next new test module cannot get the dance wrong.

## Impact

Every test module opens with the same ~8-line importlib.util `spec_from_file_location` boilerplate; a new module written with a plain import fails at discovery (hit live this sprint: `test_flow.py`'s first run died on 'No module named flow' and was rewritten to the incantation).

## Acceptance Criteria

- [ ] A shared `load_script` helper exists in the tests package and at least one test module uses it (the exemplar for future modules)
- [ ] Documentation (scripts/README or the tests module docstring) names it as the canonical way to import a script under test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
