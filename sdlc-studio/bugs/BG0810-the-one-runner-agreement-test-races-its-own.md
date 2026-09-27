# BG0810: The one-runner agreement test races its own fixture: two worker processes share one template directory

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/tests/test_lean_one_runner.py, changelog.d/BG0810.md
> **Evidence:** pre-push gate 2026-09-27 ~21:00, sdlc-studio/.local/boundary-suite-last.log: push full-suite FAIL on tools/tests/test_a_importer.py::ImporterTests::test_uses_the_template in the fixture; CI command green on the same fixture
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-27T19:28:57Z

## Summary

`tools/tests/test_lean_one_runner.py::OneRunnerTests::test_ci_and_push_agree_on_a_shared_global_fixture` builds BG0770's pair in a temp project. The gate module keeps `ROOT / "shared-template"` and its module teardown deletes it. Under the push's full-suite lane the two modules run in separate xdist workers but share that directory, so one worker's teardown can delete it while the importer is still asserting it exists. The push then reads red where CI reads green, and the test fails on scheduling alone. Seen three times on 2026-09-27 while other suites ran: twice in reviewers' full suites, and once in the pre-push gate, which refused the push (full-suite 1 red, 7619 passed).

## Steps to Reproduce

Run `bash tools/skill-tests.sh` (or any full suite) while `python3 -m pytest tools/tests/test_lean_one_runner.py` runs; under load the push verdict flips to red.

## Proposed Fix

Key the fixture's template directory to the process (`ROOT / f"shared-template-{os.getpid()}"`), so the module-global sharing that BG0770 is about stays inside one process (the unittest control still splits) while two worker processes no longer delete each other's directory.

## Acceptance Criteria

- [ ] **AC1** Given the fixture's gate module, when two worker processes each run one of the pair's modules, then neither process's teardown removes the other's template, and the push lane reads green. Fails on: a template path shared across processes (HEAD), where a teardown in one worker deletes the directory the importer in the other is asserting
  - **Verify:** pytest tools/tests/test_lean_one_runner.py::OneRunnerTests::test_the_template_is_private_to_its_process
  - **Verified:** yes (2026-09-27)
- [ ] **AC2** Given the same pair run by `unittest discover` in one process, then it is still red, so the control that CI's old command splits the pair still holds. Fails on: a per-test template that removes the module-global sharing itself
  - **Verify:** pytest tools/tests/test_lean_one_runner.py::OneRunnerTests::test_ci_and_push_agree_on_a_shared_global_fixture
  - **Verified:** yes (2026-09-27)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
