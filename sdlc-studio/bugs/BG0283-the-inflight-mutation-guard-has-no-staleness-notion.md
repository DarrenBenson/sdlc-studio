# BG0283: the inflight-mutation guard has no staleness notion, so an abandoned sidecar blocks every write in the repo indefinitely: a three-day-old file refused artifact and transition the moment the guard shipped

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py,.claude/skills/sdlc-studio/scripts/mutation.py
> **Severity:** Medium
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Hit within minutes of US0377 merging, in the ordinary course of work. `artifact.py new` refused:

```text
refused: a mutation run has a mutant applied to tools/tests/test_skill_tests_env.py - the
single-writer rule says one process rewrites a tree at a time ... Wait for the run to finish,
or - if no run is alive - restore the file(s) from git and delete .../mutation-inflight.json
```

Measured on the spot:

- the sidecar's mtime was **2026-07-21 18:50**, three days old
- `git diff` on the named file was EMPTY - the tree was never left mutated
- no `mutation.py` process was alive
- no agent worktree carried a sidecar of its own

So an abandoned artefact from a run that ended days ago was blocking every write in the
repository, and would have gone on doing so indefinitely.

**Why the existing recovery does not reach it.** `mutation.py::_recover_stranded` does restore a
stranded tree, which is the right thing - but it only runs when `mutation.py` RUNS. A project that
does not happen to start another mutation run never recovers, while `artifact.py` and
`transition.py` refuse on every invocation. The guard is correct to be conservative about a LIVE
run; it has no way at all to tell a live run from an abandoned one.

The refusal message is also missing the one fact that would let an operator judge it: how old the
claim is. "A mutation run has a mutant applied" reads as present tense for a three-day-old file.

## Impact

Any project that has ever had a mutation run killed - by a timeout, a crash, a cancelled agent.
The failure is total (every write refused) and self-perpetuating (nothing clears it but a manual
delete), and it lands on whoever writes next rather than on whoever abandoned the run.

## Acceptance Criteria

### AC1: the refusal states the age of the claim it is making

- **Given** a sidecar written some time ago
- **When** a writer refuses on it
- **Then** the message states when the run started, so an operator can tell a live run from an abandoned one without inspecting the file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_inflight_guard.py::StaleSidecarTests::test_the_refusal_states_how_old_the_claim_is

### AC2: a sidecar whose files are all unmutated is recognised as spent, not live

- **Given** a sidecar naming files that are byte-identical to their recorded originals
- **When** a writer consults the guard
- **Then** it does not refuse - nothing is mutated, so the single-writer rule has nothing to protect - and the spent sidecar is reported
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_inflight_guard.py::StaleSidecarTests::test_a_sidecar_with_nothing_actually_mutated_does_not_refuse

### AC3: a genuinely live run still refuses, unregressed

- **Given** a sidecar whose named file IS currently mutated
- **When** a writer consults the guard
- **Then** it refuses exactly as before - this must not become a way to write through a live mutation run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_inflight_guard.py::StaleSidecarTests::test_a_genuinely_mutated_file_still_refuses

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
