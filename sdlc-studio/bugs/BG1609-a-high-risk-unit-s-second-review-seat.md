# BG1609: A high-risk unit's second review seat defaults to engineering, the seat that built it, so the engineering brief's printed record command is a self-review

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py, changelog.d/BG1609.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** run eighteen, 2026-11-19, US1238: `critic.py brief --unit US1238 --seat engineering` printed the record line with --reviewer 'Dani Okafor (engineering)' and the self-review note; runs sixteen and seventeen recorded only the QA seat on high-risk units
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T12:41:23Z

## Summary

`sprint plan` gives every high-risk unit a second review seat of engineering, and `sprint lane brief` builds every unit under the engineering seat by default, so the builder and the second seat are the same seat holder. `critic.py brief --seat engineering` then prints a record command with `--reviewer` set to the author and a note that it is a self-review, telling the orchestrator to brief another seat, but the plan names no other. The orchestrator must invent a reviewer id to keep D0523's second seat, and run seventeen skipped the seat altogether.

## Steps to Reproduce

Plan a batch holding a unit tagged Risk-class high, build it with `sprint lane brief` (no --seat) and `lane land --author 'Dani Okafor (engineering)'`, then run `critic.py brief --unit <id> --seat engineering`: the record line names 'Dani Okafor (engineering)' as reviewer and a note calls it a self-review.

## Proposed Fix

Choose the second seat as a seat other than the building seat (product when the builder is engineering), or have the lane brief name the building seat and the plan pick the second seat against it, so the printed record command is never a self-review.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint plan` gives every high-risk unit a second review seat of engineering, and `sprint lane brief` builds every unit under the engineering seat by default...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Plan a batch holding a unit tagged Risk-class high, build it with `sprint lane brief` (no --seat) and `lane land --author 'Dani Okafor (engineering)'`, then...
- [ ] **AC3** The proposed fix lands, pinned by a test: Choose the second seat as a seat other than the building seat (product when the builder is engineering), or have the lane brief name the building seat and the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
