# BG0869: status backlog lists fully decomposed requests as discovery options still to refine

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_status_decomposed_requests.py, changelog.d/BG0869.md, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Evidence:** backlog sweep 2026-10-01, status.py backlog output
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T10:05:22Z

## Summary

Found in the 2026-10-01 backlog sweep: after every open CR was decomposed into Ready stories, `status.py backlog` still prints 'Discovery backlog (options - refine requests / triage issues before it is work): 6' listing CR0534, CR0552, CR0559, CR0590, CR0592 and CR0603 (each with a Decomposed-into epic), so a reader is told six requests still need refining when none does.

## Steps to Reproduce

On this repository at a915ee32 run `status.py backlog`: the In Progress CRs, each with `Decomposed-into`, are listed under the 'refine requests before it is work' heading.

## Proposed Fix

List a request that has children separately from one awaiting refinement (e.g. 'in delivery via EPxxxx'), using the same child test `status.discovery_awaiting` already applies; keep the counts honest.

## Acceptance Criteria

- [ ] **AC1** Given a CR at In Progress with a Decomposed-into epic and a CR at Proposed with none, when `status.py backlog` runs, then only the undecomposed CR is listed as awaiting refinement and the decomposed one is shown with its epic. Fails on: HEAD, which lists both as options to refine
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_status_decomposed_requests.py::StatusDecomposedRequestTests::test_a_decomposed_request_is_not_listed_as_awaiting_refinement
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
