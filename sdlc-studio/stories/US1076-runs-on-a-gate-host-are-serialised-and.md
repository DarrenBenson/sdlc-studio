# US1076: Runs on a gate host are serialised, and an abandoned push stops its run

> **Status:** In Progress
> **Delivers:** CR0635
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/remote-gate.sh, tools/tests/test_remote_gate_runs.py, changelog.d/US1076.md
> **Epic:** EP0288
> **Points:** 3
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer whose agent sessions push to one shared gate host
**I want** each host run to have its own tree, one run at a time, and an abandoned push to leave nothing running
**So that** a retry after a dropped connection cannot delete a live run, and two sessions pushing at once do not starve the host the way they starved the workstation

## Acceptance Criteria

- **AC1:** Given two runs of the same commit on one host through the stubbed transport, when both start, then each has its own directory and neither removes the other's tree
  - **Verify:** pytest tools/tests/test_remote_gate_runs.py::GateHostRunTests::test_each_run_has_its_own_tree
  - **Verified:** yes (2026-10-19)
- **AC2:** Given a run in progress on the host, when a second run starts, then it waits on a host-side lock, says it is waiting and for which run, and starts when the first ends
  - **Verify:** pytest tools/tests/test_remote_gate_runs.py::GateHostRunTests::test_a_second_run_waits_and_says_so
  - **Verified:** yes (2026-10-19)
- **AC3:** Given a hook stopped by INT or TERM, or a transport that drops mid-run, when the push ends, then it is refused and no tree or gate process for that run remains on the host
  - **Verify:** pytest tools/tests/test_remote_gate_runs.py::GateHostRunTests::test_an_abandoned_push_leaves_nothing_running
  - **Verified:** yes (2026-10-19)

## Notes

- Serves: Rowan Achterberg, End goal 1 (D0380 repoint; the card is sdlc-studio/personas/rowan-achterberg-skill-maintainer.md).
- Release: 6.2 (second run, D0365) (refine breakdown G14, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the run directory is keyed only on the commit and removed before reuse, as the trial script did
- AC2 must fail on: no lock, so both suites run at once
- AC3 must fail on: the remote gate is left running, or its tree left behind, after the local side goes
- Run the remote script under `set -o pipefail` and refuse a commit whose lockfile cannot be read: the trial's `git show ... | sha256sum` left a node directory keyed on the digest of empty input.

## Planning notes

- 2026-10-13: devserver1 is also a self-hosted GitHub Actions runner (`Runner.Worker`, `buildkitd`), so a host-side lock serialises gate runs against each other but not against the host's other work: the same push gate took 568 s and 836 s on one day, and BG1031's wall-clock test failed at load average 10.6. The doctor (US1077) or the run's output should report the host's load beside the result.

## Grooming note (2026-10-19)

- The lock and signal tests synchronise on events (a marker file, a pipe), never on wall-clock sleeps: they will run on a gate host shared with a CI runner, where wall-clock bounds have failed before (BG1031).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-12 | Claude Opus 5.5 (engineering seat) | Groomed from the refine breakdown G14 after the refine panel's review |
| 2026-10-13 | Claude Opus 5.5 (planning) | Note: the gate host is shared with a CI runner |
| 2026-10-19 | Claude Opus 5.5 | Regroomed after the goal review (round 4): the seats' findings folded in: event-synchronised lock and signal tests |
| 2026-10-19 | Claude Opus 5.5 | Repointed at Rowan Achterberg, Primary for the repository-tooling interface, before review (D0379, D0380) |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387): cleared Depends on; every dependency it named is terminal |
