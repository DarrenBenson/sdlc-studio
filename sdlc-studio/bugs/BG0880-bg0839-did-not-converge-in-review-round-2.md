# BG0880: BG0839 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Closed with findings in:** BG0839's discharge: its rejecting reviewer's APPROVE answered every finding (RUN-01M3VF2J critic-verdicts)
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/eval_run.py, evals/README.md, tools/tests/test_lean_eval_isolation.py, tools/tests/test_eval_run.py, changelog.d/BG0839.md
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T17:04:25Z

## Summary

BG0839 was rejected at round 2, the review cap, by qa-seat reviewer (subagent af234d2d), so it was carried as a known issue rather than reviewed again. The findings still open: [regression] the writable-parent preflight refuses a --dir whose parent does not exist yet (tools/eval\_run.py:60, os.access on a missing path is False): scenario 09's documented --dir /tmp/evals-v6/09-lean-sprint is refused with exit 2 and a false not writable message when /tmp/evals-v6 is absent, where b0721a57 and the base built it - fix: test the nearest existing ancestor; [new] the printed SDLC\_STUDIO\_TRANSCRIPTS=<cfg>/projects points the token meter at the wrong directory: run\_state.session\_tokens (lib/run\_state.py:722) globs *.jsonl directly in that variable, while Claude Code writes <cfg>/projects/<slug>/*.jsonl, so the meter still finds nothing, and evals/README.md:30, the changelog and test\_lean\_eval\_isolation.py:88 pin the wrong value - fix: print <cfg>/projects/<str(dest) with / replaced by ->; [new] non-blocking: only the leaf of the symlink refusal is pinned (a leaf-only check survives)

## Steps to Reproduce

1. Read the round 2 REJECT of BG0839 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0839 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: [regression] the writable-parent preflight refuses a --dir whose parent does not exist yet (tools/eval\_run.py:60, os.access on a missing path is False): scenario 09's documented --dir /tmp/evals-v6/09-lean-sprint is refused with exit 2 and a false not writable message when /tmp/evals-v6 is absent, where b0721a57 and the base built it - fix: test the nearest existing ancestor
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [new] the printed SDLC\_STUDIO\_TRANSCRIPTS=<cfg>/projects points the token meter at the wrong directory: run\_state.session\_tokens (lib/run\_state.py:722) globs *.jsonl directly in that variable, while Claude Code writes <cfg>/projects/<slug>/*.jsonl, so the meter still finds nothing, and evals/README.md:30, the changelog and test\_lean\_eval\_isolation.py:88 pin the wrong value - fix: print <cfg>/projects/<str(dest) with / replaced by ->
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** The round 2 REJECT finding no longer holds: [new] non-blocking: only the leaf of the symlink refusal is pinned (a leaf-only check survives)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC4** BG0839 AC1 still passes: Given a scenario with a fixture spec, when `eval_run.py setup --scenario <id> --dir <scratch>` runs, then `<scratch>.claude-config/skills/sdlc-studio/SKILL.md` exists, nothing is written under `<scratch>` beyond the fixture, no credential file is written, and stdout carries a worker command beginning `CLAUDE_CONFIG_DIR=<scratch>.claude-config`. Fails on: HEAD, which builds no config directory and prints no command
  - **Verify:** pytest tools/tests/test_lean_eval_isolation.py::EvalIsolationTests::test_setup_isolates_the_candidate_skill
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
