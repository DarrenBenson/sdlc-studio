# BG0868: refine add can only add stories under a new epic, so a story for a request's existing epic is minted by hand

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_refine_add_into.py, changelog.d/BG0868.md, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Evidence:** backlog sweep 2026-10-01, US0966 minted by hand
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T10:05:20Z

## Summary

Found in the 2026-10-01 backlog sweep: adding the near-miss story (US0966) to CR0559's existing epic EP0244 needed `artifact.py new --epic EP0244` plus a hand-written `Delivers: CR0559`, because `refine.py add` takes `--epic-title` (a new epic) and has no `--into` - while `refine.py apply` does accept `--into EPxxxx`. Premise at HEAD: `refine.py add --help` lists --request, --epic-title, --story, --breakdown, --dry-run and no --into.

## Steps to Reproduce

On a request already decomposed into EPxxxx, try to add one story to EPxxxx with `refine.py add --request CRxxxx ...`: the only target is a new epic.

## Proposed Fix

Accept `--into EPxxxx` on `refine add`, as `refine apply` does, wiring the story's Epic and Delivers lines and the request's links the same way.

## Acceptance Criteria

- [ ] **AC1** Given a request already decomposed into an epic, when `refine.py add --request <id> --into <epic> --story 'title|1|<affects>'` runs, then the story is created under that epic with `Delivers: <request>` and no new epic is minted. Fails on: HEAD, which rejects --into
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_refine_add_into.py::RefineAddIntoTests::test_add_into_the_existing_epic
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
