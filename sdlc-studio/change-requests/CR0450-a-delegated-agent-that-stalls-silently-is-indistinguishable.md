# CR-0450: A delegated agent that stalls silently is indistinguishable from a slow one, and the doctrine has no detection rule

> **Status:** In Progress
> **Decomposed-into:** EP0177
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-agentic-lessons.md, .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/reference-agent-prompt-template.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYHVWK closing review, two observed stalls); agent; skill v5.0.0

## Summary

The skill directs agents to fan work out - audit finders and refute panels, sprint delivery lanes, adversarial reviewers - and says nothing about how a driving agent detects that a delegate has died. Observed twice on 2026-07-27 within one run: two review agents accumulated large transcripts (841KB and 405KB), stopped writing, and returned nothing. No error, no partial output, no failure signal of any kind. Each cost roughly 35 minutes of a driving agent waiting on a completion that was never coming, and the only reason either was caught is that the operator asked what was happening.

This is the same class the audit reference already names at `#audit-refute-quorum` - 'a dead vote is not a refutation' - one layer down. There the rule is that an absent verdict must never be scored as evidence; here the rule missing is that an absent verdict must never be read as a PENDING one. Both are an absence wearing the face of a state.

A strong correlation points at the avoidance as well as the detection: on the same session, more than twenty agents run inside workflows - each finishing through a structured-output call - all completed, while both agents launched with free-form completion stalled. The mechanism is unproven and may be harness-level rather than anything this project controls, so the fix here is detection and preference, not a claim about the cause.

## Impact

Who: any project driving delegated work through this skill, which is the whole agentic execution model - audit panels, sprint lanes, review fan-out. What breaks: an unattended run waits for ever on a delegate that will never answer, and a run under supervision burns the operator's time instead. Worse for the audit path specifically, where a driving agent that cannot distinguish dead from slow will eventually give up and report the survivors it has - which is precisely the truncated-audit-wearing-a-complete-face failure the refute-quorum rule exists to prevent, reintroduced through the orchestration layer rather than the counting one.

## Acceptance Criteria

- [ ] The doctrine names the silent-stall failure mode: a delegated agent can stop without erroring, and an absent result must never be read as a pending one.
- [ ] It gives a concrete detection rule a driving agent can apply - the delegate's transcript size and modification time distinguish thinking from dead, and the presence of a result marker says whether it finished - rather than instructing the driver to wait for a signal that a dead delegate never sends.
- [ ] It states the preference for a structured-output delegation over free-form completion for long or wide tasks, with the evidence recorded and the causal claim explicitly hedged, so a reader can re-judge it if the harness behaviour changes.
- [ ] The audit reference cross-references its own dead-vote quorum rule to this one, so the two halves of the same class - an absent vote and an absent agent - are read together rather than discovered separately.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (RUN-01KYHVWK closing review, two observed stalls) | Raised |
