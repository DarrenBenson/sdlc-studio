# BG1469: persona_memory.py's --fields-file on propose and approve has no test, so a mutant ignoring the document passes

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_propose.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py, changelog.d/BG1469.md
> **Evidence:** QA seat's review of BG1459, run thirteen (sdlc-studio/reviews/verdicts/BG1459/d67c157340c4-d551dd7c.txt).
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:34:09Z

## Summary

BG1459 routed `add`, `propose` and `approve` through one fields-file loader, and changelog.d/BG1459.md says all three are served by it. Only the `add` path is pinned. A mutant making `cmd_propose` ignore the document's title (`persona_memory.py` near line 987), or `cmd_approve` ignore its reason (near line 1010), passes `test_persona_memory_store.py`, `_propose`, `_approve` and `_brief`. A probe shows both paths work today, so this is missing cover, not a defect.

## Steps to Reproduce

Mutate `cmd_propose` to drop the document's title (or `cmd_approve` its reason) and run the persona-memory test files: all pass.

## Proposed Fix

Add one test each, driving `propose --fields-file` and `approve --reject --fields-file` through the CLI with prose holding a semicolon and `$(x)`, asserting the stored text and that a flag overrides its key.

## Acceptance Criteria

- [ ] **AC1** Given a propose run with --fields-file holding a title with a semicolon and $(t), when it records, then the stored title is the document's text verbatim, and a --title flag beside it wins. Fails on: `cmd_propose` ignoring the document's title.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_propose.py
- [ ] **AC2** Given an approve --reject run with --fields-file holding a reason, when it records, then the stored reason is the document's text verbatim. Fails on: `cmd_approve` ignoring the document's reason.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
