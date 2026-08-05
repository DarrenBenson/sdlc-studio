# BG0523: Five acceptance criteria are pinned by verifiers that cannot fail on what they claim

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_message_first_gate.py
> **Evidence:** RUN-01KZ79C1 batch boundary, both seats, each mutant applied in an isolated clone with the anchor asserted unique and the working tree verified clean afterwards.
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Both adversarial seats at the RUN-01KZ79C1 boundary applied the mutants the criteria NAME, and five survived. Each criterion is marked Verified while its verifier is unable to fail on the property it states.

**US0468 AC2** - the `batch_changes` key set is derived by `re.findall(r'"(action|id|reason|at|note)":', src)` over the whole `run_state` module: a hardcoded alternation, not a derivation. Adding `origin` to the drop entry SURVIVED; renaming `note` to `remark` SURVIVED. AC2 says a key added or renamed fails the test.

**US0480 AC3** - the cross-kind masking fixture's `US0003-x.md` carries `Status: Ready`, but `affects-unresolvable` only fires at a terminal status, so the fixture emits ZERO instances of the kind it claims to repair. The test reduces to AC1's scenario; dropping the rule from the comparison SURVIVES.

**US0480 AC5** - neutering `cmd_warning_ratchet` to `return 0` left both lane tests passing. The returncode and HEAD assertions are satisfied by unrelated failing lanes in that fixture; `assertIn("warning-ratchet", text)` matches the hook's `ok warning-ratchet` PASS line. The sibling control already uses the discriminating string `FAIL warning-ratchet`.

**US0637 AC1** - `_COLLECTABLE = {"pytest"}` short-circuits before the absent-runner branch, so `the resolver answers None` is operationally identical to `the verb is not pytest` for every group in this corpus. Replacing the resolver call with a verb comparison leaves the module green and the corpus output byte-identical. AC1's whole point - that the set is DERIVED - is unpinned.

**BG0507 AC5** - the property test greps for the literal `fail=1`. Appending `fail=$(( fail + 1 ))` below the verdict write left the lane suites green. AC5 says the test fails if a new check is appended below; door four is open. `^\s*fail=` would have killed it.

## Steps to Reproduce

For each: apply the mutant the criterion names, purge `__pycache__`, run with python3 -B, and observe the named verifier still passes. All five were reproduced independently in isolated clones.

## Proposed Fix

Take them one at a time; they are five separate repairs sharing a cause. Derive US0468's key set from the `batch_changes` writer rather than a module-wide alternation. Give US0480 AC3's fixture a terminal status so it emits the kind it is about, and assert US0480 AC5 on `FAIL warning-ratchet` as its own control already does. Pin US0637 AC1 on a case where the resolver and a verb heuristic genuinely disagree - which, given _COLLECTABLE, may mean the criterion needs restating rather than the test strengthening. Anchor BG0507 AC5 on `^\s*fail=` rather than one spelling.

## Acceptance Criteria

- [ ] The behaviour described is corrected: Both adversarial seats at the RUN-01KZ79C1 boundary applied the mutants the criteria NAME, and five survived.
- [ ] Following the recorded steps no longer reproduces the defect: For each: apply the mutant the criterion names, purge `__pycache__`, run with python3 -B, and observe the named verifier still passes.
- [ ] The proposed fix lands, pinned by a test: Take them one at a time; they are five separate repairs sharing a cause.

## Impact

Five criteria read as evidence and are not. The changelog for US0468 states that a renamed ledger key now fails the test; it does not. This is the class the mutation discipline exists to prevent, and it reached a batch boundary with every unit reporting green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Filed |
