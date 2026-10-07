# BG0979: `file_finding.py` misdirects a CR's author: `--recommendation` is documented as RFC-only though a CR carries it, and the no-verifier warning cites a `sprint plan` refusal that never applies to a CR

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_cr_filing_guidance.py, changelog.d/BG0979.md
> **Evidence:** Found 2026-10-06/07 during the triage session that filed BG0955-BG0963 in this repository. CR-0611 filing.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:38:04Z

## Summary

`--recommendation` is documented 'rfc recommendation' (`file_finding.py`:2496), yet a CR filed with one lands a `## Recommendation` section; reading the help, the author filing CR-0611 left the recommendation out and pasted it in afterwards. Filing a CR with prose criteria also prints 'sprint plan REFUSES a unit whose criteria carry NO verifier at all', but a CR is never planned: it is refined into stories, which carry the verifiers.

## Steps to Reproduce

`file_finding.py file --help` -> the `--recommendation` line reads 'rfc recommendation'; file a CR with `ac` and no `verify` -> the sprint-plan warning prints.

## Proposed Fix

Document `--recommendation` for both CR and RFC, and for a CR replace the warning with one that says the criteria get their verifiers when it is refined.

## Acceptance Criteria

- [ ] **AC1** The help for `--recommendation` names CRs as well as RFCs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cr_filing_guidance.py -k recommendation_help_names_cr
- [ ] **AC2** Filing a CR with prose criteria does not print the sprint-plan refusal warning, and filing a bug without verifiers still does
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cr_filing_guidance.py -k cr_criteria_warning_points_to_refine

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
