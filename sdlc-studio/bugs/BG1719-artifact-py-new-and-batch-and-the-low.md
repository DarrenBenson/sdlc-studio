# BG1719: artifact.py new and batch, and the Low-finding consolidator, write a title's bare snake_case identifier into the H1 and the index row, so markdownlint refuses the file

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/triage_noise.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py, changelog.d/BG1719.md
> **Evidence:** Found by the run twenty-three FFA builder while fixing BG0974: artifact.py new and batch still write the title bare around artifact.py:537, and triage_noise.consolidate_low_finding writes it unsafed.
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T05:31:36Z

## Summary

BG0974 makes `file_finding.py` markdown-safe the title it writes, but the other two paths that write an artefact title do not: artifact.py new and artifact.py batch write the title bare into the H1 and the index row (around artifact.py:537), and `triage_noise.consolidate_low_finding` writes the consolidated finding's title unsafed. A title such as `test_x reads only the live _index.md` reads as emphasis there, and the commit's markdown lane refuses the new file with MD037.

## Steps to Reproduce

1. Run artifact.py new --type bug with a title holding `test_x` and `_index.md` bare. 2. Run markdownlint over the new file and bugs/_index.md. 3. Observe MD037 on the H1 and the index row.

## Proposed Fix

Route the title through the same markdown-safing `file_finding.py` now applies to its own title (BG0974), in artifact.py's minimal and full-template renderers and in the batch path, and in `triage_noise.consolidate_low_finding.`

## Acceptance Criteria

- [ ] **AC1** Given a title holding two bare identifiers that begin or contain underscores, when artifact.py new and artifact.py batch create a bug from it, then the new file and the index row pass markdownlint and each identifier sits inside a code span. Fails on: MD037 on the H1 or the row.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py -k title_identifier_is_markdown_safe
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given Low findings the consolidator merges under such a title, when `consolidate_low_finding` writes the consolidated artefact, then its file and index row pass markdownlint. Fails on: MD037 on either.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py -k consolidated_title_is_markdown_safe
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
