# BG0203: mutation survivors in the new audit profile parser: profile_names and the lens-table break are unpinned

> **Status:** Fixed
> **Verification depth:** functional (both named survivors hand-mutated and shown killed; full 190-mutant enumeration over audit.py leaves the profile surface clean)
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

## Resolution - the premise was wrong, the conclusion was right

**Both named sites were already pinned.** Hand-mutating them against
`test_audit_profiles.py` kills both: `profile_names` stubbed to return `None` gives 7 errors
(`test_the_four_promised_profiles_are_all_present` asserts its exact contents), and
`_parse_lens_table`'s early break inverted gives 3 failures and 4 errors. Neither survives, so
the finding as written does not reproduce.

**What actually happened is the more useful defect.** The original run's test command did not
cover the tests that pin those sites, and a mutation run scoped below its target's real coverage
manufactures survivors. This was reproduced deliberately: pointing the gate at
`test_audit_profiles.py` alone reports 10 survivors, and widening it to `test_audit*.py` - the
same code, the same mutants - reports 4. Six of the ten were artefacts of the command, not gaps
in the tests. **A narrow test command does not under-report coverage, it over-reports absence**,
and the phantom survivors then get filed as bugs, as this one was.

**The remaining four were real and are fixed.** `_refute_declaration`'s no-declaration return,
`_reference_section`'s missing-anchor return and its `<= level` sibling-heading rule now have
tests; `PROFILE_DIR` was dead code - defined, never used, with `profile_names` recomputing the
same path inline - and is now the single answer it was meant to be.

**Evidence.** A full enumeration over `audit.py` (190 mutants applied, 0 truncated, 0 un-checked)
leaves the profile surface clean but for line 179, a dead-store initialiser whose value is
unobservable because the not-found path returns before it is read - unpinnable by construction,
not a coverage gap. The 14 survivors elsewhere in the file are outside this bug's scope and are
filed as BG0212.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
| 2026-07-19 | sdlc-studio | Fixed. Both named survivors falsified; the real cause was a mutation command scoped below the target's coverage. Four genuine survivors pinned, residue filed as BG0212 |
