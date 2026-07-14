# BG0138: TS0001 carries 13 broken relative links (../../ where ../ is correct)

> **Status:** Fixed
> **Severity:** Low
> **Effort:** S
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Affects:** sdlc-studio/test-specs/TS0001-core-artifact-lifecycle.md, tools/check_links.py
> **Verification depth:** functional - driven through the public guard and checked on its TRUE exit code, not its printed output (a guard that reports a failure and exits 0 is BG0134's defect). A probe artefact carrying a live dead link, the same link in a code span, and the same link in a fenced block reports ONLY the live one; a genuinely dead body link makes check_links exit 1, and the clean repo exits 0.
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

## Correction to the Affects (2026-07-14)

The `Affects` line named `sdlc-studio/test-specs/TS0001-core-artifact-lifecycle.md`. **That file does not
exist.** The real one is `TS0001-ep0010-ac-coverage-token-economy-learning-loop.md`. The diagnosis and the
count of 13 were correct; the filename was invented from memory rather than checked.

This is the SECOND bug report filed this day whose file path was wrong (BG0137's repro named the archive
sub-index `_index.md`; it is `<type>.md`). Both were caught by the agent doing the work, not by any guard -
and it exposes a real hole: **the grooming gate accepts an `Affects` naming a file that does not exist.**
It checks the field is present and parseable as a path list, never that the paths RESOLVE. A unit can
therefore be "groomed" against a fictional file list, and the planner will size it from nothing (an
unresolvable path yields complexity 0, which is the flat-floor fallback). Filed as BG0144.
