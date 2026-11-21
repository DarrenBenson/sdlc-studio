# BG1681: BG1023 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_vitest_file_and_name.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/help/verify.md, changelog.d/BG1023.md
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T15:17:15Z

## Summary

BG1023 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The repair's cut at the first `--` (verify\_ac.py:2195, added in 67d57b45) is unpinned against the last: cutting at the last `--` instead passes every test in test\_verify\_ac\_vitest\_file\_and\_name.py, because each new `--` case holds one `--`, yet a line passing a `--` through, `jest a.test.ts -t name -- --ci -- extra`, builds `['jest', 'a.test.ts', '-t', 'name', '--', '--ci', '--', 'extra']` on the real code and `['jest', 'a.test.ts', '--', '--ci', '-t', 'name', '--', 'extra']` on the mutant, the round-1 defect again, where the runner reads `-t` and the name as operands and the criterion can pass without its named test\; the commit body names "the first `--`" and no test holds the word first; RULINGS: Round-1 "`_build_command` appends `-t <name>` after every other tail argument" CLOSED: the name now lands in front of the first `--`, and both the old order and the name just after `--` are killed by the new `-- --ci` and `-- --reporter=dot` cases. Round-1 "Two launcher branches in `_node_runner_argv` are unpinned" CLOSED: dropping the X\_OK guard is killed by the not-executable subtest, and a last fallback through npx is killed by the no-runner subtest, which asserts exit 127 naming the verb and never npx (its PATH-emptying patch is itself load-bearing: removing it fails the subtest). Round-1 "The `except ValueError` that keeps the jest batch cache from raising" CLOSED: re-raising is killed by the `jest <file> -t` cache case. Round-1 "Two literal-name details are unpinned" CLOSED: dropping the pipe and dropping the maxsplit are each killed. Claim inventory: the changelog's "the name goes in front of a `--` on the line, where the runner still reads `-t` as the name filter" and the commit body's five new-pin claims are TRUE by test and argv probe. AC1 and AC2 pass under `verify_ac.py run --id BG1023 --dry-run`. Reviewer mutants killed: the old order, the name just after `--`, a line with no `--` putting the name first, the X\_OK guard dropped, npx as the last fallback, the cache re-raising, the pipe dropped, the maxsplit dropped, the PATH binary passed over, the npx check skipped. The local runner path left un-absolutised survives but is equivalent through the CLI, since `--root`/`--repo-root` and the discovered root always reach run\_verifier resolved (sdlc\_md.resolve\_root), so it is no finding. A `-t name` written after `--` is moved in front of it, which reads the line's evident intent and is no finding.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1023 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1023 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The repair's cut at the first `--` (verify\_ac.py:2195, added in 67d57b45) is unpinned against the last: cutting at the last `--` instead passes every test in test\_verify\_ac\_vitest\_file\_and\_name.py, because each new `--` case holds one `--`, yet a line passing a `--` through, `jest a.test.ts -t name -- --ci -- extra`, builds `['jest', 'a.test.ts', '-t', 'name', '--', '--ci', '--', 'extra']` on the real code and `['jest', 'a.test.ts', '--', '--ci', '-t', 'name', '--', 'extra']` on the mutant, the round-1 defect again, where the runner reads `-t` and the name as operands and the criterion can pass without its named test; the commit body names "the first `--`" and no test holds the word first
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1023 AC1 still passes: `vitest <file> -t "name"` and `jest <file> -t "name"` pass the file as a positional argument and only the name to `-t`, invoking through the project's `node_modules/.bin` or npx when the bare binary is not on PATH
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_vitest_file_and_name.py::VitestFileAndNameTests::test_file_and_name_are_separate_arguments
- [ ] **AC3** BG1023 AC2 still passes: A regex metacharacter in a literal `-t` name is matched literally, or the Verify lint warns that `-t` takes a regex
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_vitest_file_and_name.py::VitestFileAndNameTests::test_a_metacharacter_in_the_name_is_literal_or_warned

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (run twenty-one orchestrator) | Fixed: BG1023 was reviewed again in round three under D0566 and its qa seat (Sam Eriksson) approved, closing the round-two findings this bug carried; BG1023 is Fixed |
