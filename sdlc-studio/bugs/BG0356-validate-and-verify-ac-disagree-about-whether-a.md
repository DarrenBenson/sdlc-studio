# BG0356: validate and verify_ac disagree about whether a bug's Verify line executes

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; the shared authority mutation-killed)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

validate.py reports a bug's Verify: line as pseudo-verify - 'nothing executes this' - while verify_ac.py will in fact execute it. Two guards give the author opposite advice about the same line, and a fixed bug consequently has no agreed executable closure path.

## Steps to Reproduce

Run verify_ac in dry-run over a bug artefact whose acceptance criteria carry pytest Verify lines. It reports nine criteria, nine passing, none unspecified - so verify_ac does execute them. Then run validate check over the same file: it reports each of those lines as pseudo-verify, meaning nothing executes it. Two shipped guards give the author opposite advice about the same line. The verify_ac side skips only ids that do not begin with the story prefix; the validate side warns for any artefact typed change-request or bug.

## Proposed Fix

See the summary; each cited site names its own remedy.

## Acceptance Criteria

### AC1: The validator no longer reports a bug's Verify line as executed by nothing

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::VerifierAuthorityAgreementTests::test_a_bug_s_verify_line_is_not_reported_as_executed_by_nothing
- **Verified:** yes (2026-07-28)

### AC2: A request's Verify line still is, so the carve-out is a bug/story rule and not the deletion of the warning

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::VerifierAuthorityAgreementTests::test_a_request_s_verify_line_still_is
- **Verified:** yes (2026-07-28)

### AC3: The runner, the validator and the creators read ONE authority, asserted as agreement between them rather than three separately expected answers

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::VerifierAuthorityAgreementTests::test_the_three_sites_read_one_authority
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Filed |
| 2026-07-28 | Claude Opus 5 | Criteria authored at delivery. This bug was filed by the audit with `See the summary` in place of a contract, which is the shape the criteria floor refuses - and it refused this one at the commit. The Verify lines are EXECUTABLE because of the change this bug pair makes: before it, a bug could not carry one. |
