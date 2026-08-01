# BG0475: decisions.py writes a multi-paragraph rationale straight into a markdown table cell, breaking the row

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-01T08:00:52Z

## Summary

`decisions.py add` and `waive` store the rationale as one cell of a pipe table. A rationale containing newlines - which a `--fields-file` document makes natural, and which a considered decision usually needs - is written verbatim, so the row ends mid-cell and the following paragraphs become stray body text. The table is then malformed: markdownlint reports MD055 (missing trailing pipe) and MD056 (3 cells where 6 are expected), and the commit gate refuses.

Hit while recording D0106. The decision is readable through `decisions.py list` because the reader tolerates it, so nothing warns at write time - the failure surfaces later as a markdown lint error naming a line number rather than the command that produced it.

## Steps to Reproduce

1. Write a fields-file whose rationale contains a blank line between paragraphs.
2. python3 .claude/skills/sdlc-studio/scripts/decisions.py add --fields-file <that> --status accepted -> succeeds, reports the new D-id.
3. npx markdownlint sdlc-studio/decisions.md -> MD055 and MD056 on the row just written.
4. The commit gate's markdown lane then refuses the commit.

## Proposed Fix

Collapse newlines to spaces when writing the cell, or escape them as `<br>`, at the point the row is composed. The writer knows it is building a table cell; every caller does not. Refusing a multi-line rationale would be worse - the reason a decision is worth recording is usually longer than one line.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `decisions.py add` and `waive` store the rationale as one cell of a pipe table.
- [ ] The proposed fix lands, pinned by a test: Collapse newlines to spaces when writing the cell, or escape them as `<br>`, at the point the row is composed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Filed |
