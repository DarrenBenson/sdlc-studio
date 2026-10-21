# BG1068: artifact.py retitle rewrites an inbound link's target but leaves its link text naming the old title, so an epic's story breakdown reads the retired title

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, tools/check_links.py, .claude/skills/sdlc-studio/scripts/tests/test_retitle_link_text.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, changelog.d/BG1068.md
> **Evidence:** EP0289 after `artifact.py retitle` of US1080, US1081 and US1082 on 2026-10-19: the three breakdown links pointed at the new slugs and kept the old titles as text, until hand-corrected.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T08:46:07Z

## Summary

`artifact.py retitle` rewrites the H1, the filename slug and the index row, and rewrites inbound references to the new path. An epic's Story Breakdown line carries the story's title as the link text (`- [ ] [US1080: <title>](../stories/US1080-<slug>.md)`), and retitle changes only the target, so the epic keeps announcing the title the retitle retired. Observed on 2026-10-19 retitling US1080, US1081 and US1082 inside EP0289.

## Steps to Reproduce

`artifact.py retitle --id US1080 --title "<new>"` on a story an epic lists -> the epic's breakdown link points at the new slug but its text still reads `US1080: <old title>`.

## Proposed Fix

When an inbound link's text is the artefact's own `<ID>: <old title>`, rewrite it to the new title with the target; leave any other link text alone.

## Acceptance Criteria

- [ ] **AC1** After `retitle`, an epic's breakdown link to the retitled story carries the new title as its text as well as the new path
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_link_text.py -k breakdown_link_text_follows_the_retitle

## Impact

The epic, the first thing a reader opens, names work by a title nobody uses any more, and a reconcile does not flag it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
