# BG0980: Filing refuses a Verify selector for a test the fix will add to an existing module, accepts the same selector into a new file, and judges neither without pytest

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_filing_selector_for_a_new_test.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, changelog.d/BG0980.md
> **Evidence:** Found 2026-10-07 filing this session's frictions; BG0955 filed 2026-10-06 without pytest installed.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:38:17Z

## Summary

`file_finding.py` refuses a `Verify:` selector that names no existing test, to catch a real test named wrongly. But a bug is filed before its fix, so its regression test does not exist yet. The check refuses `pytest <existing module> -k <new name>` and `<existing module>::<NewClass>::<test>`, accepts the same test placed in a module that does not exist yet ('a file the unit CREATES is fine'), and skips the judgement entirely when pytest is not installed. On 2026-10-07 seven findings were refused for naming new tests in existing modules and had to be re-pointed at seven new single-purpose files; BG0955's selectors into an existing module had been accepted the day before, on the same tree, because pytest was not yet installed. The rule as applied rewards scattering one-test files and gives a different verdict on different machines.

## Steps to Reproduce

With pytest installed, file a bug whose verify is `pytest <an existing test module> -k a_test_not_yet_written` -> refused; change the path to a new module name -> accepted; uninstall pytest and retry the first -> accepted.

## Proposed Fix

Judge a selector the same way whatever is installed, and treat a test the unit will add to an existing module as the creates-a-file case is treated: accept it when the unit's Affects names that module, and keep the refusal for a selector whose module is not in Affects or whose name is close to an existing test (the typo the check exists for).

## Acceptance Criteria

- [ ] **AC1** A selector naming a new test in an existing module listed in the unit's Affects is accepted at filing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_selector_for_a_new_test.py -k new_test_in_an_affected_module_is_accepted
- [ ] **AC2** A selector naming a near-miss of an existing test is still refused
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_selector_for_a_new_test.py -k near_miss_is_refused
- [ ] **AC3** The verdict is the same with and without pytest installed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_selector_for_a_new_test.py -k verdict_does_not_depend_on_pytest

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
