# BG0315: cmd_set's one-call close neither pre-flights before writing nor passes pending_fields on dry-run: refused closes leave s

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

Two symptoms of the same missing pre-flight: (1) despite the comment claiming every predictable refusal comes before any write, only the bug depth gate is pre-flighted, so annotate and `critic.record_verdict` execute before transition() raises the other five gates' refusals - a refused close leaves a depth stamp and a persistent APPROVE verdict row for a close that never happened; (2) with --depth --dry-run the annotate is skipped and transition(`dry_run`=True) is called without `pending_fields`, so the preview judges the un-stamped file and refuses a transition the identical real command accepts - the exact preview/run divergence the parameter was added to close.

## Steps to Reproduce

Evidence (`cmd_set` lines 951-1002 (annotate at 990, `record_verdict` at 993, transition() at 1000); `pending_fields` contract lines 840-846): `cmd_set` order: `_static_depth_refusal` -> annotate -> `record_verdict` -> transition(); critic.py:77-98 appends a persistent verdict row; reproduced on a fixture bug: 'set BG0001 Fixed --depth functional --dry-run' blocked rc=1 while the same command without --dry-run succeeded rc=0; `pending_fields` is threaded only from artifact.py:1300.

## Proposed Fix

In `cmd_set`, run transition(`dry_run`=True, `pending_fields`={'Verification depth': depth}) as a full pre-flight before annotate/`record_verdict` and abort on refusal, and pass the same `pending_fields` on the user-facing --dry-run path so preview and real run agree.

## Acceptance Criteria

### AC1: a refused close leaves no stamp and no verdict row

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** `pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::OneCallPreflightTests::test_a_refused_close_leaves_no_stamp_and_no_verdict_row`, written red before the fix and green after
- **Verified:** yes (2026-07-27, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
