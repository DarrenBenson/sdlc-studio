# CR-0515: An agent customises content, never tooling: hand-rolled work is detected from the run diff, reported at the close, and escapes only by filing the gap

> **Status:** In Progress
> **Decomposed-into:** EP0196
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-scripts.md
> **Priority:** High
> **Type:** Feature
> **Size:** L

## Summary

An agent customises CONTENT, never TOOLING. It authors the prose of a retro, the text of a finding, the wording of a criterion, the rationale on a waiver. It never authors a mutation harness, a census script, a review prompt, an index row, an id, a status transition or a criteria tick - those have tools, and where one is missing that is a gap to file rather than a script to write.

The rule is stated in AGENTS.md and is not enforced, so it is not followed. RUN-01KYX375 is the measurement, by the agent that had read the file: FOUR review prompts hand-written while `critic.py brief` ships the bounded scope, the criteria-as-law framing and the claim-inventory pass; seats chosen by judgement while `persona_resolve.py panel` assigns them; roughly EIGHT bespoke mutation harnesses written while `mutation.py run` does exactly that - and the hand-rolled one hit the precise hazard `mutation.py window` exists to prevent, timing out with a mutant still applied to `sprint.py`; no review span opened while `review-batch --open` ships, which cost a waived checklist item; and the cross-project lessons never read though AGENTS.md names the file.

Every one was invisible. Nothing in the close reports that a run hand-rolled its way around six shipped tools, so the sprint record reads identically to one that used them.

## Impact

This project's stated purpose is to be the antidote to vibe coding. A run that hand-rolls around its own tooling and closes green is the product failing at the one thing it exists to prevent, and it fails silently - which is worse than not having the tools, because the record asserts a discipline that was not applied.

It is also the root cause of the review problem this backlog is otherwise trying to fix: the sprawling, partly-spurious REJECT rounds came from hand-written prompts, and the same units re-reviewed from the shipped brief produced one precise finding each. Fixing the checklist and the sign-off model without fixing this leaves the input unmechanised.

## Acceptance Criteria

- [ ] A run that hand-edits an artefact a tool could have changed reports that artefact by name at the close, derived from the run diff against the tool-use ledger rather than asked
- [ ] A hand-rolled action carrying a filed gap id is reported and does NOT block; one with no gap id is OUTSTANDING - the escape is a backlog entry, never a waiver
- [ ] The close reports a count of manual actions, and a run using the tools throughout reports zero - the positive control, so the item cannot be satisfied by a detector that never fires
- [ ] Replayed against RUN-01KYX375, the item names the six tools that run bypassed
- [ ] `reference-doctrine.md` states the content-versus-tooling rule, and `reference-scripts.md` is named as the pre-task catalogue, so a consuming project inherits both

## Proposed Fix

1. TOOL-USE LEDGER. Every skill script records, per run, the artefact it touched and the action it performed. `artifact.py` already stamps `Created-by`, so the shape exists; this generalises it to modification.
2. HAND-EDIT DETECTION, DERIVED NOT ASKED. At close, the artefacts changed in the run's diff are compared against the ledger. An artefact changed with no tool provenance for that change was hand-edited, and is reported by name. This is machine-checkable and needs no question put to an agent, which is the point - an agent that hand-rolls is exactly the one that will answer 'yes I used the tools'.
3. A CHECKLIST ITEM. `tooling-used` joins the compulsory set: the count of hand-edited artefacts and hand-rolled actions this run, each named. Non-zero is OUTSTANDING unless each carries a filed gap id.
4. GAP FILING IS THE ESCAPE, AND IT IS TRACKED. Where no tool exists, the agent files a CR and cites its id against the manual action. 'Manual actions: 2, both with filed gaps' is a clean close; 'Manual actions: 6, none filed' is not. The escape produces a backlog item rather than a waiver, so the tooling improves instead of the rule eroding.
5. THE RULE, STATED WHERE IT BINDS. `reference-doctrine.md` states the content-versus-tooling line so a consuming project inherits it, and `reference-scripts.md` is named as the catalogue to consult BEFORE any mechanical task.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
