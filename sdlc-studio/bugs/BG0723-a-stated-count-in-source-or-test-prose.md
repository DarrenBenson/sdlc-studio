# BG0723: a stated count in source or test prose is never checked against the tree it counts

> **Status:** Won't Fix
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/check_spec_claims.py, tools/tests/test_check_spec_claims.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, tools/tests/test_check_versions.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0463 claims 2, 3, 4, 13 and 14, re-executed against HEAD on 2026-09-21 and all still true. They are one defect with one remedy: a number or a location stated in prose, never joined to the thing it describes. US0460 says the tools/tests module count is `33 today`; it is 73. A test docstring says `close` runs seven steps; `_CLOSE_CHAIN` has ten. sprint.py says in two places that three of the chain's steps exist to do something, while `DRY_RUN_ACTION_STEPS` is now the whole chain, so `three` describes nothing. A test module's docstring gives a run command whose discover root collects none of its tests. Three tools/tests files carry a `six parents up` comment over `parents[1]`.

## Steps to Reproduce

1. `ls tools/tests/test_*.py | wc -l` -> 73; read US0460's AC4 Given -> `33 today`. 2. `python3 -c "import sprint; print(len(sprint._CLOSE_CHAIN))"` -> 10; grep `test_sprint.py` for `seven steps`. 3. Read sprint.py's two `three of the chain's steps` sentences beside `DRY_RUN_ACTION_STEPS = tuple(_CLOSE_CHAIN)`. 4. Run the command in tools/tests/`test_check_versions.py`'s docstring - it collects zero tests.

## Proposed Fix

Fix the five instances, then gate the class: `check_spec_claims` already knows how to join a stated census to a measured one, so extend it to numbers stated in PYTHON docstrings and comments, not only in markdown. The counts that matter are derivable - module counts from the directory, chain lengths from the tuple - so the durable remedy is to derive them in the text or to fail when a literal disagrees. Pin with a fixture stating a count the tree contradicts.

## Acceptance Criteria

### AC1: a count stated in source or test prose is checked against the thing it counts

- **Given** the five instances at HEAD - US0460's `33 today` against 73 modules, a docstring's `seven steps` against a ten-entry chain, sprint.py's two `three of the chain's steps` sentences beside a whole-chain tuple, a docstring whose discover root collects none of its tests, and a `six parents up` comment over `parents[1]` in three files
- **When** the guard runs over the tree
- **Then** each is reported with the stated figure and the measured one beside it, and each is corrected; a count that is derivable is derived in the text rather than restated
- **Mutant:** in `tools/check_spec_claims.py`, keep the census join to markdown only - every one of these five lives in Python source or a docstring, so the guard that exists for exactly this class cannot see any of them
- **Verify:** pytest tools/tests/test_check_spec_claims.py::PythonProseCensusTests::test_a_stated_count_in_python_prose_is_joined_to_its_census

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - [+constraint] check stated counts in prose against the tree: new check |
