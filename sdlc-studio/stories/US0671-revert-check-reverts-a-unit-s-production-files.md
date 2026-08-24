# US0671: revert-check reverts a unit's production files and REFUSES when its own verifiers stay green

> **Status:** Draft
> **Closed with findings in:** BG0606 - the test-plan plan review REJECTed this unit's plan, and the plan-review gate was overridden at the close on the operator's recorded decision to carry it rather than repair it in this run. The rows are named in BG0606 and the tests that would bind them already exist.
> **Delivers:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Verification depth:** functional [[derived: criteria 13; plan rows 13; executed 13; killed 13; survived 0; not-run 0; retracted 1; entry point 13 of 13 criteria through the shipped CLI, 0 in-process | fp 16bcf65ccc60 ]] (the whole command is exercised through `verify_ac.py revert-check` against real git repositories with real files on disk, because the subject is what happens to bytes while it runs. NOT covered: a unit whose production file was ADDED by the change and so does not exist at the base ref - the revert deletes it, which is right, but no criterion pins that path)
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, tools/tests/test_skill_tests_env.py, .claude/skills/sdlc-studio/reference-schema.md
> **Epic:** EP0217
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** revert-check reverts a unit's production files and REFUSES when its own verifiers stay green
**So that** CR0547 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit ALL of whose non-exempt criteria stay green after its `Affects` production files are reverted to the base ref, when `verify_ac.py revert-check` runs, then it exits non-zero and names each such criterion - green after the revert is the REFUSAL, because a test that passes without the change never reached it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_a_wholly_green_unit_is_refused
  - **Verified:** yes (2026-08-21)
- [ ] **AC2** Given a unit whose verifiers genuinely exercise the shipped path, when the same revert-and-run happens, then the unit PASSES - the paired control, so the gate is shown to discriminate rather than to refuse everything put in front of it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_a_unit_whose_verifiers_go_red_passes
  - **Verified:** yes (2026-08-21)
- [ ] **AC3** Given a unit whose only green criteria are DECLARED EXEMPTIONS - a declared control, a well-formed `unnameable` row, or a criterion whose subject is a test file rather than production code - when the check runs, then it does NOT refuse the unit. RUN-01M0CT8P measured five criteria in this class across one batch, so a check without this taxonomy refuses correct work, and refusing correct work is how a gate gets switched off
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_declared_exemptions_do_not_trigger_a_refusal
  - **Verified:** yes (2026-08-21)
- [ ] **AC4** Given a FIXTURE reproducing the pre-repair working-tree state of BG0593 - the production change present, and its tests rebuilding the scratch in a private helper so the change is unexercised - when the check runs, then it REFUSES. Stated as a fixture and not as a commit BY NECESSITY: that state was never committed, it existed between 788e0c3f and its repair at 20de1d1c, and the mutation ledger it would otherwise be read from lives in gitignored `sdlc-studio/.local/`. A criterion claiming to pin a commit that does not hold the defect is a fabricated regression case, which is the defect class this very check exists to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_the_unexercised_change_fixture_is_refused
  - **Verified:** yes (2026-08-21)
- [ ] **AC5** Given a criterion whose `Verify:` line names a selector that does not resolve, when the check runs, then it reports UNRESOLVED for that criterion and does NOT count it as red - a selector failing because it names nothing is not a test reaching the change, and counting it as one is how this gate would manufacture a false pass
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_an_unresolvable_selector_is_unresolved_not_red
  - **Verified:** yes (2026-08-21)
- [ ] **AC6** Given a fixture whose verifier genuinely reaches the production change, when the check reverts and re-runs it, then that verifier goes RED - the control that proves the runner ran at all, without which a fixture reporting every criterion green cannot be told from one where nothing executed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_a_verifier_that_reaches_production_goes_red
  - **Verified:** yes (2026-08-24)
- [ ] **AC7** Given a plan row naming a PRODUCTION file whose extension is not a source-code one - a path carrying a directory, or a bare filename in a config or markup family - when the exemption taxonomy reads it, then the criterion is NOT exempted as test-code-only, because the same module's `revert_targets` would revert that file
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_a_plan_row_naming_a_non_source_production_file_does_not_exempt
  - **Verified:** yes (2026-08-24)
- [ ] **AC8** Given a plan row all of whose named paths really are test code, when the taxonomy reads it, then the exemption still FIRES - the paired control, because a pattern that saw production everywhere would refuse correct work, and refusing correct work is how a gate gets switched off
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_a_plan_row_naming_only_test_code_still_exempts
  - **Verified:** yes (2026-08-24)
- [ ] **AC9** Given a unit EVERY criterion of which is exempt, when the check runs, then it is REPORTED rather than passed - nothing was measured, and a unit that measured nothing must not come back green from the one check that exists to ask whether its verifiers reach anything
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_a_wholly_exempt_unit_is_reported_and_not_refused
  - **Verified:** yes (2026-08-24)
- [ ] **AC10** Given a criterion whose verifier never RAN - invalid, blocked or vacuous - when the check classifies it, then it is `unmeasured` and is NOT counted as evidence that the tests reached the change
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_a_verifier_that_never_ran_is_not_counted_as_evidence
  - **Verified:** yes (2026-08-24)
- [ ] **AC11** Given a criterion carrying a well-formed `unnameable` row BESIDE a nameable production mutant, when the exemption taxonomy reads it, then the criterion is NOT exempted - every row on it must be unnameable, or the second row costs nothing and covers the first
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_an_unnameable_row_beside_a_nameable_one_does_not_exempt
  - **Verified:** yes (2026-08-24)
- [ ] **AC12** Given the revert-and-run, when the check restores the tree, then it purges the cached bytecode for every file it touched - a stale `.pyc` makes the reverted module never load, and every criterion then comes back green from a check that measured nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_the_revert_purges_cached_bytecode_for_every_file_it_touches
  - **Verified:** yes (2026-08-24)
- [ ] **AC13** Given a git call that FAILS while reading the base revision, when the check reads it, then that is REPORTED rather than read as absent-at-base - deleting the production file on an unanswerable question manufactures the red this gate exists to look for
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_a_git_failure_is_reported_rather_than_read_as_absent_at_base
  - **Verified:** yes (2026-08-24)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `verify_ac.py`, delete the `if counted and not result["red"]` branch from `revert_check`, so a unit whose every measurable criterion stays green returns `pass` | Given a unit ALL of whose non-exempt criteria stay green after its `Affects` production files are reverted to the base ref, when `verify_ac.py revert-check` runs, then it exits non-zero and names each such criterion - green after the revert is the REFUSAL, because a test that passes without the change never reached it |
| AC2 | in `verify_ac.py`, replace `not result["red"]` with `green` in `revert_check`'s refusal condition, so it refuses whenever ANY criterion stays green | Given a unit whose verifiers genuinely exercise the shipped path, when the same revert-and-run happens, then the unit PASSES - the paired control, so the gate is shown to discriminate rather than to refuse everything put in front of it |
| AC3 | in `verify_ac.py`, return `{}` from `revert_exemptions` | Given a unit whose only green criteria are DECLARED EXEMPTIONS - a declared control, a well-formed `unnameable` row, or a criterion whose subject is a test file rather than production code - when the check runs, then it does NOT refuse the unit. RUN-01M0CT8P measured five criteria in this class across one batch, so a check without this taxonomy refuses correct work, and refusing correct work is how a gate gets switched off |
| AC4 | in `verify_ac.py`, invert the run classification in `revert_check` - `"red" if res.ok else "green"` | Given a FIXTURE reproducing the pre-repair working-tree state of BG0593 - the production change present, and its tests rebuilding the scratch in a private helper so the change is unexercised - when the check runs, then it REFUSES. Stated as a fixture and not as a commit BY NECESSITY: that state was never committed, it existed between 788e0c3f and its repair at 20de1d1c, and the mutation ledger it would otherwise be read from lives in gitignored `sdlc-studio/.local/`. A criterion claiming to pin a commit that does not hold the defect is a fabricated regression case, which is the defect class this very check exists to refuse |
| AC5 | in `verify_ac.py`, delete the `selector_resolves(...) is False` arm from `revert_check`, so an unresolvable selector is executed and its non-zero exit counted red | Given a criterion whose `Verify:` line names a selector that does not resolve, when the check runs, then it reports UNRESOLVED for that criterion and does NOT count it as red - a selector failing because it names nothing is not a test reaching the change, and counting it as one is how this gate would manufacture a false pass |
| AC6 | in `verify_ac.py`, take the `red` arm of `revert_check`'s run classification to `green`, so a verifier that FAILS after the revert - one that did reach the change - reports as untouched | Given a fixture whose verifier genuinely reaches the production change, when the check reverts and re-runs it, then that verifier goes RED - the control that proves the runner ran at all, without which a fixture reporting every criterion green cannot be told from one where nothing executed |
| AC7 | in `verify_ac.py`, drop the `/`-carrying arm from `_MUTANT_PATH_RE` and match only the bare-filename extension allowlist | Given a plan row naming a PRODUCTION file whose extension is not a source-code one - a path carrying a directory, or a bare filename in a config or markup family - when the exemption taxonomy reads it, then the criterion is NOT exempted as test-code-only, because the same module's `revert_targets` would revert that file |
| AC8 | in `verify_ac.py`, delete the test-code-only arm from `revert_exemptions`, so a criterion whose plan row names nothing but test code is measured rather than exempted | Given a plan row all of whose named paths really are test code, when the taxonomy reads it, then the exemption still FIRES - the paired control, because a pattern that saw production everywhere would refuse correct work, and refusing correct work is how a gate gets switched off |
| AC9 | in `verify_ac.py`, delete the `if not counted` branch from `revert_check`, so a unit with nothing measurable returns `pass` instead of being REPORTED | Given a unit EVERY criterion of which is exempt, when the check runs, then it is REPORTED rather than passed - nothing was measured, and a unit that measured nothing must not come back green from the one check that exists to ask whether its verifiers reach anything |
| AC10 | in `verify_ac.py`, classify an invalid, blocked or vacuous verifier result as `green` rather than `unmeasured` in `revert_check` | Given a criterion whose verifier never RAN - invalid, blocked or vacuous - when the check classifies it, then it is `unmeasured` and is NOT counted as evidence that the tests reached the change |
| AC11 | in `verify_ac.py`, exempt a criterion on ANY well-formed `unnameable` row in `revert_exemptions`, dropping the every-row requirement | Given a criterion carrying a well-formed `unnameable` row BESIDE a nameable production mutant, when the exemption taxonomy reads it, then the criterion is NOT exempted - every row on it must be unnameable, or the second row costs nothing and covers the first |
| AC12 | in `verify_ac.py`, delete the `_purge_pyc(root, targets["production"])` call from `revert_check`'s revert loop, so the reverted module loads from stale bytecode | Given the revert-and-run, when the check restores the tree, then it purges the cached bytecode for every file it touched - a stale `.pyc` makes the reverted module never load, and every criterion then comes back green from a check that measured nothing |
| AC13 | in `verify_ac.py`, swallow `_BaseUnreadable` in `revert_check` and carry on with an empty blob | Given a git call that FAILS while reading the base revision, when the check reads it, then that is REPORTED rather than read as absent-at-base - deleting the production file on an unanswerable question manufactures the red this gate exists to look for |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | Goal review round 2: the pinned regression case named a commit that holds the REPAIR, not the defect, and the ledger it would read is gitignored - re-pinned as a named fixture. Exemption taxonomy added, without which the check refuses correct units |
| 2026-08-21 | sdlc-studio | `Affects` extended with the generated verb catalogue: `command_audit --coverage` reads it, and the new verbs are absent from it until `docgen surface` runs |
| 2026-08-21 | sdlc-studio | The full suite refused twice on guards this work tripped: `git -C` does not override an inherited repo-locating variable, and this check WRITES what git hands it, so the scrub carries the full list and is registered where every other copy is pinned. `Affects` extended to the registry that pins it |
| 2026-08-21 | sdlc-studio | Delivery review round 1 REJECTED this unit on six blocking findings. `Revert-check-exempt` gates the check and existed in no schema, so the versioned contract now carries it and `Affects` names the file |
