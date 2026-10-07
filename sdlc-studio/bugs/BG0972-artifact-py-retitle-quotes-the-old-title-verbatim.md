# BG0972: `artifact.py retitle` quotes the old title verbatim in its revision row, so a retitle made to remove an em dash or a bare identifier puts it straight back

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_retitle_revision_row.py, changelog.d/BG0972.md
> **Evidence:** Found 2026-10-06/07 during the triage session that filed BG0955-BG0963 in this repository. BG0952 and BG0955 retitles.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:37:20Z

## Summary

`retitle` appends `Retitled: was '<old title>'` to the Revision History (artifact.py:2203). When the title was changed precisely because it broke a house rule, the row reintroduces the offence: BG0952 was retitled to drop an em dash and the row re-added it, so `tools/lint-style.sh` still failed; BG0955 was retitled to code-span `test_lean_backlog_sweep` and `_index.md` and the row re-added them bare, so markdownlint MD037 still failed. Both needed a hand edit of the row the tool wrote.

## Steps to Reproduce

File an artefact whose title holds an em dash; `artifact.py retitle --id <id> --title '<the same without it>'`; run `tools/lint-style.sh` -> it fails on the new revision row.

## Proposed Fix

Write the old title into the row in a form that passes the same lanes as a title: code-spanned and with an em dash spelled U+2014, or record only that the title changed and leave the old text to git history.

## Acceptance Criteria

- [ ] **AC1** Retitling an artefact whose old title holds an em dash leaves a file that passes the house-style check
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_revision_row.py -k retitle_row_passes_house_style
- [ ] **AC2** Retitling one whose old title holds a bare `snake_case` identifier leaves a file markdownlint passes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_revision_row.py -k retitle_row_passes_markdownlint

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
