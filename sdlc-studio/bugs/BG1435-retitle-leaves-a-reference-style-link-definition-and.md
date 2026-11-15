# BG1435: retitle leaves a reference-style link definition and a link in the project-root README dangling, while its changelog says it finds every link to the renamed file

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/link_refs.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_retitle_reference_links.py, changelog.d/BG1019.md, changelog.d/BG1435.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Evidence:** Run twelve (RUN-01M7E52T) review of BG1019, qa-seat-BG1019-r1, verdict sdlc-studio/reviews/verdicts/BG1019/79e80f16d392-c2502f6d.txt ([new] scope of the claim; the scan is unchanged from base)
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T02:10:11Z

## Summary

`link_refs.inbound_references` scans inline `[text](path)` links under the workspace only, so a reference-style definition (`[label]: path`) and a link from the project-root README to a renamed artefact stay dangling while `artifact.py retitle` exits 0. changelog.d/BG1019.md:7 and the `scripts/lib/link_refs.py` module docstring say retitle finds every link to the renamed file. The narrow scan predates BG1019.

## Steps to Reproduce

Link a story from the project-root README and from a reference-style definition in another artefact, retitle the story, then run tools/`check_links.py`: both links dangle.

## Proposed Fix

Rewrite reference-style definitions too and include the project-root Markdown files in the scan, or scope the changelog and docstring to inline links under the workspace.

## Acceptance Criteria

- [ ] **AC1** Given an artefact linked from the project-root README and from a reference-style definition, when it is retitled, then both links point at the new name. Fails on: either left dangling while retitle exits 0.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_reference_links.py::RetitleReferenceLinkTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
