# CR-0381: artifact.py new accepts a pipe-separated --ac and emits a malformed AC without warning

> **Status:** In Progress
> **Decomposed-into:** EP0139
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py
> **Date:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The scaffold pairs --ac with --verify positionally. Passing the verifier inside the --ac string instead, as 'criterion|pytest path::Node' - a natural guess, and the shape several other tools in this repo use - is accepted silently. The whole string is then treated as prose, so the identifier-backticking pass rewrites the command (`test_gate.py` becomes a code span) and the literal pipe is left embedded in the criterion text. The result is an AC that reads plausibly, carries no Verify line the runner can see, and needs hand-rewriting into Given/When/Then form. Confirmed NOT a defect in --verify itself: a correctly-paired --verify is emitted clean and unbackticked. The cost is real - all four stories in EP0093 needed their AC blocks rewritten by hand at plan time - and the fix is a warning, not new behaviour.

## Impact

Anyone scaffolding a story with executable ACs. A silently malformed AC is worse than a rejected one: it looks groomed, so the missing Verify line is only noticed when conformance later reports the story as carrying no executable check - or not at all.

## Acceptance Criteria

- [ ] An --ac value containing an unescaped pipe, passed without a paired --verify, is refused or warned about by name, rather than written out as prose
- [ ] A correctly paired --ac/--verify remains byte-identical to today's output, so the guard adds a warning and changes no working path

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Raised |
