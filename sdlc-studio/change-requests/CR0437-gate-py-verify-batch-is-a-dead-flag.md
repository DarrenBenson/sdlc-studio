# CR-0437: gate.py --verify-batch is a dead flag: run_gate accepts verify_batch and never reads it

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

`run_gate` declares `verify_batch` and `cmd_gate` passes it in, but no line of `run_gate`'s body reads it: the only verify-lane construction hardcodes batch=True under --release, and without --release the verify lane does not exist, so --verify-batch changes nothing on any invocation while its help text and inline comment claim otherwise.

## Impact

`run_gate` declares `verify_batch` and `cmd_gate` passes it in, but no line of `run_gate`'s body reads it: the only verify-lane construction hardcodes batch=True under --release, and without --release the verify lane does not exist, so --verify-batch changes nothing on any invocation while its help text and inline comment claim otherwise.

## Acceptance Criteria

- [ ] Either wire it through (pass batch=`verify_batch` when constructing the verify lane, letting an operator force per-AC authoritative runs under --release) or delete the flag, its help text, and the dead parameter.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Raised |
