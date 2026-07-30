# BG0426: the epic story census could not read the linked Epic field the shipped template writes, and a wrong count was committed

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, tools/tests/test_epic_index_derived.py, sdlc-studio/epics/_index.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** Found by an independent adversarial review of US0477/US0478, which the operator asked for after the units were already delivered and green. Every suite passed with the defect present: the AC5 repo-wide sweep compared the index against the census, so a broken census agreed with the rows it had itself produced.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (from the independent review of US0477); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z
> **Verification depth:** functional

## Summary

`epic_story_count` compared the `Epic` field whole (`field == epic_id`) while every other reader of that field in the family extracts the id first (transition, `verify_ac`, sprint, `ac_scope`, mutation). The shipped story template writes the LINKED form `> **Epic:** [EP0001: Title](../epics/EP0001-x.md)` and 34 story files here use it, so the census counted none of them. Two consequences both reached the tracked tree: a story count of 7 was written into a row whose true count is 18, justified by a census that could not see two thirds of the evidence; and three rows were held as uncorroborated that simply had stories the reader could not see. The recorded REASON for holding the remaining rows was also wrong - they are not epics whose story files were deleted (no story file has ever been deleted in this repository's history) but epics whose rows carry an Estimated Story Count from before stories were individually tracked.

## Steps to Reproduce

1. `grep -h '^> [*][*]Epic:[*][*]' sdlc-studio/stories/*.md | sort | uniq -c` - 34 files use the linked form.
2. Count EP0008 both ways: strict equality gives 7, id-extraction gives 18.
3. The committed row said 7.

## Proposed Fix

FIXED. The census extracts and normalises the id (`ID_SEARCH_RE` + `norm_id`), matching every other reader; the lookup normalises its argument too. The three wrong counts are corrected in the index and the held set drops from eight rows to six. The false explanation is corrected in the reference, the story Evidence, the source comments and the pinned test comment. A regression test asserts the bare, linked and hyphenated forms all count as one epic.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `epic_story_count` compared the `Epic` field whole (`field == epic_id`) while every other reader of that field in the family extracts the id first (transition...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (from the independent review of US0477) | Filed |
