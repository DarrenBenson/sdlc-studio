# CR-0111: verify_ac batch mode - run the test runner once, not a cold start per AC

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

verify_ac executes each AC's Verify line as its own subprocess (scripts/verify_ac.py run_verifier), so a story/batch with N runner-targeted ACs spawns the runner N times. A field agent verifying a sprint measured ~1.5s per jest cold start x ~48 ACs = 70+ seconds - 48 cold starts for what one 'jest --json' run could resolve. Add a batch mode: for runner verbs (jest/pytest/vitest), run the suite ONCE with a JSON reporter, build a {test-id -> outcome} map, and resolve each AC's runner-targeted Verify line against that map. Linear cold-start cost collapses to one run.

## Acceptance Criteria

- [ ] verify_ac gains a batch mode that, for jest/pytest/vitest verbs across a story or --batch of stories, runs each distinct runner once with a JSON reporter and resolves every matching AC against the cached result map (no per-AC runner spawn)
- [ ] non-runner verbs (file/grep/http/shell/manual) and the no-JSON fallback still use the per-AC path; verdicts are identical to the per-AC path (a parity test asserts same pass/fail)
- [ ] the batch run is materially faster on suites with many runner-targeted ACs (one cold start, not N); the verify-report.json is produced from the single run
- [ ] documented in reference-verify.md; unit test: one suite result resolves multiple ACs + parity with per-AC; CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
