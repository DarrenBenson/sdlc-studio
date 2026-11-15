# BG1453: file_finding keeps a placeholder id such as changelog.d/BGXXXX.md in Affects verbatim instead of substituting the minted id or refusing it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding_placeholder.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, changelog.d/BG1453.md
> **Evidence:** Run twelve (RUN-01M7E52T) orchestrator friction log
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:38:24Z

## Summary

Seventeen bugs filed from fields files carried `changelog.d/BGXXXX.md` in Affects; BG1441's self-check was then refused when its builder wrote the real fragment.

## Steps to Reproduce

File a bug whose fields-file Affects holds changelog.d/BGXXXX.md: the Affects keeps it.

## Proposed Fix

Substitute the minted id for an XXXX placeholder in Affects, or refuse the placeholder with the reason.

## Acceptance Criteria

- [ ] **AC1** Given a fields file whose Affects names changelog.d/BGXXXX.md, when the finding is filed, then its Affects names changelog.d/<minted id>.md or the filing is refused. Fails on: the placeholder kept.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_placeholder.py::FileFindingPlaceholderTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
