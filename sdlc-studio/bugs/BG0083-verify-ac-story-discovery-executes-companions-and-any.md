# BG0083: verify_ac story discovery executes companions and any us*.md file, poisoning runs and ts-check

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4. walk_stories (verify_ac.py:594-602) matches any markdown whose name starts 'us' with no companion-suffix exclusion, though its docstring claims it matches the shared sdlc_md discovery (which excludes companions, sdlc_md.py:572-574). Reproduced and adversarially verified (RV0007): a consultation companion quoting an AC heading plus an unindented '- **Verify:** shell false' line was EXECUTED (arbitrary shell from a non-story document, subject to the shell gate), failed the run (exit 1) despite the real story passing, entered the report, and _report_failed_acs (:774) maps the companion stem to US0001 - so ts-check reports a false matrix-vs-report failure for the real story.

## Steps to Reproduce

stories/US0001-login.md (passing AC) + stories/US0001-login-consultations.md quoting '### AC1' and '- **Verify:** shell false'; verify_ac.py run -> exit 1, report contains the companion key; ts-check on a green matrix -> false failure.

## Proposed Fix

Filter by extract_record_id prefix US plus conventions.companion_suffixes, mirroring sdlc_md.iter_artifact_files.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
