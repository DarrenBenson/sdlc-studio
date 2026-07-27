# BG0301: shell-hazard fingerprint false-positives on aligned code-block spacing: a two-space gap in a code excerpt reads as a collapsed command substitution

> **Status:** Fixed
> **Verification depth:** functional
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py
> **Severity:** Low
> **Points:** 2

## Summary

The shell-hazard fingerprints in `file_finding.py` (around line 481) over-flag legitimate technical prose in an artefact field. Two false positives were hit filing THIS very report and are worth listing because they are self-demonstrating:

- the collapsed-double-space rule flags any run of two spaces between non-space characters; that spacing is normal in a quoted code excerpt (column-aligned file-and-line references, a comment offset from a statement by two spaces).
- the unbalanced-backtick rule flags a field with an odd number of backtick characters; a markdown fenced-code marker (three backticks) or a lone backtick in prose is odd, though it is not a shell substitution.

The catch-rate test (`test_shell_hazard_rate.py`, `MeasuredCatchRateTests`) asserts ZERO false positives across all artefact fields, and it scans the working tree not the diff, so one such artefact turns the whole suite and every committer's commit gate red until the prose is reworded. It happened live this session: a parallel session's legitimately-authored bug carried a code excerpt whose alignment tripped the double-space rule, blocking the gate tree-wide.

## Steps to Reproduce

1. File any bug or CR whose body has a quoted code excerpt with two spaces between tokens (column alignment), or any field with an odd backtick count (a fenced-code marker, a lone backtick).
2. Run `python3 -m unittest test_shell_hazard_rate.MeasuredCatchRateTests.test_no_legitimate_artefact_field_is_flagged`.
3. Observe the artefact flagged as a false positive; the suite and the commit gate go red for everyone until the prose is changed. This report itself had to be written avoiding both patterns.

## Proposed Fix

Exempt code context from these fingerprints, or require a stronger signal than a bare two-space gap or an odd backtick count. The real hazard is a value shaped like a shell command with a collapsed substitution, not any aligned code or any markdown inline-code or fence. Skip fenced and indented code blocks when scanning a field, and judge the double-space and backtick rules only against text that reads as a command. Add a regression fixture with a benign aligned code excerpt and a fenced block to the catch-rate test so the exemption stays.

## Acceptance Criteria

### AC1: a fenced or indented code block in a field is not scanned for shell hazards

- **Given** an artefact field whose only hazard-shaped content sits inside a fenced code block
  (column-aligned gaps of two spaces, and fence markers that make the backtick count odd)
- **When** the shell-hazard scan runs over that field
- **Then** it reports nothing - a code illustration is exempt, because its spacing and markers are
  not the marks of a shell that ate a command-shaped argument
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py::CodeBlockExemptionTests::test_fenced_and_indented_blocks_are_not_flagged

### AC2: the exemption does not blind the detector to a real corruption

- **Given** the recorded corpus of values a completed command substitution genuinely corrupted
- **When** the scan runs after the code-block exemption is added
- **Then** it still catches the same count it did before - the exemption removes false positives
  without lowering the true-positive rate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py::MeasuredCatchRateTests::test_the_catch_count_over_the_corpus_is_asserted_as_a_number

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
