# CR-0705: sprint plan names the registry files a unit implies when it adds a script, a verb or reference text, before the build

> **Status:** Proposed
> **Priority:** High
> **Type:** enhancement
> **Size:** M
> **Evidence:** Run twelve (RUN-01M7E52T) orchestrator friction log F2, F4: US1155, BG1268, US1152, US0994/US0995, BG1268 again
> **Date:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:37:34Z

## Summary

Five run-twelve lands were refused after a full hook run for a file the unit's Affects did not name: the regenerated reference-scripts-surface.md (a new verb), `sprint_report.NON_CEREMONY_VERBS` (a new verb), a `### name.py` catalogue heading (a new script), the root census and parser coverage (a new script), a regenerated reading guide (a page past 400 lines) and a line ceiling (a page past 600). The plan's Affects advisory names none of them. A plan-time check that reads each unit's criteria and Affects for a new script or verb, and its reference pages' projected size, would name the missing files when grooming can still add them.

## Impact

Serves Abena Osei's End goal 3 (cost per point): each refused land cost 5 to 20 minutes of hooks plus a resumed builder.

## Acceptance Criteria

- [ ] `sprint plan` reports, for each unit whose criteria add a script or a verb, every registry file that implies and is missing from its Affects
- [ ] `sprint plan` reports a unit whose reference page would cross a reading-guide or line-ceiling threshold without the generated guide or the ceiling file in its Affects
- [ ] `sprint plan` reports a unit whose criteria add a script taking free prose, or a new flag, without `test_artifact.py` (the prose-writer sweep's `--fields-file` and `SAFE_INPUT_WRITERS` registry) or the unjudged-flags baseline and command audit in its Affects

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Raised |
| 2026-11-15 | Claude Opus 5.5 (run thirteen orchestrator) | Added the prose-writer sweep and the unjudged-flags ratchet, two more registries a new script or flag implies: US1058's land was refused on the first and its repair turned main red on the second (BG1459) |
