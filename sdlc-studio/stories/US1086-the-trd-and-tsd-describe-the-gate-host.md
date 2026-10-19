# US1086: The TRD and TSD describe the gate host a clone can configure, the fallback and the local override

> **Status:** Draft
> **Delivers:** CR0644
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, sdlc-studio/tsd.md, tools/tests/test_lean_gate_host_docs.py, changelog.d/US1086.md
> **Epic:** EP0290
> **Points:** 2
> **Depends on:** US1075, US1084
> **Persona:** Maya Okafor

## User Story

**As** the skill maintainer configuring a gate host for this clone
**I want** the TRD and TSD to describe where the push gate runs, how a clone configures a host, the fallback and the local override
**So that** configuring the remote gate needs only the documents, and nobody believes a failed transport fell back to the local gate silently

## Acceptance Criteria

- **AC1:** Given every `git config` key and environment variable `.githooks/pre-push`, `tools/remote-gate.sh`, `tools/run-suite.sh` and `tools/enable-hooks.sh` read to choose or report where the gate runs, when the TRD and TSD are read, then each is named
  - **Verify:** pytest tools/tests/test_lean_gate_host_docs.py::GateHostDocsTests::test_every_gate_host_setting_is_named
- **AC2:** Given the push stage of the TSD, when it is read, then it says where the gate runs with a host configured, with none, and with `SDLC_GATE_LOCAL=1`, and that a transport failure refuses the push rather than running the gate locally
  - **Verify:** pytest tools/tests/test_lean_gate_host_docs.py::GateHostDocsTests::test_the_push_stage_names_each_gate_location

## Notes

- AC1 must fail on: a setting the hook or remote-gate.sh reads left unnamed in either document; the set is read from the scripts, never typed into the test.
- AC2 must fail on: the TSD saying a transport failure falls back to the local gate, or one of the three locations unnamed.
- Every derived set asserts a known member first (LL0043): `sdlc.gateHost` and `SDLC_GATE_LOCAL`.
- Depends on US1075, which ships the configuration, and on US1084, which writes the stage this extends.
- Covers CR0644 AC5. Persona to be repointed to the skill-maintainer card once US1079 lands.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | Claude Opus 5.5 | Groomed: criteria, Verify lines and the mutants each must fail on (D0377) |
| 2026-10-19 | Claude Opus 5.5 | Regroomed after the goal review (round 4): the seats' findings folded in: run-suite.sh and enable-hooks.sh among the sources, known-member floor |
