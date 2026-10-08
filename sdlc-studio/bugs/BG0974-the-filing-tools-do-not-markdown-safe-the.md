# BG0974: The filing tools do not markdown-safe the title or the Evidence line, so a bare snake_case identifier fails MD037 at commit or in CI

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py, changelog.d/BG0974.md
> **Evidence:** Found 2026-10-06/07 during the triage session that filed BG0955-BG0963 in this repository. BG0955 title, BG0959 Evidence line.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:37:32Z

## Summary

`file_finding.py` markdown-safes the summary, steps, fix, recommendation and impact (`file_finding.py`:2011), but not the title, which becomes the H1 and the index row, nor the Evidence line. An identifier such as `test_lean_backlog_sweep` or `_mode_and_cutoff` written bare there reads as emphasis, and markdownlint MD037 refuses the file: BG0955's H1 and index row, and BG0959's Evidence line, both filed on 2026-10-06/07. A clone without markdownlint commits it cleanly, so the failure surfaces later, often to a different session.

## Steps to Reproduce

`file_finding.py file --type bug --title 'test_x reads only the live _index.md' ...`; `markdownlint` the new file and `bugs/_index.md` -> MD037.

## Proposed Fix

Apply the same markdown-safing to the title and the Evidence value as to the prose fields, so an identifier with underscores is code-spanned or escaped in the H1, the index row and the Evidence line.

## Acceptance Criteria

- [ ] **AC1** A finding titled with a bare `snake_case` identifier is written so that markdownlint passes its H1 and its index row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py -k title_identifier_passes_markdownlint
- [ ] **AC2** An Evidence value holding such an identifier passes markdownlint too, and its text still reads the same
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py -k evidence_identifier_passes_markdownlint

## Further evidence

- 2026-10-08: BG0991 was filed with code spans ending in a space (`##` and `**Verify:**` each followed by one), which markdownlint refuses (MD038); fixed at triage.

## Related

- BG0967 is the opposite failure in the same safing: the filer back-ticks identifiers inside Steps to Reproduce and corrupts the shell commands there. Fix the two together, so the title and Evidence are safed and the Steps are left runnable.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
