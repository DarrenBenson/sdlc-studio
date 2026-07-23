# CR-0357: the RFC accept gate's fail-closed fallback can refuse a valid RFC, and says nothing about why

> **Status:** In Progress
> **Decomposed-into:** EP0126
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/reference-rfc.md
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The fail-closed fallback reads every unsettled decision row anywhere in the file, so an RFC with every decision settled can be refused because of an EXAMPLE row inside a fenced block. The trigger is a document ending inside an unterminated fence, which is valid CommonMark - a fence closes at end of document, so an appendix whose last block is never closed is well-formed and every parser accepts it. The operator is then told to close a decision that does not exist, and the remedy is editing a valid document to satisfy the tool. Incidence is 0 of 47 on the current corpus and a Decision-Override escape exists, so this is a cost worth paying rather than a defect - but it is undocumented, and the operator meeting it has no signal that the refusal is a known false positive rather than a real open decision.

## Impact

An operator meets a refusal naming a decision that is settled, with no indication it is the fallback's deliberate over-report. The likely responses are editing valid markdown or distrusting the gate, and the second is worse.

## Acceptance Criteria

- [ ] the refusal states when it came from the fallback, so the operator can tell a deliberate over-report from a real open decision
- [ ] the fallback's trade (a rare false positive for no false negative) is documented where the gate is described, not only in the source
- [ ] the Decision-Override escape is named in the refusal text

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
