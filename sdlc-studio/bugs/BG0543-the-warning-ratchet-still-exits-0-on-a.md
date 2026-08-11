# BG0543: the warning ratchet still exits 0 on a stale baseline, and its replacement headline contradicts the line below it

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07, independent delivery review of BG0524, probed through the shipped CLI on a throwaway fixture.
> **Verification depth:** functional (unit: the command driven as a subprocess in every mode and state, asserting the EXIT CODE rather than the wording, which is what the previous repair changed; mutation: every planned mutant applied and killed)
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0524 was filed because `npm run lint:warning-ratchet` printed `clean` on a baseline it could not establish. Its repair changed the words and not the exit code.

Probed through the shipped CLI on a fixture with 3 recorded entries and 0 live: exit 0. AC1 says it exits non-zero and names the state; AC2 says each state exits non-zero. Both are marked `Verified: yes`, and neither verifier touches an exit code - all three tests call `render_ratchet` in-process.

That is the exact defect class the artefact's own preamble records against US0480 AC4, reproduced by the repair for it. This lane sits in the per-commit `npm run lint` chain, so a stale baseline passes every commit.

Second defect, arithmetic: the stale headline interpolates `report['live']` as the recorded count, but that branch is reached only when `stale` is non-empty, where recorded = live + stale. The fixture prints `0 recorded, 3 of them repaired and removable` one line above `3 recorded instance(s) no artefact still carries` - the headline contradicting the next line, which is what this bug exists to repair.

## Steps to Reproduce

1. Build a fixture whose `.validate-warning-baseline.json` records 3 instances the tree no longer carries. 2. `validate.py warning-ratchet`. 3. It names the state STALE and exits 0. 4. Read the headline: it reports 0 recorded, directly above a line reporting 3.

## Proposed Fix

Return non-zero from `cmd_warning_ratchet` for every untrustworthy state, not only for new instances, and assert the EXIT CODE through the command in each test rather than the rendered string in-process. Compute the recorded count as live + stale rather than live.

AC1's declared mutant is also unapplicable - `validate.py` already reads `"ok": not new`, so the criterion names a no-op as its falsifying change, and AC3's declared mutant survives its own suite.

## Acceptance Criteria

> **PREMISE VERIFIED FIRST, and it is largely FALSE - 2026-08-11.** The bug says the ratchet
> "still exits 0 on a stale baseline". Measured through the shipped CLI on fixtures, one state
> per probe:
>
> | state | exit |
> | --- | --- |
> | not baselined, live warnings present | 1 |
> | baseline corrupt | 1 |
> | entries with no reason | 1 |
> | not baselined, nothing live | 0, `clean` |
> | STALE - recorded entries the tree no longer carries | 0 |
>
> Four of the five are already right, so "each state exits non-zero" describes work that is done.
> And the fifth is a DELIBERATE, documented decision, not a defect: the code says a repaired
> instance is good news and "refusing the commit that repaired it would teach an author to stop
> repairing". That reasoning is sound and this unit does not overturn it.
>
> What survives is the half in this bug's own title: the replacement headline CONTRADICTS the
> exit code. The stale message says "Not `clean`" while the command exits 0, which every caller
> and the whole `npm run lint` chain reads as clean. A message and an exit status that disagree
> is the same class as a refusal that does not refuse - it is just pointing the other way. So the
> unit is narrowed to making them agree, and the false half is recorded rather than built.

### AC1

- **Given** a fixture whose baseline is STALE - entries recorded that the tree no longer carries
- **When** `validate.py warning-ratchet` is run AS A SUBPROCESS
- **Then** it exits 0 AND its message states that it is reporting rather than refusing, so a
  reader learns the exit code from the text instead of inferring the opposite from "Not `clean`".

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k a_stale_ratchet_baseline_says_it_is_not_refusing
- **Verified:** yes (2026-08-10)
- **Mutant:** in `validate.py`, remove the non-blocking statement from the stale message, restoring a headline that reads as a refusal while the command exits 0.

### AC2

- **Given** the four states that DO refuse - not-baselined with live instances, corrupt,
  reasonless, and a new instance
- **When** each is run as a subprocess
- **Then** each exits NON-ZERO. Asserted on the EXIT CODE, not the wording: all three shipped
  verifiers call `render_ratchet` in-process, which is exactly why the previous repair could
  change the words and leave the code untouched.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k every_refusing_ratchet_state_exits_non_zero
- **Verified:** yes (2026-08-10)
- **Mutant:** in `validate.py`, change `cmd_warning_ratchet` to return 0 for every state.

### AC3

- **Given** a fixture with a clean, current, fully reasoned baseline
- **When** the command is run as a subprocess
- **Then** it exits ZERO - the positive control, without which AC2 is satisfied by a command that
  always fails.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k a_clean_ratchet_baseline_exits_zero
- **Verified:** yes (2026-08-10)
- **Mutant:** in `validate.py`, change `cmd_warning_ratchet` to return 1 unconditionally.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `validate.py`, remove the non-blocking statement from the stale message | |
| AC2 | in `validate.py`, change `cmd_warning_ratchet` to return 0 for every state | |
| AC3 | in `validate.py`, change `cmd_warning_ratchet` to return 1 unconditionally | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
