# CR-0645: Refresh the TRD to 6.2: delivery units that execute Verify lines, committed evidence and run records, the type registry, network paths and the stale ADRs

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Evidence:** RV0028 findings TRD-1 (Critical), TRD-5, TRD-6, TRD-7, TRD-8, TRD-10 to TRD-20 and TRD-23 to TRD-25; trd.md:395 'Only a story carries an executable verifier'; lib/sdlc_md.py:1633 `EXECUTES_VERIFIERS = ("story", "bug")` since 7479957e (2026-07-28); test_lean_v61_review_residue.py:155-176 passes on the legacy telemetry file name.
> **Date:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:48:07Z

## Summary

RV0028's TRD leg found the TRD accurate on its ADRs, script tiers, lane registries and ULID design, but behind on everything built since early August, outside the gate sections CR0644 covers. Most consequential: it says only a story carries an executable verifier, while `sdlc_md.EXECUTES_VERIFIERS` is (story, bug) and the Fixed gate depends on it; two code comments (`file_finding.py`:52-56, artifact.py:1091-1093) still say the same. It also misses the move of telemetry, lessons, verdict logs, reports and run records into committed storage, the two-tier run state and the close-and-sign lifecycle, the charter type and `META_TYPES`, three gh callers and the version-check GET, and ADR-003, ADR-009 and ADR-012 have drifted from what is built.

## Impact

A rebuild from the TRD would refuse the Verify lines the Fixed gate needs, and its storage blueprint omits the committed records every checkout now reads.

## Acceptance Criteria

- [ ] The TRD says stories and bugs execute their Verify lines and CRs and RFCs refuse a command-shaped one, naming `sdlc_md.EXECUTES_VERIFIERS` as the authority, and the two stale code comments say the same
- [ ] The TRD's storage sections list the committed evidence (actuals and forecasts shards, lessons.jsonl, the verdict logs, RPT reports, run records) and describe the live and tracked run state and the run lifecycle through close and sign
- [ ] The type registry lists charter with its vocabulary and names `META_TYPES`; the network section lists every gh caller and records the version-check GET as an ADR-004 exception
- [ ] ADR-003, ADR-009 and ADR-012 match what is built, ADR-012 carries a revision row, and the header's coverage line names v6.1.0 plus 6.2 on main
- [ ] The `.local` writer pin fails when a documented writer no longer writes the documented file

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Raised |
