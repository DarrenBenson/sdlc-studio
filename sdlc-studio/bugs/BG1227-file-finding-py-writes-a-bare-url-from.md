# BG1227: file_finding.py writes a bare URL from a finding's prose, so the filing's own commit is refused by the markdown lane

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding_bare_url.py, changelog.d/BG1227.md, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** BG1225's paperwork commit, refused by the markdown lane on 2026-11-05.
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T11:07:55Z

## Summary

2026-11-05, run six. A finding whose steps name an http URL is written to the bug file unchanged, and markdownlint's MD034 (no bare URLs) then refuses the commit that carries it. It happened at BG1225 and twice in run five, each time costing a refused commit and a hand edit.

## Steps to Reproduce

1. File a bug whose steps contain `http://127.0.0.1:8080` in plain prose.
2. Commit the filing: the markdown lane refuses MD034.

## Proposed Fix

Wrap a bare http or https URL in backticks when the filer renders prose fields, or refuse the filing naming the field, so the file it writes always passes the lint the commit runs.

## Acceptance Criteria

- [ ] **AC1** A finding whose prose holds a bare http URL is written so markdownlint's MD034 passes on the filed file, and a URL already in backticks is left as it is.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_bare_url.py
  - **Verified:** yes (2026-11-05)

## Impact

Each occurrence costs a refused commit and a hand edit in the orchestrator's context.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
