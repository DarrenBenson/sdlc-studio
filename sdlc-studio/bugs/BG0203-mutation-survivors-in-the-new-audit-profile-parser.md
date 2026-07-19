# BG0203: mutation survivors in the new audit profile parser: profile_names and the lens-table break are unpinned

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py, .claude/skills/sdlc-studio/scripts/audit.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A bounded mutation run over this sprint's diff applied 15 mutants and 4 survived, all in audit.py's newly added profile surface. Two sites: `profile_names` (a stub-return-null and a no-op-mapper both survived, so no test pins what it returns) and `_parse_lens_table`'s early-break at the end of the first table (invert-guard survived at both branches, so the ignore-a-later-table behaviour the comment claims is untested). The code may well be correct; the point is that nothing would catch it becoming incorrect. Found by the mutation gate at the sprint close, not by the epic's own tests, which is the gate working as intended. Note the run sampled 15 of 654 enumerated mutants (2.3 per cent) under the ceiling, so the remaining 639 are un-checked rather than clean - this finding is a floor on the gap, not its extent.

## Steps to Reproduce

1. rm -rf .claude/skills/sdlc-studio/scripts/`__pycache__.` 2. python3 -B .claude/skills/sdlc-studio/scripts/mutation.py run --files .claude/skills/sdlc-studio/scripts/audit.py --max-mutations 15 --test 'cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest `tests.test_audit`'. 3. Observe SURVIVED at audit.py lines 95, 100, 118, 119.

## Proposed Fix

Add cases to `test_audit_profiles.py` that pin `profile_names`' return value (packs on disk unioned with the reference-declared defaults, sorted) and `_parse_lens_table`'s handling of a file containing a second table after the lens table. Then re-run the bounded mutation over audit.py and confirm those four sites are killed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
