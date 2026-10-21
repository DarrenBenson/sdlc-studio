# BG1095: US1086 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, sdlc-studio/tsd.md, tools/tests/test_lean_gate_host_docs.py, changelog.d/US1086.md, sdlc-studio/stories/US1086-the-trd-and-tsd-describe-the-gate-host.md
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

- [ ] **AC1** The TRD's and the TSD's push-gate sections each state, in a table, where the gate runs for each configuration the scripts read (a gate host set, none, `SDLC_GATE_LOCAL=1`) and what a transport failure does, and the test compares both tables' cells exactly with those configurations; the fall-back phrase scan is gone
  - **Verify:** pytest tools/tests/test_lean_gate_host_docs.py::GateHostDocsTests::test_the_push_stage_tables_each_gate_location
- [ ] **AC2** US1086 AC1 still passes: every `git config` key and environment variable the four scripts read to choose or report where the gate runs is named in the TRD and the TSD
  - **Verify:** pytest tools/tests/test_lean_gate_host_docs.py::GateHostDocsTests::test_every_gate_host_setting_is_named

## Grooming note (2026-10-20)

- Goal review, 2026-10-21 (engineering, product and qa seats): the three carried findings (the fixed phrase trigger, the negation scope, the wrong-way sentences) all attack the fall-back phrase scan, which AC1 retires; the redelivery's reviewer rules each CLOSED, OVER-CLAIMED or MOVED rather than re-checking it by hand [LC-015]. The scan was also the only pin on the TRD's transport sentence, so AC1 covers the TRD's table too.
- Goal review amendment round, 2026-10-21 (engineering): the scan's test is US1086 AC2's stamped selector, so US1086's AC2 Verify line is re-pointed at AC1's test in the same commit, or the stamps lane refuses it; US1086 joins the Affects. (qa) AC1's expected cells are written in the test; the reviewer checks them against the hook's behaviour.
- AC1 must fail on: a table row missing or naming the wrong location; the TRD's sentence left as prose. AC2 must fail on: a setting the scripts read left unnamed.
- Dropped: the `[pre-existing]` item on AGENTS.md's push-figure command. It is BG1098's (filed again as BG1105 in error, and superseded by BG1098).
- The new AC1 takes RETRO0135's lesson (L-0002): a test of prose by phrase list never converged across US1084, US1085 and US1086. Stating the locations as a table that a test compares exactly retires the fall-back scan the carried findings each attack, rather than widening it a third time.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Filed |
| 2026-10-20 | Claude Opus 5.5 | Regroomed: criteria kept for the [new] non-info findings only (BG1079); see the grooming note |
| 2026-10-21 | Claude Opus 5.5 | Regroomed on the run-three goal review's two rounds (engineering, product and qa seats; D0384) |
