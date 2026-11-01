# BG1157: No test pins that a --host prerequisite check still names a missing markdownlint, so widening PUSHER_ONLY to it stays green

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_gate_prereqs.py
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, BG1138 APPROVE by qa-seat-BG1138-r1 (brief 771df035cf0c).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T05:14:39Z

## Summary

qa-seat-BG1138-r1's APPROVE of BG1138 (2026-11-01): changelog.d/BG1138.md:9 says both host checks still name a missing rg or markdownlint as a note, and the test is named `test_a_host_check_leaves_out_gh_and_nothing_else`, but every --host check stubs markdownlint as present (tools/tests/`test_gate_prereqs.py`:204, 208, 211) or asserts only the rg note (:240, :244). The mutant `PUSHER_ONLY = frozenset({"gh", "markdownlint"})` (tools/`gate_prereqs.py`:58) passes four modules (29 passed). The claim is true at HEAD by execution.

## Steps to Reproduce

1. Set `PUSHER_ONLY` to {gh, markdownlint} in a throwaway worktree.
2. Run `test_gate_prereqs.py`, `test_remote_gate_doctor.py`, `test_pre_push_prereqs.py` and `test_remote_gate_push.py`: green.

## Proposed Fix

Assert `note: markdownlint is not found` on the doctor run, whose fixture PATH already lacks markdownlint.

## Acceptance Criteria

- [ ] **AC1** The host-scope test fails when `PUSHER_ONLY` also leaves out markdownlint.
  - **Verify:** pytest tools/tests/test_gate_prereqs.py

## Impact

A later edit could hide a missing markdownlint on the gate host and the suite would not notice.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
