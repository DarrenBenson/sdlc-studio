# BG1679: transition.py moves a story from Draft to Ready without checking its Definition of Ready, so Draft to Ready to Done skips the gate BG0954 adds

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition_ready_gate.py, changelog.d/BG1679.md, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** Run twenty-one qa review of BG0954 (verdict 6ddbf7d546d3-fe5d33d6), marked pre-existing with no open bug covering it.
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T12:43:45Z

## Summary

BG0954 refuses Draft to Done when the Definition of Ready is unmet, but transition.py set --status Ready runs no readiness check of its own: a Draft story with no Affects and no Points moves to Ready, then to Done, and the Done gate reads it as having been Ready. Outside a sprint (where sprint plan refuses such a unit) nothing checks readiness on that path.

## Steps to Reproduce

In a fresh project, create a Draft story with criteria but no Affects or Points; run transition.py set --id US0001 --status Ready, then --status Done: both succeed.

## Proposed Fix

Run the same Definition of Ready check BG0954 uses on the move to Ready, refusing with the unmet items, and pin Draft to Ready to Done refused at the first step.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0954 refuses Draft to Done when the Definition of Ready is unmet, but transition.py set --status Ready runs no readiness check of its own: a Draft story with...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a fresh project, create a Draft story with criteria but no Affects or Points; run transition.py set --id US0001 --status Ready, then --status Done: both...
- [ ] **AC3** The proposed fix lands, pinned by a test: Run the same Definition of Ready check BG0954 uses on the move to Ready, refusing with the unmet items, and pin Draft to Ready to Done refused at the first...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
