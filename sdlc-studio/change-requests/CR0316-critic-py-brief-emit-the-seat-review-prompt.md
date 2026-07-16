# CR-0316: critic.py brief: emit the seat-review prompt deterministically and parse the returned verdict block - the critic ceremony is re-derived by hand every unit

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-agent-prompt-template.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; sprint-run retro RUN-01KXGPBN

## Summary

The independent-critic ceremony has a fixed deterministic skeleton: resolve the reviewing seat's charter (`persona_resolve)`, name the unit and its ACs, list the diff scope (the unit's Affects + git status), state the judge dimensions and the exact VERDICT/ISSUES/BLOCKING return contract. Ship it: critic.py brief --unit USxxxx --seat qa|engineering [--tier full|light] prints the assembled review brief (agent pipes it to a subagent verbatim), and critic.py record --from-verdict FILE|- parses the returned block (VERDICT/ISSUES/BLOCKING) into the existing record call, refusing a malformed block loudly. The judgement stays with the seat; only the scaffolding becomes deterministic - the same move artifact.py made for artefact bodies.

## Impact

Each of this sprint's six critic runs was a bespoke hand-written prompt (charter path, unit, diff scope, judge instructions, return-format contract) plus a hand-transcribed verdict into critic.py record - ~6 re-derivations of the same structure in one sprint, and any drift in the return contract breaks the recording step silently.

## Acceptance Criteria

- [ ] critic.py brief assembles seat charter reference, unit ACs, Affects-derived diff scope and the return contract into one printable prompt; unknown unit or seat refused loudly
- [ ] critic.py record accepts the VERDICT/ISSUES/BLOCKING block (file or stdin) and records it with reviewer/author/tier, refusing a malformed or verdict-less block
- [ ] reference-agent-prompt-template.md documents the brief as the canonical critic invocation; hand-authored prompts remain valid

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
