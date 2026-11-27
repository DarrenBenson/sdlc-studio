# BG1773: A request's Decomposed-into keeps only its last child when ids are Crockford-style, because `decomposed_ids` reads none of them

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, changelog.d/BG1773.md
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio file
> **Raised-by:** orchestrator; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-26T10:18:01Z

## Summary

In the website repository, whose ids are Crockford-style (US-01M8BJ3B, written US01M8BJ3B in a link field), refining CR-01M8A98E on 2026-11-26 with one `artifact.py new --parent CR-01M8A98E` per child (an epic and five stories) left the CR's Decomposed-into naming only the last child; CR-01M8A9DZ the same with three. artifact.py means to append (the new-with-parent path at scripts/artifact.py:1362-1366 on main reads the existing ids with `sdlc_md.decomposed_ids` and writes them back with the new one), but `decomposed_ids` returns [] for any Crockford id: run against main (f81903cf8), '> **Decomposed-into:** US01M8BJ3B' gives [] and 'EP01M8BJ86, US01M8BJ3B' gives [], while 'US1234, US1235' gives both. So every spawn overwrites the list, and reconcile's link check, which reads the field through the same function, sees no child to check and reports no drift, so the lost links are silent. Also present at v6.4.0 (artifact.py:1293-1295).

## Steps to Reproduce

With main's scripts on the path: python3 -c "import sdlc_md; print(sdlc_md.decomposed_ids('> **Decomposed-into:** US01M8BJ3B\n'))" prints []. In a fixture project with Crockford ids, two `artifact.py new --type story --parent <CR>` calls leave the CR's Decomposed-into naming only the second story.

## Proposed Fix

Make `decomposed_ids` read every id shape `norm_id` writes (the numeric and the Crockford forms), so the append path keeps the earlier children and reconcile's link check sees them.

## Acceptance Criteria

- [ ] **AC1** Given a Decomposed-into field naming Crockford-style ids (EP01M8BJ86, US01M8BJ3B), alone, in a list, or beside numeric ids, then `decomposed_ids` returns each, in order, and a parenthetical annotation is still stripped. Fails on: [] for a Crockford id.
  - **Verify:** shell python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py -k test_decomposed_ids_reads_crockford_ids
  - **Verified:** yes (2026-11-27)
- [ ] **AC2** Given a fixture project with Crockford ids and one request, when two `artifact.py new --type story --parent <request>` calls run through the CLI, then the request's Decomposed-into names both stories. Fails on: only the second story listed.
  - **Verify:** shell python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_refine.py -k test_two_spawns_under_one_parent_keep_both_with_crockford_ids
  - **Verified:** yes (2026-11-27)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | orchestrator | Filed |
| 2026-11-26 | orchestrator (D0545) | Affects gains changelog.d/BG1773.md for the lane; joins run twenty-eight to be fixed before 6.5 (the release bar allows no open Medium); its file stays out of git until Fixed. |
| 2026-11-26 | orchestrator (D0545) | Affects widened to reconcile.py and its test: the builder found reconcile's wiring read (`ID_SEARCH_RE.findall`) and its Epic read miss dashless schema-3 ids the same way, so they are fixed in this unit (D0561). |
