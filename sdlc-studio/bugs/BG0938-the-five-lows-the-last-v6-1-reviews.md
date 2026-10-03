# BG0938: The five lows the last v6.1 reviews raised (D0334)

> **Status:** In Progress
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/sprint.py, tools/tests/test_lean_install_ps1_default.py, tools/tests/test_lean_docs_v61.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_last_lows.py, CHANGELOG.md, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T15:43:34Z

## Summary

Raised by the last v6.1 reviews and ruled fixed before the tag (D0334): (1) changelog compose's pin covers a #### block only in the last section, so a missing blank line after a block followed by another ### heading passes (changelog.py ~238); (2) two fragments each carrying a #### Retired flags table in one section cut to sibling duplicate headings (MD024); (3) a TRD .local row whose writer cell reads 'mutation.py run' passes US0984's specifications test; (4) the no-pwsh source-read arm of the install.ps1 test passes three broken defaults - assert the fetched tag is what is installed; (5) a goal-review seats value that is a string or object is iterated, so the refusal names a character or key; and the note parser is quadratic on a whitespace-free run of repeated measure names.

## Steps to Reproduce

Each is reproduced in the v6.1 review verdicts for BG0929, US0984, BG0934 and BG0936.

## Proposed Fix

Pin and fix each as named; merge duplicate #### headings in one section; refuse a non-list seats value by naming it; make the parser linear on that input. No new gate.

## Acceptance Criteria

- [ ] **AC1** Given a cut with a #### block in a section that a later ### heading follows, and two fragments carrying #### Retired flags in one section, when the changelog is cut, then it lints clean with one merged heading. Fails on: the missing-blank-line mutant and the current duplicate headings
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_last_lows.py::V61LastLowsTests::test_the_cut_places_every_hash4_block_cleanly
  - **Verified:** yes (2026-10-03)
- [ ] **AC2** Given a goal-review fields file whose seats value is a string or an object, when record refuses it, then the message says seats must be a list. Fails on: the current refusal naming a character or key
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_last_lows.py::V61LastLowsTests::test_a_non_list_seats_value_is_named
  - **Verified:** yes (2026-10-03)
- [ ] **AC3** Given a goal note of 20,000 characters made of repeated measure names with no whitespace, when the close checks it, then it finishes in well under a second. Fails on: the current quadratic scan
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_last_lows.py::V61LastLowsTests::test_the_note_parser_is_linear_on_repeated_names
  - **Verified:** yes (2026-10-03)
- [ ] **AC4** Given the TRD's .local table, a row whose writer cell names a retired script command such as 'mutation.py run' fails the specifications test, and the install.ps1 source-read arm fails when the fetched tag is discarded. Fails on: the current tests, which pass both
  - **Verify:** pytest tools/tests/test_lean_docs_v61.py tools/tests/test_lean_install_ps1_default.py
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
