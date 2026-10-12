# BG1024: verify_ac's grep verb takes a leading flag as the pattern, so `grep -q -e X file` and `grep -E ... file` Verify lines fail

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_grep_flags.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/reference-verify.md, changelog.d/BG1024.md
> **Created:** 2026-10-11
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-10T23:07:53Z

## Summary

The grep DSL verb (`verify_ac.py` ~1505-) treats the first shlex token as the regex and the rest as paths, so a Verify line written with grep flags (`grep -q -e foo src/x.ts`, `grep -E 'a|b' src/x.ts`) searches for the literal '-q' / '-E' and fails. Found in a consuming project's release-gate triage (3 such lines). The second defect that triage found, a `### AC3 (DEFERRED)` heading not parsed as a criterion, is split out as BG1026.

## Steps to Reproduce

Verify line `grep -E 'a|b' src/x.ts` where src/x.ts contains 'a': reported red.

## Proposed Fix

Read a known set of leading grep flags (-E, -F, -i, -w, -q, and -e PATTERN) before the pattern and pass the meaningful ones through; a leading token outside that set stays the pattern, so a deliberate dash-leading pattern (`-Ran`, the case the `-e` and `--` hardening exists for) is still searched for literally.

## Acceptance Criteria

- [ ] **AC1** Given a Verify line `grep -E 'a|b' <file>` over a file containing `a`, when verify_ac runs it, then the criterion passes, and the same line over a file containing neither `a` nor `b` fails
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_grep_flags.py::GrepFlagTests::test_extended_flag_is_read_as_a_flag
- [ ] **AC2** Given a Verify line `grep -q -e foo <file>` over a file containing `foo`, when verify_ac runs it, then the criterion passes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_grep_flags.py::GrepFlagTests::test_e_pattern_is_the_pattern
- [ ] **AC3** Given a Verify line `grep -Ran <file>` whose leading token is not a known flag, when verify_ac builds the command, then it still searches for `-Ran` literally
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_grep_flags.py::GrepFlagTests::test_an_unknown_dash_token_stays_the_pattern

## Impact

The most natural grep Verify lines can never pass, so a criterion that is met reads red.

## Triage

- Confirmed at 19415be3 through `_build_command`: `grep -E 'a|b' src/x.ts` builds `['rg', '-q', '-e', '-E', '--', 'a|b', 'src/x.ts']`, and `grep -q -e foo src/x.ts` builds `['rg', '-q', '-e', '-q', '--', '-e', 'foo', 'src/x.ts']` (verify_ac.py:1506-1529). The first token is always the pattern. Pre-existing.
- The second defect in the filing (`### AC3 (DEFERRED)` not parsed) is a different code path (`AC_HEADING_RE`, lib/sdlc_md.py:58) and is split out as BG1026. Points raised to 2: a flag parser with the dash-leading-pattern protection kept is more than a one-liner. Severity Low stands.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-11 | sdlc-studio | Filed |
| 2026-10-12 | Claude Opus 5.5 (triage) | Triaged: reproduced; the heading defect split out as BG1026; criteria on a new test module (BG0980); changelog fragment named for the unit |
