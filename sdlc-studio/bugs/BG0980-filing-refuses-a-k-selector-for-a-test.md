# BG0980: Filing refuses a `-k` selector for a test the fix will add to an existing module without naming the node-id form it would accept, so authors scatter one-test files

> **Status:** Open
> **Severity:** Low
> **Points:** 1
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

- [ ] **AC1** A `-k` selector that selects nothing in an existing module is refused with a message naming the node-id form (`<module>::<Class>::<test>`) as the way to name a test the fix will add there, and that node-id form of the same test is accepted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_selector_for_a_new_test.py::NewTestSelectorTests::test_the_k_refusal_names_the_node_id_route
- [ ] **AC2** A selector naming a near-miss of an existing test is still refused
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_selector_for_a_new_test.py -k near_miss_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
| 2026-10-21 | sdlc-studio | Retitled: was 'Filing refuses a Verify selector for a test the fix will add to an existing module, accepts the same selector into a new file, and judges neither without pytest' |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
