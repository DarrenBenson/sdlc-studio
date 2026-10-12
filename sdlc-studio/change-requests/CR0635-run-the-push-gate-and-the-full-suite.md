# CR-0635: Run the push gate and the full suite on a configured gate host over ssh, so a memory-starved workstation stops killing them

> **Status:** In Progress
> **Decomposed-into:** EP0288
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .githooks/pre-push, tools/remote-gate.sh, tools/tests/test_remote_gate.py, tools/enable-hooks.sh, AGENTS.md, CONTRIBUTING.md
> **Date:** 2026-10-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-12T10:33:03Z

## Summary

The push gate (`gate.py --boundary push`, the full suite plus the core lanes) took 26 to 64 minutes over its last five runs on the 8-core, 14 GB workstation this repo is developed on (`sdlc-studio/.local/gate-timings.json`), and the agent harness stopped it twice in a week, with the full suite six more times, because free memory ran low (2-3 GB free, load 17-20) while three agent sessions, an editor agent and review subagents shared the machine. Each kill forced a choice between a 50-minute retry and a `--no-verify` push. An idle machine on the LAN (devserver1: 8 cores, 14 GB, 10 GB available) can run the same gate. AGENTS.md still says a push gate takes 'about five minutes', a figure measured on 16 cores.

## Impact

The operator and every agent pushing from a workstation shared with other sessions: today the gate is either killed or bypassed, and a bypassed gate guards nothing (19415be3 reached main red that way on 2026-10-12).

## Acceptance Criteria

- [ ] Given a clone configured with a gate host, when a push runs the pre-push hook, then the commit being pushed is sent to the host, `gate.py --boundary push` runs there against exactly that commit, its output streams back, and its exit code decides the push
- [ ] Given a configured gate host that cannot be reached, when a push runs, then the hook refuses and names both the host and the local fallback, and never silently runs locally or passes
- [ ] Given a clone with no gate host configured, when a push runs, then the gate runs locally exactly as today
- [ ] Given a configured gate host, when the full suite is asked for before a commit through the documented wrapper, then it runs on the host against the working tree's staged state, and a red run there is red here

## Recommendation

Opt in per clone (`git config sdlc.gateHost <ssh host>`); send the commit with plumbing that runs no hooks (`git send-pack` to a bare repository on the host, never `git push`, which would run the local gate first), check it out into a fresh tree, and run the gate in a provisioned environment there (a venv with pytest, pytest-xdist and coverage; node with the pinned markdownlint). Correct AGENTS.md's 'about five minutes' to point at `gate_timing estimate`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | Claude Opus 5.5 (triage) | Raised |
