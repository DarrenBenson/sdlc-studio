# US0671: revert-check reverts a unit's production files and REFUSES when its own verifiers stay green

> **Status:** Draft
> **Delivers:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Verification depth:** functional [[derived: criteria 5; plan rows 6; executed 6; killed 6; survived 0; not-run 0; entry point 5 of 5 criteria through the shipped CLI, 0 in-process | fp 3a9c3f123a3e ]] (the whole command is exercised through `verify_ac.py revert-check` against real git repositories with real files on disk, because the subject is what happens to bytes while it runs. NOT covered: a unit whose production file was ADDED by the change and so does not exist at the base ref - the revert deletes it, which is right, but no criterion pins that path)
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

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `verify_ac.py`, delete the `if counted and not result["red"]` branch from `revert_check`, so a unit whose every measurable criterion stays green returns `pass` | Given a unit ALL of whose non-exempt criteria stay green after its `Affects` production files are reverted to the base ref, when `verify_ac.py revert-check` runs, then it exits non-zero and names each such criterion - green after the revert is the REFUSAL, because a test that passes without the change never reached it |
| AC2 | in `verify_ac.py`, replace `not result["red"]` with `green` in `revert_check`'s refusal condition, so it refuses whenever ANY criterion stays green | Given a unit whose verifiers genuinely exercise the shipped path, when the same revert-and-run happens, then the unit PASSES - the paired control, so the gate is shown to discriminate rather than to refuse everything put in front of it |
| AC3 | in `verify_ac.py`, return `{}` from `revert_exemptions` | Given a unit whose only green criteria are DECLARED EXEMPTIONS - a declared control, a well-formed `unnameable` row, or a criterion whose subject is a test file rather than production code - when the check runs, then it does NOT refuse the unit. RUN-01M0CT8P measured five criteria in this class across one batch, so a check without this taxonomy refuses correct work, and refusing correct work is how a gate gets switched off |
| AC4 | in `verify_ac.py`, invert the run classification in `revert_check` - `"red" if res.ok else "green"` | Given a FIXTURE reproducing the pre-repair working-tree state of BG0593 - the production change present, and its tests rebuilding the scratch in a private helper so the change is unexercised - when the check runs, then it REFUSES. Stated as a fixture and not as a commit BY NECESSITY: that state was never committed, it existed between 788e0c3f and its repair at 20de1d1c, and the mutation ledger it would otherwise be read from lives in gitignored `sdlc-studio/.local/`. A criterion claiming to pin a commit that does not hold the defect is a fabricated regression case, which is the defect class this very check exists to refuse |
| AC4 | in `verify_ac.py`, skip the revert loop in `revert_check` and run the verifiers against the intact tree | Given a FIXTURE reproducing the pre-repair working-tree state of BG0593 - the production change present, and its tests rebuilding the scratch in a private helper so the change is unexercised - when the check runs, then it REFUSES. Stated as a fixture and not as a commit BY NECESSITY: that state was never committed, it existed between 788e0c3f and its repair at 20de1d1c, and the mutation ledger it would otherwise be read from lives in gitignored `sdlc-studio/.local/`. A criterion claiming to pin a commit that does not hold the defect is a fabricated regression case, which is the defect class this very check exists to refuse |
| AC5 | in `verify_ac.py`, delete the `selector_resolves(...) is False` arm from `revert_check`, so an unresolvable selector is executed and its non-zero exit counted red | Given a criterion whose `Verify:` line names a selector that does not resolve, when the check runs, then it reports UNRESOLVED for that criterion and does NOT count it as red - a selector failing because it names nothing is not a test reaching the change, and counting it as one is how this gate would manufacture a false pass |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | Goal review round 2: the pinned regression case named a commit that holds the REPAIR, not the defect, and the ledger it would read is gitignored - re-pinned as a named fixture. Exemption taxonomy added, without which the check refuses correct units |
| 2026-08-21 | sdlc-studio | `Affects` extended with the generated verb catalogue: `command_audit --coverage` reads it, and the new verbs are absent from it until `docgen surface` runs |
| 2026-08-21 | sdlc-studio | The full suite refused twice on guards this work tripped: `git -C` does not override an inherited repo-locating variable, and this check WRITES what git hands it, so the scrub carries the full list and is registered where every other copy is pinned. `Affects` extended to the registry that pins it |
| 2026-08-21 | sdlc-studio | Delivery review round 1 REJECTED this unit on six blocking findings. `Revert-check-exempt` gates the check and existed in no schema, so the versioned contract now carries it and `Affects` names the file |
