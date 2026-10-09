# BG1018: refine apply --question leaves the request ending on a blank line, which markdownlint refuses (MD012)

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_consult_section_lints.py, changelog.d/BG1018.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py
> **Evidence:** persona_resolve.py `consult` (~332-338); the D0355 mint of twelve requests.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T10:06:10Z

## Summary

`persona_resolve.consult` writes the `## Amigo Consult` section with `text.rstrip() + '\n\n' + section + '\n'`, and `section` already ends with a newline after its last question, so a request refined with `--question` ends in a blank line: markdownlint MD012 (multiple consecutive blank lines) on every such request, which the pre-commit markdown lane refuses. Reproduced on 2026-10-09 minting the D0355 breakdown: all twelve refined requests failed MD012 until the trailing blank line was stripped by hand.

## Steps to Reproduce

`refine.py apply --request <CR> --breakdown <file> --question q` on a request with no Amigo Consult section, then markdownlint the request -> MD012 at its last line.

## Proposed Fix

Join the section without the extra newline (one trailing newline at end of file), on both the append and the replace path.

## Acceptance Criteria

- [ ] **AC1** A request refined with `--question`, appended to or re-consulted, ends with exactly one newline and passes markdownlint
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_consult_section_lints.py::ConsultSectionTests::test_a_consulted_request_ends_with_one_newline

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
