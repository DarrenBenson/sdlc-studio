# US1114: remote-gate.sh runs one commit's release gate on the gate host and records it green only when the host passed it

> **Status:** Ready
> **Delivers:** CR0660
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/remote-gate.sh, tools/tests/test_remote_gate_release.py, changelog.d/US1114.md
> **Epic:** EP0296
> **Points:** 3
> **Persona:** Rowan Achterberg

## User Story

**As a** the skill maintainer releasing a version (Rowan)
**I want** `tools/remote-gate.sh push --commit <sha> --release` to run that commit's own `gate.py --release` on the gate host
**So that** the pre-tag gate stops occupying the workstation, and its green names exactly the commit it judged

## Acceptance Criteria

- **AC1:** Given a gate host, when `remote-gate.sh push --commit <sha> --release` runs, then the host runs `gate.py --release` in a checkout of exactly <sha>, and the local exit is 0 only for the host's pass and 1 for its refusal (3 and 4 keep their meanings)
  - **Verify:** pytest tools/tests/test_remote_gate_release.py::RemoteReleaseGateTests::test_the_host_runs_the_commits_own_release_gate
- **AC2:** Given `SDLC_VERIFY_TIMEOUT` and `SDLC_VERIFY_WORKERS` set locally to positive integers, when the release gate runs on the host, then the host's gate reads the same values, and a value that is not a positive integer is refused by name before any connection is made
  - **Verify:** pytest tools/tests/test_remote_gate_release.py::RemoteReleaseGateTests::test_the_verify_settings_reach_the_host_and_a_bad_value_is_refused
- **AC3:** Given the host's release gate passed on <sha>, then `sdlc-studio/.local/release-gate-green.json` names exactly <sha>; given it refused, or the connection failed, then the marker is byte-identical to before
  - **Verify:** pytest tools/tests/test_remote_gate_release.py::RemoteReleaseGateTests::test_green_is_recorded_only_for_the_sha_the_host_passed

## Notes

- Serves: Rowan Achterberg, End goal 3 (a release a consuming team can upgrade to). CR0660; D0399.
- AC1 must fail on: the host job running `gate.py --boundary release`, which binds no verify lane, or a refusal exiting 0.
- AC2 must fail on: the variables not forwarded, so the host uses 300 s, or forwarded unvalidated, so a value containing `;` reaches the remote command line.
- AC3 must fail on: green recorded before the exit code is read, or on any exit, or HEAD recorded instead of <sha>. Use the fake-ssh fixture that `test_remote_gate_runs.py` already uses.
- Risks: the host job exports `SDLC_STUDIO_BOUNDARY_SUITE=1` today and a local `gate.py --release` does not; choose parity on purpose, or boundary_only verifiers change verdict between routes. The host lock (US1076) serialises this job with every clone's pushes for as long as it runs. Write the marker through `release_cut.record_green`; `tag-check` still asks the forge. The shipped toolchain runbook (section 6) is Maya's surface and is not edited here: name the route in the script's usage header.
- Overlaps: CR0635 and US1075 (the remote gate), US1076 (the lock), BG1028. Independent of US1113's files, so it can build beside it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-02 | Claude Opus 5.5 (grooming) | Groomed under D0399 from the run-five planning pass: user story, criteria with Verify lines, mutants and risks |
