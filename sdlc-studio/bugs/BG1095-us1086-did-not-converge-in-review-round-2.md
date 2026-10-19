# BG1095: US1086 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, sdlc-studio/tsd.md, tools/tests/test_lean_gate_host_docs.py, changelog.d/US1086.md
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T20:48:21Z

## Summary

US1086 was rejected at round 2, the review cap, by qa-seat-US1086-r1, so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the AC2 fall-back scan's transport trigger is still a fixed phrase list (tools/tests/test\_lean\_gate\_host\_docs.py:67), but its comment says "however a sentence words it" (:66), its docstring says "in any wording and in either document" (:87-88), and the repair commit claims "a dropped or failed connection". Each of these, added alone to the TSD push stage, leaves test\_the\_push\_stage\_names\_each\_gate\_location green: "A dropped connection falls back to the local gate." (N1), "A failed connection falls back to running the gate here." (N3), "If the connection to the host fails, the gate runs here." (N2), "If the host is down, the hook falls back to the local gate." (N4) and "When ssh cannot connect, the gate runs locally." (N5). This is round 1's blocking fall-back finding, OVER-CLAIMED. It closes either by making the trigger catch these wordings (the words appearing together rather than as set phrases) or by making the comment and docstring state the list the test actually covers; BLOCKING: [new] the scan accepts a fall-back if NEGATES (:69) matches anywhere in the same clause, not on the fall-back it governs (:114-116), so a negation of some other "run" excuses it. "A transport failure falls back to the local gate and does not run on the host." (N7), which is the story's named mutant in the criterion's own words, passes when added to the TSD. So do "A host that cannot be reached falls back to the local gate rather than running on the host." (N6) and "A host that cannot be reached never runs the gate and falls back to this machine." (N9). Replacing the TRD's sentence with "A host that cannot be reached falls back to the local gate rather than running the gate there." (N8) also passes, so the TRD can be made to say the opposite of the hook. This is round 1's "guard accepts any not, rather than or never", MOVED rather than closed; [new] low: the location checks still pass some wrong-way sentences. The host check (:93-95) accepts any "there" in a "gateHost set" sentence, so "...to that host, but the gate runs on this machine, not there, through..." passes (N11). The override check (:103-105) refuses only three set phrases, so "`SDLC_GATE_LOCAL=1 git push` runs it on this machine for one push, but only where `sdlc.gateHost` is empty." passes (N10). Round 1's B9, B13 and B14 are killed, so this does not hold the gate; [pre-existing] AGENTS.md still says `python3 tools/gate_timing.py estimate --suite boundary-push --warn-seconds 0` prints the current push figure. On this clone, which names a gate host, that is the local series, which a host run never enters (.githooks/pre-push:222 and :259). It is outside US1086's Affects, and no open Bug or CR covers it

## Steps to Reproduce

1. Read the round 2 REJECT of US1086 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US1086 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the AC2 fall-back scan's transport trigger is still a fixed phrase list (tools/tests/test\_lean\_gate\_host\_docs.py:67), but its comment says "however a sentence words it" (:66), its docstring says "in any wording and in either document" (:87-88), and the repair commit claims "a dropped or failed connection". Each of these, added alone to the TSD push stage, leaves test\_the\_push\_stage\_names\_each\_gate\_location green: "A dropped connection falls back to the local gate." (N1), "A failed connection falls back to running the gate here." (N3), "If the connection to the host fails, the gate runs here." (N2), "If the host is down, the hook falls back to the local gate." (N4) and "When ssh cannot connect, the gate runs locally." (N5). This is round 1's blocking fall-back finding, OVER-CLAIMED. It closes either by making the trigger catch these wordings (the words appearing together rather than as set phrases) or by making the comment and docstring state the list the test actually covers
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: BLOCKING: [new] the scan accepts a fall-back if NEGATES (:69) matches anywhere in the same clause, not on the fall-back it governs (:114-116), so a negation of some other "run" excuses it. "A transport failure falls back to the local gate and does not run on the host." (N7), which is the story's named mutant in the criterion's own words, passes when added to the TSD. So do "A host that cannot be reached falls back to the local gate rather than running on the host." (N6) and "A host that cannot be reached never runs the gate and falls back to this machine." (N9). Replacing the TRD's sentence with "A host that cannot be reached falls back to the local gate rather than running the gate there." (N8) also passes, so the TRD can be made to say the opposite of the hook. This is round 1's "guard accepts any not, rather than or never", MOVED rather than closed
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** The round 2 REJECT finding no longer holds: [new] low: the location checks still pass some wrong-way sentences. The host check (:93-95) accepts any "there" in a "gateHost set" sentence, so "...to that host, but the gate runs on this machine, not there, through..." passes (N11). The override check (:103-105) refuses only three set phrases, so "`SDLC_GATE_LOCAL=1 git push` runs it on this machine for one push, but only where `sdlc.gateHost` is empty." passes (N10). Round 1's B9, B13 and B14 are killed, so this does not hold the gate
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC4** The round 2 REJECT finding no longer holds: [pre-existing] AGENTS.md still says `python3 tools/gate_timing.py estimate --suite boundary-push --warn-seconds 0` prints the current push figure. On this clone, which names a gate host, that is the local series, which a host run never enters (.githooks/pre-push:222 and :259). It is outside US1086's Affects, and no open Bug or CR covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC5** US1086 AC1 still passes: Given every `git config` key and environment variable `.githooks/pre-push`, `tools/remote-gate.sh`, `tools/run-suite.sh` and `tools/enable-hooks.sh` read to choose or report where the gate runs, when the TRD and TSD are read, then each is named
  - **Verify:** pytest tools/tests/test_lean_gate_host_docs.py::GateHostDocsTests::test_every_gate_host_setting_is_named
- [ ] **AC6** US1086 AC2 still passes: Given the push stage of the TSD, when it is read, then it says where the gate runs with a host configured, with none, and with `SDLC_GATE_LOCAL=1`, and that a transport failure refuses the push rather than running the gate locally
  - **Verify:** pytest tools/tests/test_lean_gate_host_docs.py::GateHostDocsTests::test_the_push_stage_names_each_gate_location

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Filed |
