# BG0692: gate.py never sets the boundary-suite marker itself, so SDLC_GATE_BOUNDARY=push reads [PASS] module-alone over a red boundary-only test

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/tests/test_boundary_marker.py, .githooks/pre-push, tools/run-suite.sh, AGENTS.md
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/BG0664-delivery-engineering.txt (engineering seat); verdicts/BG0664-delivery-qa.txt (qa seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md. The re-run line half was repaired in ef5b29e8; the environment route was re-read at HEAD (gate.py sets no SDLC_STUDIO_BOUNDARY_SUITE).
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`SDLC_STUDIO_BOUNDARY_SUITE`=1 is set only on the pre-push hook's own gate.py invocations. The refusal's re-run line has since been given the prefix, but the environment route to the same boundary, `SDLC_GATE_BOUNDARY`=push (gate.py:3703), still runs without it: with a red marked test the hook's invocation gives rc 1 with the test in the FAIL line, and the environment route gives rc 0 with [PASS] module-alone (probed by both seats). With the marker now in the gate environment, the advisory revert-check lane also runs any marked test a batch unit's Verify selector names, twice per unit, and that cost is not priced. AC1 priced two marked tests and there are now three (`test_cli_grammar.py`:707 was added later and runs the 83 s control twice); module-alone measured 661.6 s with the marker against 558.3 s without, still inside AC1's price. tools/tests/`test_boundary_marker.py` hand-parses the hook and the workflow YAML with regexes (_commands, `_sets_marker` and `_backed_runs`, lines 127-181), duplicating what tools/`boundary_roster.py` already reads, and fails a correct hook that exports the marker at top level; its AC2 check reads only the 'runs in FULL at ... -' phrase (line 204), so a second docstring sentence claiming close survives. Its docstring (line 48) says no hook invokes run-suite.sh, but .githooks/commit-msg:155 does, in --check mode. Pre-existing: .githooks/pre-push:11-12 and the AGENTS.md pre-push row still say the boundary gate runs 'the full suite', and tools/run-suite.sh:187 still names close among its callers (both left untouched per the unit's Revision History).

## Steps to Reproduce

1. In a throwaway copy, add a failing test marked boundary-only. 2. `SDLC_STUDIO_BOUNDARY_SUITE`=1 python3 .claude/skills/sdlc-studio/scripts/gate.py --boundary push - module-alone FAILS, naming the test. 3. `SDLC_GATE_BOUNDARY`=push python3 .claude/skills/sdlc-studio/scripts/gate.py - [PASS] module-alone, rc 0. 4. Move the marker export in .githooks/pre-push to the script's top level and run tools/tests/`test_boundary_marker.py` - it fails on a hook that sets the marker for both invocations.

## Proposed Fix

Have gate.py export `SDLC_STUDIO_BOUNDARY_SUITE`=1 into the lanes' environment whenever it resolves a push or release boundary, by flag or by `SDLC_GATE_BOUNDARY`, so every route to the boundary runs the marked tests. Price the marked tests in revert-check or have that lane skip them. Rewrite `test_boundary_marker.py` over tools/`boundary_roster.py`'s reader so it judges what the hook does rather than how it is spelt. Correct its line-48 docstring, the 'full suite' wording in the hook header and AGENTS.md, and run-suite.sh's list of callers.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `SDLC_STUDIO_BOUNDARY_SUITE`=1 is set only on the pre-push hook's own gate.py invocations.
- [ ] **AC2** The proposed fix lands, pinned by a test: Have gate.py export `SDLC_STUDIO_BOUNDARY_SUITE`=1 into the lanes' environment whenever it resolves a push or release boundary, by flag or by...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
