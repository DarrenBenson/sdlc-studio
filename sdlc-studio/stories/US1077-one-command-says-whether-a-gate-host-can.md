# US1077: One command says whether a gate host can judge a push

> **Status:** Draft
> **Delivers:** CR0635
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/remote-gate.sh, tools/enable-hooks.sh, tools/tests/test_remote_gate_doctor.py, CONTRIBUTING.md, changelog.d/US1077.md
> **Epic:** EP0288
> **Points:** 2
> **Depends on:** US1075
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer relying on a gate host
**I want** `tools/remote-gate.sh doctor` to check the host against the one prerequisite list, and `enable-hooks.sh` to show the configured host and that verdict
**So that** a host that has lost a prerequisite is named in seconds, not after a ten-minute run turns red

## Acceptance Criteria

- **AC1:** Given a fixture host home whose interpreter carries every entry on the prerequisite list US1004 creates, when `doctor` runs through the stubbed transport, then it exits 0 and names the host
  - **Verify:** pytest tools/tests/test_remote_gate_doctor.py::GateHostDoctorTests::test_a_complete_host_is_reported_ready
- **AC2:** Given the same home without pytest-xdist, when `doctor` runs, then it exits non-zero naming pytest-xdist and the install route
  - **Verify:** pytest tools/tests/test_remote_gate_doctor.py::GateHostDoctorTests::test_a_missing_prerequisite_is_named
- **AC3:** Given a clone with `sdlc.gateHost` set, when `tools/enable-hooks.sh` runs, then it prints the configured host and doctor's verdict
  - **Verify:** pytest tools/tests/test_remote_gate_doctor.py::GateHostDoctorTests::test_enable_hooks_names_the_host_and_its_verdict

## Notes

- Serves: Rowan Achterberg, End goal 1 (D0380 repoint; the card is sdlc-studio/personas/rowan-achterberg-skill-maintainer.md).
- Release: 6.2 (second run, D0365) (refine breakdown G14, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: doctor checks a hard-coded list of its own instead of the one list
- AC2 must fail on: doctor reports ready without checking each entry
- AC3 must fail on: enable-hooks.sh does not mention the gate host
- Decide presence with US1004's dist-info technique against a fixture home, so the test needs no network and no installer.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-12 | Claude Opus 5.5 (engineering seat) | Groomed from the refine breakdown G14 after the refine panel's review |
| 2026-10-19 | Claude Opus 5.5 | Repointed at Rowan Achterberg, Primary for the repository-tooling interface, before review (D0379, D0380); resolved dependencies cleared: US1004 |
