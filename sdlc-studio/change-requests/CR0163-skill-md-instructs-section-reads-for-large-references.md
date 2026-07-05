# CR-0163: SKILL.md instructs section reads for large references (honour the Reading Guides)

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-05
> **Created-by:** sdlc-studio file

## Summary

The big three references (epic 1069, story 1036, code 939 lines) carry Reading Guides but nothing instructs the agent to honour them, so the default is an 8-10k-token whole-file read for single-section flows. Add one rule to SKILL.md: for a reference over ~400 lines, read the Reading Guide first and load only the named section; verify the big-3 guides name greppable headings.

## Acceptance Criteria

- [ ] SKILL.md carries the slice-read rule in Instructions and the Progressive Loading Guide
- [ ] reference-epic/story/code Reading Guides name headings that exist verbatim in the file

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-05 | audit | Raised |
