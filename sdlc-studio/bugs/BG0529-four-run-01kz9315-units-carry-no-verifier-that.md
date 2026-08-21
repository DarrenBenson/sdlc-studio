# BG0529: four RUN-01KZ9315 units carry no verifier that enters the shipped entry point, so the wiring each one exists to add is pinned by nothing

> **Status:** Fixed
> **Verification depth:** functional (four CLI lane tests driving the shipped verbs in subprocesses; lane-check confirmed clear for all four units, and each unit's two criteria execute; mutation: 5 declared mutants, all KILLED - two were re-chosen after surviving because they patched a message rather than the resolver, and one registered verdict was RETRACTED on the record after executing it showed it survived; restore byte-exact)
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_sprint_report.py
> **Evidence:** RUN-01KZ9315 close, 2026-08-06, commit c82d1248. Baselined with a stated reason in sdlc-studio/.validate-warning-baseline.json rather than repaired, because a finding surfaced during a close is filed and deferred - the rule that gives the close a fixed point. A baselined entry is reported stale and removable once fixed, never re-spendable.
> **Created:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`lane-check` names four units of RUN-01KZ9315 - US0640, US0642, US0644, US0645 - each of which changes a command and none of whose verifiers drives that command. Every criterion is pinned in-process only.

The wiring is not unverified: both adversarial seats drove each mechanism through the CLI and reported the transcripts, and the run's own delivery exercised them by hand. What is missing is an AUTOMATED lane test - so the wiring is verified for today and pinned by nothing for tomorrow, which is precisely the state `critic.py brief --tier` was in for a whole sprint while `brief_fingerprint(brief(...))` passed in-process and the shipped verb printed nothing.

US0640's entry is worth separating from the other three. It appeared only because this close widened the unit's `Affects` to name `config.py` and `triage_noise.py`, where its AC4 actually landed. The lane is reporting a surface that was always there and was previously hidden by an understated footprint - the check got better, not the code worse.

## Steps to Reproduce

1. `git commit` on the RUN-01KZ9315 close. 2. The `warning-ratchet` lane fails, printing four LANE-CHECK lines: `US0640 ... this unit changes a command (plan_review.py, config.py, triage_noise.py) and NONE of its 4 verifier(s) enters the shipped entry point`, and the same shape for US0642 (critic.py), US0644 (critic.py) and US0645 (`sprint_report.py).`

## Proposed Fix

Add one CLI lane test per unit, driving the shipped verb in a throwaway fixture and asserting on its exit code and output rather than on a return value: `plan_review` enablement via the command that consults it, `critic.py brief` at both tiers asserting the claim-inventory block's presence and absence, `critic.py signoff` asserting the capacity column reaches the written row, and `sprint_report.py operator-summary` asserting the rendered page rather than the dict. Each already has a hand-run transcript from this run's review to assert against, so the expected output is not being invented.

CR0520 is the standing fix for the class - `verify_ac lane-check` gating a unit that changes a command and has no lane verifier - and this bug is four instances to close under it rather than a separate mechanism.

## Acceptance Criteria

- [x] **AC1** Given each of US0640, US0642, US0644 and US0645, when `verify_ac lane-check` sweeps the corpus, then none of them is named - each now carries a verifier that enters the shipped entry point.
  - **Verify:** shell test $(python3 .claude/skills/sdlc-studio/scripts/verify_ac.py lane-check 2>&1 | grep -cE "LANE-CHECK: US064[0245]") -eq 0
  - **Verified:** yes (2026-08-15)
- [x] **AC2** Given the three lane modules this unit adds, when they run together, then every one passes - the four behaviours themselves belong to the four stories' own criteria, and restating them here would leave two criteria sharing one selector and neither discriminating.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_critic.py .claude/skills/sdlc-studio/scripts/tests/test_lane_plan_review.py .claude/skills/sdlc-studio/scripts/tests/test_lane_sprint_report.py
  - **Verified:** yes (2026-08-15)

## Resolution

Four CLI lane tests, one per unit, driving the shipped verb in a subprocess and asserting on exit code and OUTPUT rather than on a return value. Each unit gained a criterion naming its lane test, which is what clears `lane-check` - the sweep reads a unit's own verifiers, so a lane test nothing points at closes nothing.

Two of the four tests were written weak and had to be replaced, which is the finding worth keeping. The sign-off test branched on the exit code with BOTH arms passing, so it could not fail either way; it now runs against a throwaway workspace and asserts the fields reach the written record. The operator-summary test asserted only that something printed and no traceback appeared, which no plausible change could break; it now asserts the specific words an absent record produces - `none recorded`, `unjudged`, `UNMEASURED` - and that no zero is printed for a cost nobody measured.

Two mutants also had to be re-chosen after surviving: one patched a message rather than `active()`, the behavioural resolver, and one never applied at all because its anchor was not unique. Both looked like evidence.

The tests were split by subject - `test_lane_critic.py`, `test_lane_sprint_report.py`, `test_lane_plan_review.py` - rather than kept as one module. A single file spanning three scripts attributes to none of them and would have raised the census baseline a third time in one run; split, each attributes cleanly by reference and the baseline is untouched. Making the census right beat recording another exemption.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | swap a unit's lane verifier for an in-process pytest line, so lane-check names it again | lane-check names none of the four |
| AC2 | in critic.py `brief`, drop the tier gate so full and light print the same brief | the three lane modules all pass |

## A note on the criteria

The first cut carried one criterion per lane test, each naming the same selector as the story's
own new criterion. `verify-lint --ratchet` refused it, correctly: two ACs sharing a selector
cannot both discriminate, and a regression in either fails both while neither says which broke.
The four behaviours belong to the four STORIES; what belongs to this bug is that the units now
carry a lane verifier at all, and that the modules it adds pass.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
| 2026-08-21 | sdlc-studio | `Verification depth` stated a criterion count the artefact contradicts. Corrected, and the class is now gated by a census over every bug artefact so a new disagreement is refused rather than found by a reviewer |
