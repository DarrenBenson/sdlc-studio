# BG1606: The close's caller-check reads a static site's page and component changes as mechanisms no caller consumes

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1606.md
> **Evidence:** the website's RUN-01M7R7KN close, 2026-11-19: orchestrator
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T07:50:28Z

## Summary

`sprint close` on the website's run printed caller-unnamed for six of seven units, each a change to an Astro page, an MDX page, a component or a data file the build renders: 'adds a mechanism ... and no criterion names the caller that consumes it'. On a static site the built page is the deliverable and the reader is its consumer, so the advisory is noise on every content unit and buries the case it exists for.

## Steps to Reproduce

Close a run whose units change only src/pages, src/content and src/components files of an Astro site: the caller-check lists every unit as caller-unnamed.

## Proposed Fix

Treat a unit whose Affects are rendered content (pages, content collections, components and the data they read) as consumed by the build, or let a project declare its rendered paths in config, so the caller-check judges only code a caller must reach.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint close` on the website's run printed caller-unnamed for six of seven units, each a change to an Astro page, an MDX page, a component or a data file the...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Close a run whose units change only src/pages, src/content and src/components files of an Astro site: the caller-check lists every unit as caller-unnamed.
- [ ] **AC3** The proposed fix lands, pinned by a test: Treat a unit whose Affects are rendered content (pages, content collections, components and the data they read) as consumed by the build, or let a project...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
