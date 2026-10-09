# BG1019: artifact.py retitle refuses in every consuming project: it loads tools/check_links.py from the operated repo or the skill's own source checkout, and an installed skill has neither

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T15:04:47Z

## Summary

`artifact.py retitle` (`_load_check_links`, artifact.py ~2004-2020 on main) looks for `check_links.py` at <operated repo>/tools/`check_links.py` and at Path(`__file__).parents[4]`/tools/`check_links.py` - the skill's own source repo layout. An installed skill (~/.claude/skills/sdlc-studio) has no such parent, and a consuming project has no tools/`check_links.py`, so every retitle in a consuming project refuses with 'cannot locate `check_links` (tools/`check_links.py)` to find inbound references - refusing rather than rename the file'. Found retitling a bug in a consuming project (a consuming project) whose title the work had outgrown; the only route left is a hand rename, which the skill otherwise forbids.

## Steps to Reproduce

In a consuming project with the installed skill 6.1.x: python3 ~/.claude/skills/sdlc-studio/scripts/artifact.py retitle --id BG0001 --title 'x' -> refused, cannot locate `check_links.`

## Proposed Fix

Ship the inbound-reference scan as runtime payload (move the needed `check_links` functions into scripts/, or a scripts/links.py), or fall back to a built-in grep-based inbound-reference scan when `check_links` is absent; add a test that runs retitle from an installed-layout copy with no tools/.

## Acceptance Criteria

- [ ] **AC1** retitle succeeds in a consuming project with the installed skill layout and no tools/`check_links.py`, still rewriting inbound references
  - **Verify:** shell python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_installed_layout.py -q

## Impact

Retitle is unusable outside the skill's own repo; artefact titles drift from their content.

## Triage

- Reproduced on 2026-10-09 with the installed copy in a throwaway project: after `reconcile.py apply --scope bugs`, `artifact.py retitle --id BG0001 --title 'new title'` refuses `cannot locate check_links (tools/check_links.py) to find inbound references`. `check_links.py` lives in the repository's `tools/`, which is not shipped. Pre-existing.
- Severity Medium stands: retitle is unusable in every consuming project. Private project name generalised.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
| 2026-10-09 | Claude Opus 5.5 (triage) | Triaged: reproduced with the installed copy; project name generalised |
