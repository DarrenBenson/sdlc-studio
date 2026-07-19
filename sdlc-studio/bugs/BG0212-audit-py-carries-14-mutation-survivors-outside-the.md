# BG0212: audit.py carries 14 mutation survivors outside the profile parser, now enumerated in full

> **Status:** Fixed
> **Verification depth:** functional (full 190-mutant enumeration re-run: 15 survivors to 6, and each of the 6 shown equivalent by construction)
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/audit.py, .claude/skills/sdlc-studio/scripts/tests/test_audit.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A full mutation enumeration over audit.py (190 mutants applied, 0 truncated, 0 un-checked, test command covering `test_audit`*.py) leaves 15 survivors. One - the dead-store level initialiser in `_reference_section` - is unpinnable by construction: its value is unobservable, because the anchor-not-found path returns before level is ever read. The other 14 are real coverage gaps in the `audit_unit` and reporting surface, outside the profile parser that BG0203 was scoped to. They are the same class as the profile-surface gaps fixed under BG0203 (not-found and empty-return paths that no test asserts), in code BG0203 did not cover. Filed rather than fixed so BG0203 stays inside its stated scope.

## Steps to Reproduce

find . -name `__pycache__` -type d -exec rm -rf {} + ; python3 .claude/skills/sdlc-studio/scripts/mutation.py run --files .claude/skills/sdlc-studio/scripts/audit.py --test "cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest discover -s tests -p '`test_audit`*.py'" --max-mutations 200 --format json. Survivors report at lines 179 (unpinnable dead store), 228, 229, 233, 239, 241, 249, 271, 347, 358, 375, 458, 472, 476, 481.

## Proposed Fix

Pin each surviving branch with a test that asserts the behaviour it controls, as was done for the profile parser: the not-found and empty-return paths need a case that distinguishes them from the happy path. Leave line 179 alone and say why - a dead store with no observable value cannot be pinned, and a test pretending to cover it would be the vacuous kind this repo keeps finding.

## Resolution - 15 survivors to 6, and the 6 are unkillable by construction

**Nine were real and are pinned.** `cmd_profile`'s output branches (list vs resolve, text vs
JSON, the threshold line) had no test asserting what the COMMAND prints, only what the
resolution beneath returned. Three predicate fall-through branches - `_weak_verify`,
`_missing_regression_test`, `_already_satisfied` - were tested for their TRUE case only, so
the common answer could be inverted unnoticed. And `cmd_check`'s status-query path was
exercised nowhere: neutralising the id-selection line left the batch EMPTY, which audits
clean and exits 0 - a false green over work never examined.

**Two needed `assertIs`, not `assertFalse`.** These predicates are annotated `-> bool`, and a
stub returning `None` is falsy, so `assertFalse` passed on a mutant that had broken the
declared contract. Asserting identity against `False` pins the annotation and kills them.

**The remaining 6 are EQUIVALENT MUTANTS, not coverage gaps**, and are recorded here rather
than chased:

| Line | Mutant | Why no test can kill it |
| --- | --- | --- |
| 179, 271, 458 | `unset-delivered-field` on an initialiser | The value is always overwritten before it is read, so the initial value is unobservable |
| 233, 241, 249 | `stub-return-null` on `return 0` | `main` returns into `SystemExit`, and `SystemExit(None)` exits 0 exactly as `SystemExit(0)` does - behaviour is identical |

Chasing these would mean writing tests that assert implementation details no caller can
observe, which is the vacuous coverage this repo keeps filing bugs about. **A mutation
survivor is not automatically a coverage gap**, and reporting a count without that
distinction overstates the debt - which is how BG0203 came to be filed against code that was
already covered.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
| 2026-07-19 | sdlc-studio | Fixed. 9 real gaps pinned, 15 survivors to 6; the 6 shown equivalent by construction |
