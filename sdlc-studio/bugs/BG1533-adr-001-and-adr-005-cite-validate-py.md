# BG1533: ADR-001 and ADR-005 cite validate.py instructions as enforcement, but it is advisory and nothing runs it

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, AGENTS.md, tools/tests/test_lean_trd_refresh.py, changelog.d/BG1533.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md ADR-001 Consequences (lines 839-840); ADR-005 Decision (lines 935-937)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:23:23Z

## Summary

ADR-005 in `sdlc-studio/trd.md` (lines 935 to 937) says `validate.py instructions` enforces the hygiene of the AGENTS.md standard, and ADR-001 (lines 839 and 840) says it partly enforces keeping the loading guide and the type tables in sync. The check is advisory: every content rule is a warning, it exits 0 with warnings, and no hook, gate lane, npm script or workflow runs it. Only `init.py` and `project_upgrade.py` call it, to report. It contains no loading-guide or type-table check at all, so the mitigation ADR-001 names for its own downside does not exist. Run against this repository it reports two of ADR-005's own hygiene rules failing (no doctrine pointer and no integration rule), and nothing noticed. A rule stated but gated nowhere is the failure LL0027 names.

## Steps to Reproduce

1. From the repository root, run `validate.py` with the `instructions` subcommand.
2. Observe two warnings, `no-doctrine-pointer` and `no-integration-rule`, the line 'errors=0 warnings=2 info=0', and exit status 0.
3. Search `gate.py`, `package.json`, `.githooks/`, `.github/workflows/` and the shell scripts in `tools/` for a call to the instructions check: there is none.
4. Search `validate.py` for loading guide or type table: there is no match.
5. Read `sdlc-studio/trd.md` lines 839 to 840 and 935 to 937.
6. Expected: the ADRs describe what the check does and where it runs. Actual: they call an advisory, unwired check enforcement, and one of the two claimed checks does not exist.

## Proposed Fix

Correct both ADRs in `sdlc-studio/trd.md`: ADR-005 should say `validate.py instructions` reports the hygiene as warnings at init and upgrade and is not a gate, and ADR-001 should drop the claim that it holds the loading guide and type tables in sync, naming the check that does or stating that none does. Resolve this repository's two warnings in `AGENTS.md`, either by adding the doctrine pointer and the integration line within the page's character cap or by recording why each is declined. Add a pin to `tools/tests/test_lean_trd_refresh.py` that the TRD does not use the word enforces for a check that exits 0 on its own warnings, and that the instructions check reports no warning on this repository. Whether the check should become a blocking lane is a separate change to file.

## Acceptance Criteria

- [ ] **AC1** Given ADR-001 and ADR-005 in `sdlc-studio/trd.md`, when they are read, then ADR-005 says `validate.py instructions` reports the AGENTS.md hygiene as warnings at init and upgrade and is not a gate, and ADR-001 no longer says it keeps the loading guide and type tables in sync, naming the check that does or stating that none does. Fails on: the word enforces used for a check that exits 0 on its own warnings.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdInstructionsCheckTests::test_the_adrs_do_not_call_the_advisory_check_enforcement
  - **Verified:** yes (2026-11-19)
- [ ] **AC2** Given this repository, when `validate.py instructions` runs from its root, then it reports no warning, with the doctrine pointer and the integration rule present in `AGENTS.md`. Fails on: `no-doctrine-pointer` or `no-integration-rule` still reported.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdInstructionsCheckTests::test_the_instructions_check_reports_no_warning_here
  - **Verified:** yes (2026-11-19)
- [ ] **AC3** Given `AGENTS.md` after the two additions, when its length is measured, then it stays within the 7,000 character cap the page states for itself. Fails on: the warnings cleared by growing the page past its cap.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdInstructionsCheckTests::test_agents_md_stays_within_its_character_cap
  - **Verified:** yes (2026-11-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
