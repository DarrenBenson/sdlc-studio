# CR-0362: a retro finding fixed during the sprint has no honest disposition: the vocabulary is filed or declined

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/templates/core/retro.md
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

retro.py accepts two dispositions for a finding: filed (an artefact id) or declined (with a reason). A closing review that finds eleven defects which are then FIXED in the same sprint fits neither. Filing a ticket for work already done mints a unit that is born complete and pollutes the backlog; declining it is false, because it was not declined, it was repaired. The retro for RUN-01KXWWM3 had eleven such findings and every one had to be written as 'declined: fixed in <sha>', which reads as a refusal in the permanent record of a sprint that did the work. The disposition rule is otherwise good - it is the check that stops a finding being written down and left to rot - and this is the one shape it cannot express.

## Impact

The retro is the durable account of what a sprint learned and did. Recording repairs as declines misdescribes the sprint to anyone reading it later, and pushes an author toward the alternative of filing throwaway tickets to satisfy a gate. Both are worse than the truth.

## Acceptance Criteria

- [ ] a third disposition records a finding fixed within the sprint, with the commit or unit that fixed it
- [ ] the gate accepts it as dispositioned, distinctly from filed and from declined
- [ ] the counts the close reports name the three states separately, so a sprint that repaired eleven findings does not read as having declined eleven

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
