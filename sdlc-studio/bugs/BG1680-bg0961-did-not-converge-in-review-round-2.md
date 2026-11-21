# BG1680: BG0961 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/reference-verify.md, changelog.d/BG0961.md
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T15:16:56Z

## Summary

BG0961 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The repair's backslash guard in the merged single-quote and ANSI-C branch is unpinned: widening `if ch == "\" and state == "ansi":` (verify\_ac.py:837) to any backslash, so a backslash inside single quotes escapes the closing quote, passes every HardeningTests case, yet through run\_verifier `shell grep -qF '\' <skill>/scripts/verify_ac.py` and `shell test 'a\' = "a\" && test -f <skill>/scripts/verify_ac.py` pass on the real code and fail on the mutant with `skill: No such file or directory`\; no test puts a backslash before a closing single quote, the one place the two literal states now sharing a branch differ; BLOCKING: [new] The repair's `state != "dq"` guard on ANSI-C quoting (verify\_ac.py:859) is unpinned on its `$(...)` side: narrowing it to `state == "code"` passes every HardeningTests case, because each ANSI-C case in test\_a\_skill\_path\_with\_a\_space\_is\_quoted sits at the top level or inside double quotes, yet `shell test "$(echo $'a\'b')" = "a'b" && test -f <skill>/scripts/verify_ac.py` over a skill directory named `my skill` passes through run\_verifier on the real code and fails on the mutant with `binary operator expected`, the round-1 ANSI-C defect again one level down, inside the substitution the docstring says opens a fresh context; RULINGS: Round-1 "The closing single quote in `_expand_skill_placeholder` is unpinned" CLOSED: the sq-never-closes mutant is killed by the new `grep -q 'marker'` case, and the round-1 shape `shell grep -q 'def' <skill>/scripts/verify_ac.py` passes through run\_verifier over `my skill's`. Round-1 "The double-quoted escape set at verify\_ac.py:827 is unpinned" CLOSED: dropping the double quote, the backslash or the backtick from the class is each killed by the new skill directory name. Round-1 "The nested-parenthesis branch at verify\_ac.py:861 is unpinned" CLOSED: deleting it is killed, and the round-1 shape passes through run\_verifier. Round-1 "The docstring (verify\_ac.py:818-824) and reference-verify.md say the placeholder behaves as a shell variable would" CLOSED at the top level: `shell test $'a\'b' = "a'b" && test -f <skill>/scripts/verify_ac.py` now passes through run\_verifier (and fails against a missing script), and the docstring, reference-verify.md and changelog no longer claim shell-variable behaviour, but the new ANSI-C branch carries the two unpinned guards above. Claim inventory: the commit body's and changelog's "an escaped quote does not end the string", "inside double quotes `$'` is not ANSI-C" and "backticks are not tracked" are TRUE by test and probe. AC1-AC3 pass under `verify_ac.py run --id BG0961 --dry-run`. Reviewer mutants killed: sq never closes, the three escape-set drops, nested parenthesis deleted, ANSI-C never closes, ANSI-C backslash escapes nothing, ANSI-C opened inside double quotes, ANSI-C read as single quotes, `)` inside `$(...)` never pops. Survivors re-run alone, each one change, with the behaviour difference shown through run\_verifier on /bin/sh (bash here). Under D0561 each fix is a test per shape above, inside the unit.

## Steps to Reproduce

1. Read the round 2 REJECT of BG0961 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0961 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The repair's backslash guard in the merged single-quote and ANSI-C branch is unpinned: widening `if ch == "\" and state == "ansi":` (verify\_ac.py:837) to any backslash, so a backslash inside single quotes escapes the closing quote, passes every HardeningTests case, yet through run\_verifier `shell grep -qF '\' <skill>/scripts/verify_ac.py` and `shell test 'a\' = "a\" && test -f <skill>/scripts/verify_ac.py` pass on the real code and fail on the mutant with `skill: No such file or directory`; no test puts a backslash before a closing single quote, the one place the two literal states now sharing a branch differ
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: BLOCKING: [new] The repair's `state != "dq"` guard on ANSI-C quoting (verify\_ac.py:859) is unpinned on its `$(...)` side: narrowing it to `state == "code"` passes every HardeningTests case, because each ANSI-C case in test\_a\_skill\_path\_with\_a\_space\_is\_quoted sits at the top level or inside double quotes, yet `shell test "$(echo $'a\'b')" = "a'b" && test -f <skill>/scripts/verify_ac.py` over a skill directory named `my skill` passes through run\_verifier on the real code and fails on the mutant with `binary operator expected`, the round-1 ANSI-C defect again one level down, inside the substitution the docstring says opens a fresh context
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG0961 AC1 still passes: A shell verifier that checks the skill's `verify_ac.py` via the skill placeholder passes when `verify_ac` runs it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::HardeningTests::test_run_verifier_shell_pass_and_fail_resolves_the_skill_placeholder
- [ ] **AC4** BG0961 AC2 still passes: After `verify_ac.py run` stamps such a criterion Verified, its Verify line still reads the placeholder; no absolute install path is written into the artefact
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::HardeningTests::test_the_placeholder_is_never_written_back
- [ ] **AC5** BG0961 AC3 still passes: A skill directory whose path holds a space is substituted quoted, so the shell sees one argument; a check that should fail still fails
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::HardeningTests::test_a_skill_path_with_a_space_is_quoted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (run twenty-one orchestrator) | Fixed: BG0961 was reviewed again in round three under D0565 and its qa seat (Sam Eriksson) approved, closing the round-two findings this bug carried; BG0961 is Fixed |
