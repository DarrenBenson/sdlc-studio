# CR-0394: A message describing what a guard will do must be DERIVED from the guard, never restated beside it

> **Status:** In Progress
> **Decomposed-into:** EP0107
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/best-practices/script.md,.claude/skills/sdlc-studio/reference-scripts.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The `window open` sentence was wrong five times in a row in one sprint, each time repaired by an author who believed they had understood the previous failure. v1 described a tree-wide freeze after the guard became path-scoped. v2 printed the raw paths field, so the default invocation said zero paths while claiming everything. v3 rendered the normalised record but not the matcher's verdict, so a bare dot read as one narrow path. v4 enumerated the matcher's literal spellings and missed the fnmatch glob family, getting the single star right only by accident. v5 finally PROBES the matcher's own question instead of describing it. The class is general and has nothing to do with windows: every one of the five was an independent RESTATEMENT of a rule that lives in code elsewhere, and a restatement can only ever be correct until the rule moves. The same shape appears elsewhere in this repo - a documented config key no code read (BG0250), an engagement-floor caveat printed on the refusal but not the pass, and a docstring naming an opt-out that did nothing.

## Impact

Any script printing a sentence about what a gate, guard or check will do. The failure is silent and fails in the DANGEROUS direction about half the time: an operator told a guard is narrow when it is total concludes the guard is inert, and routes around it.

## Acceptance Criteria

- [ ] The best-practice guide states the rule: a user-facing sentence about a guard's behaviour is computed from the guard's own predicate, not written alongside it.
- [ ] Where a message and a verdict must agree, one test drives BOTH over the same input and asserts they agree, rather than asserting the message's text separately.
- [ ] The rule names its own counter-example: an enumeration of spellings is a restatement wearing a function's clothes, and probing the real predicate is what makes it a derivation.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
