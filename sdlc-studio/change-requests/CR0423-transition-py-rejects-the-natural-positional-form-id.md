# CR-0423: transition.py rejects the natural positional form (ID Status); the first guess errors on argparse noise

> **Status:** Complete
> **Decomposed-into:** EP0165
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The gated status-change tool is invoked as transition.py set --id US0443 --status Review. The obvious first attempt - transition.py US0443 Review or transition.py set US0443 Review - fails with a raw argparse error listing subcommands, not a hint. Dogfood friction hit repeatedly while closing EP0163.

## Impact

Every agent or operator driving transitions by hand hits an unhelpful error on the natural form before discovering the flag syntax; slows every manual transition and reads as the tool being broken.

## Acceptance Criteria

- [ ] The natural positional form transition.py set ID Status is accepted, or the error names the exact correct invocation, not just the subcommand list

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Raised |
