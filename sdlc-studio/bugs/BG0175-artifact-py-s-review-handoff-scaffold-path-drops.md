# BG0175: artifact.py's review/handoff scaffold path drops --author: literal {{author}} in the revision row and no Raised-by stamp, unlike every other type

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; dogfood retro 2026-07-16

## Summary

artifact.py has two render paths that disagree on what authorship means (LL0016). The main _render path stamps '> **Raised-by:**' from --author and writes the real name into the revision row via `file_finding.rev_row.` The review scaffold fallback (~line 554) builds its own header with no Raised-by line and hard-writes a literal '{{author}}' placeholder into the revision row - even when --author was explicitly passed. Observed live 2026-07-16: 'artifact.py new --type review --author "Darren Benson; human; ..."' produced RV0009 with 'Created-by: sdlc-studio new', no Raised-by, and '| 2026-07-16 | {{author}} | Created via new |' - the operator's authorship of record silently discarded on the one artefact type that records sign-offs.

## Steps to Reproduce

1. python3 scripts/artifact.py new --type review --title x --author 'Name; human; v1'. 2. Open the created RV file. 3. No Raised-by header; revision row Author cell is the literal {{author}}.

## Proposed Fix

Route the review/handoff scaffold through the same head/`rev_row` writers as _render (one authority for authorship), or at minimum substitute {{author}} from the resolved --author and stamp Raised-by.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Filed |
