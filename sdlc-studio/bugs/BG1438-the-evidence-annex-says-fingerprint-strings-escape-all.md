# BG1438: The evidence annex says fingerprint strings escape all control characters while the reference implementation escapes only U+0000 to U+001F, and it omits the no-closed-sprint limit of the version stamp

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_wording.py, tools/check_budgets.py, changelog.d/BG1438.md, tools/tests/test_check_budgets.py
> **Evidence:** Run twelve (RUN-01M7E52T) reviews of US0993 and US0996: sdlc-studio/reviews/verdicts/US0993/804aba71b3f4-3a4029d3.txt and sdlc-studio/reviews/verdicts/US0996/86dc8ba3d0a0-0ca76220.txt (non-blocking)
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T02:39:07Z

## Summary

reference-evidence-schema.md (the Report fingerprint section, near line 361) says strings escape all 'control characters', but the reference implementation it gives escapes only U+0000 to U+001F, so a consumer escaping U+007F or U+0080-U+009F computes a different digest. The Versioning section also leaves out the known limit the version-stamp story's Notes ask for: a project with ledgers but no closed sprint has no stamp to read.

## Steps to Reproduce

Read the fingerprint section's escaping rule beside its reference implementation; read the Versioning section for a project that has never closed a sprint.

## Proposed Fix

Name the escaped range exactly (U+0000 to U+001F) and state the no-closed-sprint limit beside the ledger sections; move the page's line ceiling if the guide grows.

## Acceptance Criteria

- [ ] **AC1** Given the annex's fingerprint section, when it states which characters a string escapes, then it names U+0000 to U+001F, the range its reference implementation escapes, and the Versioning section states that a project with no closed sprint has no stamp. Fails on: 'all control characters', or no word on the unstamped case.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_wording.py::AnnexWordingTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
