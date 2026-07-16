# BG0155: A corrupt .close-owed-baseline.json silently disarms the entire 'un-skippable' close-down and every surface then invites re-stamping a baseline that forgives the owed debt

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/hooks/close_guard.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/status.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

`load_baseline` (`close_owed.py`:75-84) returns None for a truncated/malformed baseline and for a parsed dict whose 'grandfathered' is not a list - indistinguishable from 'never baselined'. Every enforcement half then stands down: `cmd_detect` exits 0, the Stop hook's decide() returns None, and gate --require-close reports count 0 with 'no baseline stamped yet' (despite the lane's fail-loud framing). Worse, the unbaselined-path messages (render(), status advisory) tell the operator to run `close_owed baseline`, which snapshots every currently-terminal id into a fresh grandfather set - permanently forgiving exactly the units that genuinely owed a close. One merge-conflict-marker in the committed ~283-id JSON converts RFC0042's un-skippable ceremony into a silent pass plus an amnesty instruction (LL0008/LL0010/LL0013). A JSON-array baseline additionally crashes owed() with an uncaught AttributeError that the hook and status advisory swallow to 'allow'. No test covers a present-but-unreadable baseline; US0163's ACs enumerate covered/grandfathered/unbaselined only. Verified 3x.

## Steps to Reproduce

Truncate or corrupt .close-owed-baseline.json (e.g. leave merge-conflict markers, or replace with a JSON array). Run `close_owed detect` -> exit 0; trigger the Stop hook -> allows; run `gate --require-close` -> passes with 'no baseline stamped yet'; every surface prints 'Run `close_owed` baseline', which stamps the owed units into the forgiven set. With a JSON array, owed() raises AttributeError, swallowed to allow by the hook and status advisory.

## Proposed Fix

Make `load_baseline` distinguish corrupt from absent: a present-but-unparseable/mis-shaped baseline is a loud blocking error state in detect, the hook, and the gate lane (never 'allow'), with a message directing repair - never `baseline` re-stamping. Validate the parsed shape. Add tests for truncated, JSON-array and wrong-shape baselines.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
