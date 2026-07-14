# BG0138: TS0001 carries 13 broken relative links (../../ where ../ is correct)

> **Status:** Open
> **Severity:** Low
> **Effort:** S
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Affects:** sdlc-studio/test-specs/TS0001-core-artifact-lifecycle.md, tools/check_links.py
> **Depends on:** BG0137
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The test spec sdlc-studio/test-specs/TS0001 links to stories, the PRD and epics with a ../../ prefix where ../ is correct, so 13 links in one artefact body do not resolve. Surfaced by BG0135 while widening `check_links`: the new index-row pass does not scan artefact BODIES, only index rows, so this is invisible to the gate. It is a small defect on its own, but it is evidence for the general case - nothing validates the relative links inside an artefact body, so any artefact can carry dead references indefinitely.

## Steps to Reproduce

1. Open sdlc-studio/test-specs/TS0001-*.md. 2. Read lines 21-31, 599 and 600: they use ../../stories/, ../../prd.md, ../../epics/. 3. TS0001 sits at sdlc-studio/test-specs/, so the correct prefix is ../ - the targets are one level up, not two. 4. All 13 links 404 on GitHub.

## Proposed Fix

Correct the 13 links in TS0001. Then consider the general case: extend `check_links` to validate relative file links inside artefact BODIES, not only index rows. Scope it carefully - the skill tree (templates, best-practices) deliberately carries unresolvable placeholder links like path/to/guide.md and CR{{`dep_id`}}-{{`dep_slug`}}.md which are payload meant to resolve in a consuming project, so a body-link pass must be scoped to the sdlc-studio/ workspace or it will cry wolf on 58 template placeholders.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
