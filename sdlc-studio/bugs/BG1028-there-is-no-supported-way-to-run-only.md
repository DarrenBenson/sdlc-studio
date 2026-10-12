# BG1028: There is no supported way to run only the release verify lane: `gate.py --release --only verify` is refused for deselecting the bound lanes, and the refusal's advice (drop --release) leads to `unknown check name(s): verify`

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate_verify_lane_alone.py, .claude/skills/sdlc-studio/help/gate.md, changelog.d/BG1028.md
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-12T11:22:30Z

## Summary

Repairing a consuming project's AC corpus (437 red and 1,567 unspecified criteria) needs the release verify lane run on its own, repeatedly. `gate.py --release --allow-external --only verify` fails at selection: 'deselecting the bound lane(s) review-legs, versions, changelog-fragments proves nothing ... Drop the --skip/--only that excludes them, or drop the mode flag (--release ...) and run the standard gate' (gate.py ~2066-2078). Following that advice, `gate.py --only verify` fails with 'unknown check name(s): verify', because the verify lane is registered only under --release (gate.py ~2001). So the only routes are the whole --release gate (every other release lane too) or importing gate and calling the private `_verify_acs(root, allow_external=True, batch=True)`. The same shape bit filing: the consuming project's BG0555 carried `gate.py --release --only verify` as its own Verify line, which can never pass.

## Steps to Reproduce

In a consuming project: `python3 scripts/gate.py --release --only verify` -> selection FAIL (bound lanes deselected); then `python3 scripts/gate.py --only verify` -> `unknown check name(s): verify`.

## Proposed Fix

Either let `--only verify` select the verify lane in the standard gate (it is a read-only, dry-run lane), or give `verify_ac.py` a `gate-lane` subcommand that runs exactly `_verify_acs` and prints its verdict; and make the refusal's advice name a command that works.

## Acceptance Criteria

- [ ] **AC1** Given a workspace with one red executable criterion, when the documented command for the release verify lane alone runs, then it exits non-zero naming that criterion, and with the criterion green it exits 0, without running any other release lane
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_verify_lane_alone.py::VerifyLaneAloneTests::test_the_verify_lane_runs_alone_and_decides
- [ ] **AC2** Given `gate.py --release --only verify`, when the selection is refused for the bound lanes, then the refusal names a command that runs the verify lane alone, and that command is accepted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_verify_lane_alone.py::VerifyLaneAloneTests::test_the_refusal_names_a_command_that_works

## Impact

Corpus repair loops have to run the whole release gate or a private function; an AC verifier naming the natural command can never pass.

## Triage

- Reproduced at 4932cf5d: `gate.py --release --allow-external --only verify` fails selection ('deselecting the bound lane(s) review-legs, versions, changelog-fragments proves nothing ...'), and following its advice, `gate.py --only verify` fails 'unknown check name(s): verify', because the verify lane is registered only under `--release`. Pre-existing.
- Severity Low stands; the private project name is generalised; criteria split in two on a new test module (BG0980), so the refusal's advice is tested on its own.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Filed |
| 2026-10-12 | Claude Opus 5.5 (triage) | Triaged: reproduced; project name generalised; criteria on a new test module; changelog fragment named for the unit |
