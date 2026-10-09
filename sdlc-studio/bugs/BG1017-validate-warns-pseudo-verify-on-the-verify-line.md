# BG1017: validate warns pseudo-verify on the Verify line a request's own writers put beneath each criterion

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate_request_verify_line.py, changelog.d/BG1017.md, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Evidence:** Found by the G9 breakdown of CR0618 and its panel review (D0355); validate.py:390 and :401, file_finding.py:1426.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T10:05:22Z

## Summary

Since US0970 (2026-10-01), `file_finding.py file --type cr` and `artifact.py new --type cr` write each `verify` entry as a `- **Verify:** <selector>` line beneath its criterion (`checklist_block`, `file_finding.py`:1426), and the filer warns when a criterion has none. `validate.py check` then warns pseudo-verify on exactly that line and advises 'Restate it as the observable outcome' (validate.py:401), because `file_finding.scan_prose_acs` judges every line of the criteria section. The lane's comment, 'The creators REFUSE to write one' (validate.py:390), has been false since US0970. The filer's own refusal (`check_prose_acs`) judges only the criterion's prose, so the validator should judge the same: skip the lines `file_finding.criteria_blocks` reads as a criterion's Verify line (added by the first CR0618 story), keep warning on a command written into the criterion's text, and point the advice at a `- **Verify:**` line beneath the criterion, which refine carries to the story. Depends on US1025 (the CR0618 story whose parser it reuses).

## Steps to Reproduce

File a CR with a `verify` entry under a criterion; `validate.py check` warns pseudo-verify on that Verify line and advises restating it.

## Proposed Fix

Judge only a criterion's prose, as the filer's own `check_prose_acs` does, skipping the Verify line beneath it.

## Acceptance Criteria

- [ ] **AC1** Given a CR filed by `file_finding.py file --type cr` with a `verify` entry, and a CR whose criterion prose ends `Verify: rg -qi effort sprint.py`, when `validate.py check --file` runs on each, then the first draws no pseudo-verify warning and the second does, advising a `- **Verify:**` line beneath the criterion. Fails on: `scan_prose_acs` judging every line of the section (today), or an exemption keyed on the word Verify rather than the parsed block.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_request_verify_line.py::RequestVerifyLineTests::test_only_a_command_in_criterion_prose_is_warned

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
