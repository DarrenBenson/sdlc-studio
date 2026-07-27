# CR-0448: command_audit reports a flag whose destination is never read - and is proven on verify_batch

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (scope residue from the D0069 cap); agent; skill v5.0.0

## Summary

US0479 deletes gate's dead --verify-batch flag. The general detector was cut because a round-two reviewer showed the proposed specification provably would NOT have caught `verify_batch`: treating getattr(args, name, default) as a legitimate read exempts exactly the pattern that made the flag dead.

## Impact

Who: every operator trusting a documented flag to do something. What breaks: another dead flag ships wearing live documentation, and the detector built to prevent it passes.

## Acceptance Criteria

- [ ] The detector flags a flag whose argparse destination no line of the module reads.
- [ ] It is validated against `verify_batch` as it stood before US0479 deleted it - the defence is proven on the bug it defends against, not only on a fixture.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (scope residue from the D0069 cap) | Raised |
