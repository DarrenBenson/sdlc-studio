# BG0646: status.py takes 113 seconds on this corpus, so the command every session is ordered to run first times out under a two-minute tool default

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Created:** 2026-09-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

AGENTS.md orders every session to run status second, before acting. Measured on 2026-09-04 over 814 stories and 644 bugs: 113 s wall clock (rc 0), and an earlier invocation in the same session was killed by a 120 s tool timeout with the output lost. A read-only dashboard that costs two minutes is one an agent learns to skip, which is the failure mode AGENTS.md names for this repository. The cost is not stated by the command and nothing prints before the census completes.

## Steps to Reproduce

1. time python3 .claude/skills/sdlc-studio/scripts/status.py on this tree. 2. Observe about 113 s with no output until the end. 3. Run it under a 120 s tool timeout and observe the kill.

## Proposed Fix

Profile the census: the likely cost is per-artefact parsing repeated across the requirements, bugs, reviews and backlog passes plus the already-delivered advisory's pairwise title comparison over 256 open artefacts. Parse each artefact once and share the census across passes, cache the parse keyed on file mtime under sdlc-studio/.local, print the headline lines before the advisories, and record the measured duration in gate-timings so a regression is visible. Target: under 15 s on this corpus.

## Acceptance Criteria

- [ ] **AC1** Given this corpus, when status.py runs, then it completes in under 15 s and prints the headline lines before any advisory
  - **Verify:** manual - time the command on this tree; the executable verifier is authored when this is groomed, because its test does not exist yet
- [ ] **AC2** Given a fixture corpus, when status.py runs twice, then the second run reads the cached census and every artefact file is parsed at most once per run
  - **Verify:** manual - the executable verifier is authored when this is groomed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
