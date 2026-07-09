# CR-0200: Split the reference-scripts.md catalogue into a lean index plus grouped pages

> **Status:** Proposed
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Priority:** Low
> **Type:** Improvement

## Summary

`reference-scripts.md` has grown past its 600-line reference budget three sprints running
(EP0014, EP0016, EP0019) and is deliberately allowlisted at 643. It is the script catalogue an
agent reads before hand-doing a mechanical task, so it is loaded often; a 640-line file is
costly to scan and the ceiling-bump ritual is a standing smell. Filed as a follow-up in RETRO0012
and RETRO0013.

Split it into a lean index (a one-line-per-script table pointing to grouped detail pages, e.g.
by lifecycle area - creation/transition, reconcile/verify, audit/review, upgrade/deploy), so each
file sits under the reference budget and the index is cheap to load. The doc-coverage floor must
still hold: every shipped script is catalogued somewhere reachable, and `doc_coverage.py` finds it.

## Acceptance Criteria

- [ ] `reference-scripts.md` becomes a lean index under the 600-line reference budget; the 643
      allowlist entry is removed from `tools/check_budgets.py`
- [ ] Every script still has a catalogue entry (`doc_coverage.py` passes: 0 undocumented); detail
      lives in grouped sub-pages each under the reference budget
- [ ] All internal anchor links resolve (`check_links.py`); pointers from SKILL.md / other
      references to `reference-scripts.md` still land
- [ ] No script content or behaviour changes - this is a documentation reorganisation only

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
