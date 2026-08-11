# BG0523: Five acceptance criteria are pinned by verifiers that cannot fail on what they claim

> **Status:** Fixed
> **Severity:** High
> **Points:** 5
> **Verification depth:** functional (each of the five criteria's named mutants applied to the shipped file, bytecode purged, run under `python3 -B`, the anchor asserted unique, the patch asserted to have changed the file, and the tree verified byte-identical afterwards; every one KILLED, and each was reproduced as SURVIVED against the pre-repair verifier first)
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

> **Groomed 2026-08-11.** The tool-derived criteria this replaces restated the finding, which
> states nothing a test can fail on. Each one below names, in terms, the production change that
> must redden it, and carries its own verifier - the repaired criterion's verifier stays with
> that criterion, so nothing here shares a selector with the unit it is about.

### AC1: the recorded ledger keys are read by running the writers, not by scanning for them

- **Given** the `batch_changes` keys `run_state` writes, derived by executing a drop, an add with
  a reason and a second add of the same unit against a throwaway run - the three branches that
  between them produce every key the two writers can record
- **When** a key is ADDED to an entry (`origin` on the drop) or RENAMED (`note` to `remark` on
  the duplicate add), and the batch-mutation section of `help/sprint.md` is left alone
- **Then** the check fails naming the key, because the set is what the writers put on a real
  ledger rather than a `"(action|id|reason|at|note)"` alternation that names the answer in
  advance and so cannot see either change; and a key the section does not name as a code span is
  refused, so being right about the set is worth something
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py::SprintSurfaceTests::test_the_recorded_key_set_is_executed_and_an_unnamed_key_is_refused

### AC2: the cross-kind masking fixture carries both kinds

- **Given** the fixture behind `a kind paid down elsewhere cannot mask a regression in another`,
  whose masking story carried `Status: Ready` while `affects-unresolvable` is reported only at a
  terminal status, so it emitted zero instances of the kind it exists to be about
- **When** `affects-unresolvable` is dropped from `validate.RATCHET_RULES`, or the masking story
  is put back at a non-terminal status
- **Then** the check fails, because the surplus is asserted by identity - two
  `affects-unresolvable` instances on that story, named target by named target - rather than
  assumed; without it the scenario reduces to its single-kind sibling and dropping the rule from
  the comparison survives
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::WarningRatchetTests::test_the_masking_fixture_emits_the_second_kind_it_is_named_for

### AC3: the lane's refusal is attributable to the ratchet and actionable on its own

- **Given** a temp clone with the shipped hooks enabled and a staged artefact carrying one
  unrecorded `affects-undeclared` instance, where other lanes also fail
- **When** `cmd_warning_ratchet` is neutered to `return 0`, or `render_ratchet` prints a bare
  count instead of the instance identities
- **Then** the check fails, because it reads the `FAIL warning-ratchet` line and then only that
  lane's own block - the bare token `warning-ratchet` also appears on the hook's `ok` line, and
  the returncode and HEAD assertions were being carried by the unrelated failing lanes
- **Verify:** pytest tools/tests/test_message_first_gate.py::WarningRatchetLaneTests::test_the_refusal_names_the_instance_inside_the_ratchet_lane_own_block

### AC4: the exempt set follows the resolver where a verb heuristic would disagree

- **Given** a duplicate group whose selector is `pytest -k a_thing`: the verb is inside
  `_COLLECTABLE`, so a verb comparison calls it answerable, while the resolver answers None
  because the selector names no file any collection could run over
- **When** the lint's `selector_resolves(...) is None` call is replaced by that verb comparison
- **Then** the check fails, because the group is reported splittable rather than exempt. Every
  fixture the set was previously derived over used a verb OUTSIDE `_COLLECTABLE`, where the
  resolver short-circuits and the two answers are the same sentence, so the derivation claim was
  unpinned however the report read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::UnanswerableGroupTests::test_the_resolver_and_a_verb_heuristic_disagree_and_the_report_follows_the_resolver

### AC5: the late-`fail` property is anchored on an assignment, not on one spelling

- **Given** the shipped `commit-msg` hook, asserted clean, and a copy of it with an assignment
  appended below the suite-verdict write in each of five spellings: `fail=$(( fail + 1 ))`,
  `fail=2`, `fail+=1`, an inline `&& fail=1`, and `export fail=1`
- **When** the detector is narrowed back to the literal `"fail=1" in ln`
- **Then** the check fails on every spelling but the literal one, which is door four standing
  open in the very test that pins the property; and reading `$fail` below the write is still not
  reported, so the detector has not simply been widened to everything
- **Verify:** pytest tools/tests/test_precommit_lane_order.py::SuiteVerdictFailOpenTests::test_the_property_check_catches_a_late_fail_however_it_is_spelled

## Impact

Five criteria read as evidence and are not. The changelog for US0468 states that a renamed ledger key now fails the test; it does not. This is the class the mutation discipline exists to prevent, and it reached a batch boundary with every unit reporting green.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | {{name the production change this test must fail on}} | the recorded ledger keys are read by running the writers, not by scanning for them |
| AC2 | {{name the production change this test must fail on}} | the cross-kind masking fixture carries both kinds |
| AC3 | {{name the production change this test must fail on}} | the lane's refusal is attributable to the ratchet and actionable on its own |
| AC4 | {{name the production change this test must fail on}} | the exempt set follows the resolver where a verb heuristic would disagree |
| AC5 | {{name the production change this test must fail on}} | the late-`fail` property is anchored on an assignment, not on one spelling |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Filed |
| 2026-08-11 | Claude Opus 5 | Groomed: the three tool-derived criteria replaced by five, one per repair, each naming the production change that must redden it and carrying its own verifier |
