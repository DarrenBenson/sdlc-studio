# BG0409: Six of the nine stop-ship repairs revert with no test going red, and two of the tests written to hold them assert a different thing than they claim

> **Status:** Fixed
> **Verification depth:** functional (tests red-first, each fix verified by applying its mutant)
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Round-2 independent review of commit 06c806d7: 21 mutants applied, 12 killed, 9 SURVIVED the full 5,140-test suite. Every survivor re-confirmed against the whole suite, and eight compatible survivors applied simultaneously still gave `Ran 5140 tests ... OK`.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** round-2 independent review; human; v1

## Summary

The nine stop-ship repairs are correct code. Six of them are held by nothing, so the next refactor reverts them silently - which is the same failure class the nine were filed for.

What survives the full suite:

- **`file_finding`, both halves (F1, F2).** `test_file_finding.py` is not in the commit AT ALL. Removing `_prose_safe` restores the metadata-forgery path; reverting the heading test to a whole-body substring restores the false refusal. Two live security/correctness fixes, zero guards.
- **`release_cut`'s exception branch (R2).** Restoring `except Exception: return [], None` survives. The test named for it, `test_a_raising_helper_refuses_rather_than_reporting_clean`, calls the real helper against `/nonexistent/definitely/not/a/repo` - which does NOT raise, it returns `{'baselined': False, 'corrupt': False, ...}`. The test exercises the no-baseline branch, and never asserts `unknown` at all. One of the three states the commit says are now told apart has no guard.
- **mutation's method-doubling half (M2).** Returning `f"{ctx}.{meth}"` unconditionally survives, because the only unittest-format assertions use the PRE-3.11 form `(tests.test_x.C)`. The 3.11+ form the fix exists for is the only form this machine emits (Python 3.14.4).
- **gate's two halves (G2, G3) individually.** Only removing BOTH the protected-prefix check and the `isdir` check reddens. They are redundant for the single fixture, so neither is independently held - and the prefix half has a case no test touches: a DIRECTORY under a protected tree, which only the prefix check rejects.
- **mutation's evidence half (M4, M5).** `test_the_evidence_satisfies_its_consumer` hand-writes a dict already containing `killed_by` and feeds it to `census.mutant_rows`. It asserts the CONSUMER, never the producer. Dropping `row["killed_by"] = [killer]` survives. This is the re-implements-the-code-and-asserts-it-against-itself pattern BG0401 was filed for in this same sprint, reintroduced in the test written to replace two source-greps.

And one guard over-claims its own scope rather than being absent: `CloseRecordsNoSuiteVerdictTests` documents itself as asserting "the PROPERTY - the close writes no suite verdict - rather than the absence of a call, so a differently-spelled reintroduction is caught too". It does not. Reintroducing US0553 as a direct `_p.write_text(...)` to the exact file `gate.suite_decision` reads survives all 5,140 tests: the test asserts `gate.recorded_verdicts == []` on a stub and never looks at the filesystem. Its companion `test_the_close_gate_runs_no_suite_lane` is a NAME grep over `DEFAULT_CHECKS` - a lane called `tests`, `mutation` or `verify` satisfies it.

## Steps to Reproduce

1. Apply each mutant above to a clean tree and run `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests` from the repo root. All six survive.
2. `git show --stat 06c806d7 | grep test_file_finding` returns nothing.
3. Run `close_owed.owed(Path('/nonexistent/definitely/not/a/repo'))` directly: it returns rather than raising, so the test named for the raising branch never reaches it.
4. Read `test_the_evidence_satisfies_its_consumer`: the `killed_by` key it asserts is one it wrote itself.

## Proposed Fix

One discriminating test per survivor, each written to fail against the mutant named above rather than against the shape of the fix.

The two that need more than a test:

- **`release_cut`'s raising branch** needs a helper that actually raises - monkeypatch `close_owed.owed` to raise, do not pick an input hoped to raise - and must assert `unknown` is set, which is the whole point of the return shape.
- **the mutation evidence half** must assert the PRODUCER: run a real mutant to a real kill and assert `killed_by` on the row `run_gate` emitted, not on a dict the test authored.

Correct the `CloseRecordsNoSuiteVerdictTests` docstring to describe what it checks - one call, on a stub - or make it check the property by asserting the file is absent after a close.

## Acceptance Criteria

- [ ] Each of F1, F2, R2, M2, G2, G3, M4 and M5 reddens at least one test when applied to a clean tree.
- [ ] `test_file_finding.py` covers both `_prose_safe` (a forged metadata line in `steps` does not survive `extract_field`) and the heading test (a body merely mentioning a heading in prose still lands its section).
- [ ] The `release_cut` raising-branch test drives a helper that genuinely raises, and asserts the refusal reason, not just an empty unit list.
- [ ] The mutation method-doubling test asserts the Python 3.11+ unittest form, which is the only form the current interpreter emits.
- [ ] The gate protected-prefix and isdir checks each redden a test on their own, and a directory under a protected tree is covered.
- [ ] The `killed_by` assertion is made against a row the producer emitted, not a dict the test wrote.
- [ ] `CloseRecordsNoSuiteVerdictTests`'s docstring matches its scope, or the test asserts the property it claims.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | round-2 independent review | Filed |
