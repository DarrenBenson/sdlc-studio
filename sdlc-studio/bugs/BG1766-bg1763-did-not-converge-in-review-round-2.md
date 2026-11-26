# BG1766: BG1763 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1763.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M89MN1 - raised during the run, 2026-11-26T02:52:48Z

## Summary

BG1763 was rejected at round 2, the review cap, by agent-aa341c5c62633f048 (product), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the new `runner_can_run` counts the dots in the file's name rather than its whole path, and no test pins that (critic.py:3915-3922, test\_critic.py:4554): every runnable fixture path (`tests/test_widget.py`, `tests/widget_test.py`) has no dot outside its file name, so a mutant that counts the dots over the whole path (`test_file.count(".") == 1` in place of `name.count(".") == 1`), applied in a detached worktree, passes NonPytestSelfCheckTests (5 passed) and every module that reads the self-check or the hand-in list (19 modules, 89 and 367 passed). Rendered through `sprint.py lane brief` under that mutant, a pytest unit whose tests sit under a dotted directory, such as this repository's own `.claude/skills/...` layout or `tests/v1.2/test_a.py`, loses its runner command, selector and report and is sent by hand (at 76d14ad76: runner 1, by hand 0\; under the mutant: runner 0, by hand 1), with the suite still green. The docstring, the changelog and the commit message all say "whose name holds no other dot", so this is the unit's own claim. One runnable fixture under a dotted directory in the positive control would pin it [LC-002]; RULINGS: Round one, "the hand-run route's promise to every project whose tests pytest cannot run is pinned only on the JS family": CLOSED. The Go (US0104), dotted `.spec.py` (US0105) and Rust (US0106) units now pin it. My round-one JS allowlist and `.test`/`.spec` name-rule mutants, re-applied to the new `by_hand` line, are killed (4 failed and 2 failed), and a Go unit's lane brief at 76d14ad76 names no selector, runner command or report. Round one's pre-existing note on the hand-in list: CLOSED in this round, now that sprint.py is in Affects. The vitest fixture's hand-in list names no `mutation-edits.json`, hands in only the mutants file, recorded through --mutants, and accepts a test by its path or as `path::name`. The mixed (US0303) and dotted-directory pytest (US0308) units' hand-in lists match the base byte for byte. AC1 is met: verify\_ac dry-run pass=1, and the vitest lane brief holds no "pytest selector". From the product seat, a vitest, Go or dotted `.spec.py` builder now reads one route from step 2 through the hand-in list. Claim inventory, every claim TRUE: pytest's default import of `tests/widget.spec.py` exits 2 with "No module named 'widget'", `--import-mode=importlib` runs it (hence "by default"), and a named `.go` or `.ts` file gives "no tests ran", exit 4. "A pytest unit's brief is unchanged" holds for conventionally named tests, and the changelog states the dotted-name exception. 17 modules (440 tests) pass at 76d14ad76. The author's M1-M16 replayed killed. My Q1, Q2 and Q4 (the sprint hand-in reading any `.py` as runnable) were killed. Q3 above survived and was re-tested in isolation on the dotted-directory units.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1763 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1763 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the new `runner_can_run` counts the dots in the file's name rather than its whole path, and no test pins that (critic.py:3915-3922, test\_critic.py:4554): every runnable fixture path (`tests/test_widget.py`, `tests/widget_test.py`) has no dot outside its file name, so a mutant that counts the dots over the whole path (`test_file.count(".") == 1` in place of `name.count(".") == 1`), applied in a detached worktree, passes NonPytestSelfCheckTests (5 passed) and every module that reads the self-check or the hand-in list (19 modules, 89 and 367 passed). Rendered through `sprint.py lane brief` under that mutant, a pytest unit whose tests sit under a dotted directory, such as this repository's own `.claude/skills/...` layout or `tests/v1.2/test_a.py`, loses its runner command, selector and report and is sent by hand (at 76d14ad76: runner 1, by hand 0; under the mutant: runner 0, by hand 1), with the suite still green. The docstring, the changelog and the commit message all say "whose name holds no other dot", so this is the unit's own claim. One runnable fixture under a dotted directory in the positive control would pin it [LC-002]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1763 AC1 still passes: Given a unit whose Affects test files are vitest and whose criteria name no pytest selector, then its lane brief does not ask for a pytest selector: it names a runner that can run the unit's tests, or the hand-run MUTANTS.json route. Fails on: "its test a pytest selector" in that brief.
  - **Verify:** shell python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_critic.py::NonPytestSelfCheckTests::test_a_vitest_unit_is_not_asked_for_a_pytest_selector

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Filed |
