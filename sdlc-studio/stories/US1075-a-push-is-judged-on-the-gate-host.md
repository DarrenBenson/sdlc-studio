# US1075: A push is judged on the gate host this clone configures

> **Status:** In Progress
> **Delivers:** CR0635
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-push, tools/remote-gate.sh, tools/tests/test_remote_gate_push.py, tools/tests/test_pre_push_hook.py, tools/tests/test_skill_tests_env.py, CONTRIBUTING.md, changelog.d/US1075.md
> **Epic:** EP0288
> **Points:** 5
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer pushing from a workstation shared with agent sessions
**I want** the pre-push gate to run on the gate host I configure for this clone, against exactly the commit I am pushing and the same range and tags my clone sees
**So that** a push is judged in full without competing for my workstation's memory, and a killed gate no longer leaves me choosing between a long retry and a bypass

## Acceptance Criteria

- **AC1:** Given a clone whose `sdlc.gateHost` names a host reached through a stubbed transport, an uncommitted edit that would flip the stub gate's verdict, and a push of a commit that is not HEAD, when the hook runs over a commit the host judges red, then the commit is sent without running a local hook, the stub gate records that it ran in the host's checkout of exactly that commit, and the push is refused
  - **Verify:** pytest tools/tests/test_remote_gate_push.py::RemoteGatePushTests::test_the_host_judges_exactly_the_pushed_commit
  - **Verified:** yes (2026-10-19)
- **AC2:** Given a pushed commit on top of origin/main and a release tag, when the host judges it, then the gate there computes the same pushed range and resolves the same latest tag as the local hook
  - **Verify:** pytest tools/tests/test_remote_gate_push.py::RemoteGatePushTests::test_the_host_sees_the_same_range_and_tag
  - **Verified:** yes (2026-10-19)
- **AC3:** Given a pushed tag and a configured host, when the hook runs, then the host judges the tagged commit at `--boundary release`, the known-issues check runs locally, and a green host run lets the push through with the host's output on the pusher's stderr
  - **Verify:** pytest tools/tests/test_remote_gate_push.py::RemoteGatePushTests::test_a_tag_is_judged_at_the_release_boundary_on_the_host
  - **Verified:** yes (2026-10-19)
- **AC4:** Given a configured host whose transport exits 255, before the gate starts or after it has started, when a push runs, then the hook refuses, naming the host and `SDLC_GATE_LOCAL=1`, and runs no gate locally on its own initiative
  - **Verify:** pytest tools/tests/test_remote_gate_push.py::RemoteGatePushTests::test_a_transport_failure_refuses_and_names_the_fallback
  - **Verified:** yes (2026-10-19)
- **AC5:** Given the same commit, when the push runs with no host configured, and again with a host configured and `SDLC_GATE_LOCAL=1`, then each runs the gate once in the local worktree, and with a host configured and neither, the gate runs on the host
  - **Verify:** pytest tools/tests/test_remote_gate_push.py::RemoteGatePushTests::test_the_gate_runs_where_the_configuration_says
  - **Verified:** yes (2026-10-19)
- **AC6:** Given a configured host and a red latest push run on main that is not acknowledged, or a prerequisite the host's interpreter lacks, when the hook runs, then it refuses before the host's gate runs: the red-main read stays local and runs before anything is sent, and US1005's preflight runs on the host's interpreter, in the host's checkout of the pushed commit, before that gate starts
  - **Verify:** pytest tools/tests/test_remote_gate_push.py::RemoteGatePushTests::test_the_host_path_keeps_the_red_main_read_and_the_preflight
  - **Verified:** yes (2026-10-19)
- **AC7:** Given this clone configured with `sdlc.gateHost` naming the gate host, when one of this repository's own pushes after this unit lands runs with no `--no-verify`, then the host judges it, and its duration is recorded under `boundary-push@<host>` in this clone's gate timings
  - **Verify:** manual: with `git config sdlc.gateHost devserver1` set, push without `--no-verify`, then `python3 tools/gate_timing.py estimate --suite boundary-push@devserver1 --warn-seconds 0` prints an expected figure from at least one recorded run

## Notes

- Serves: Rowan Achterberg, End goal 1 (D0380 repoint; the card is sdlc-studio/personas/rowan-achterberg-skill-maintainer.md).
- Release: 6.2 (second run, D0365) (refine breakdown G14, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the hook sends the working tree or HEAD instead of the pushed commit, or runs the gate locally
- AC2 must fail on: only the commit is sent, so the host's range widens to all history and its tag lookup fails
- AC3 must fail on: the host always runs `--boundary push`, or the host's output is discarded
- AC4 must fail on: a transport failure falls back to the local gate silently, or is read as a pass
- AC5 must fail on: `SDLC_GATE_LOCAL=1` is ignored, or the local path is taken with a host configured
- Send with `git send-pack` to a bare repository on the host, never `git push`, which runs this clone's pre-push gate first (it did in the 2026-10-12 trial and hung for ten minutes). Mirror `refs/remotes/*` and `refs/tags/*` with the commit: the panel probed that `gate.pushed_paths` (`git log HEAD --not --remotes`, gate.py:346) widens to all history without them, and the trial's host run judged 1074 story units and 3093 artefacts where a one-commit push judges a handful.
- One bare repository per clone on the host (keyed by a clone id), so one clone's mirrored refs never narrow another's range.
- Default transport `ssh -o BatchMode=yes -o ServerAliveInterval=60 -o ServerAliveCountMax=10 -- <host>`, overridable by `sdlc.gateSsh`: BatchMode because the hook's stdin is the ref list, the keepalive because the full-suite lane is silent while pytest's output is captured, and `--` so a host value cannot inject an option. `git send-pack` reaches the host through `GIT_SSH_COMMAND`, so the test shim serves `git-receive-pack` too.
- Stream the remote side over ssh's stdin from the pushed commit's own copy of `tools/remote-gate.sh`, never a copy installed on the host, which would drift.
- With a host configured, US1005's preflight runs on the host's interpreter. D0181's red-main read stays local and runs before the send; the host never needs `gh`.
- Record the host run's duration under `boundary-push@<host>` (or `boundary-release@<host>`) in this clone's gate-timings, never in the local series US1006 reads.
- A red host run's refusal names the host's log path and the remote re-run, not the local re-run the host exists to avoid.
- Panel correction on the trial: of its three red tests, `BoundaryMarkerReachesThePushTests` and `FrozenNotesTests` were BG0978; `test_gate.py::ModuleAloneLaneTests` failed its 3.0-second wall-clock bound at exactly 3.0 under the full parallel suite, and passed on the rerun.

## Grooming note (2026-10-19)

- AC6 must fail on: the host path skipping the red-main read (D0181) or the preflight (US1005), both previously Notes only. Corrected before the build: the preflight reads `requirements-dev.txt` from the repository it runs in, so on the host it can only run once the commit has arrived, in the host's checkout, before the gate; the red-main read alone runs before anything is sent.
- AC7 is the live proof the goal review asked for: every other criterion runs a stubbed transport. It also retires D0370's interim `--no-verify` rule for this clone.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-12 | Claude Opus 5.5 (engineering seat) | Groomed from the refine breakdown G14 after the refine panel's review |
| 2026-10-19 | Claude Opus 5.5 | Regroomed after the goal review (round 4): the seats' findings folded in: AC6 (red-main and preflight on the host path), AC7 (a real push judged on the host) |
| 2026-10-19 | Claude Opus 5.5 | Repointed at Rowan Achterberg, Primary for the repository-tooling interface, before review (D0379, D0380); resolved dependencies cleared: BG0976, BG0978, US1005, US1006 |
| 2026-10-19 | Claude Opus 5.5 | AC6 corrected before the build: the host's preflight runs in its checkout of the pushed commit, before the gate, since it reads that commit's requirements-dev.txt |
| 2026-10-19 | Claude Opus 5.5 | Repair after the round-1 REJECT: AC7's Verify line names a command that exists (`gate_timing.py estimate`, not the absent `show`) |
