# EP0215: A Verify selector that resolves to nothing is refused where it is WRITTEN, and the existing corpus is swept

> **Status:** Done
> **Derived Point Total:** 11
> **Parent:** CR0508
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0508. Delivers the work CR0508 requested.

## Story Breakdown

- [x] [US0667: Every writer refuses a Verify selector that resolves to nothing, naming the near miss, and reuses selector_resolves rather than reimplementing it](../stories/US0667-every-writer-refuses-a-verify-selector-that-resolves.md)
- [x] [US0668: A selector that cannot be JUDGED is accepted and reported unjudged, never refused, so a missing runner never makes the writer unusable](../stories/US0668-a-selector-that-cannot-be-judged-is-accepted.md)
- [x] [US0669: validate sweeps the existing corpus for unresolvable selectors, giving unresolvable_stamps its first caller](../stories/US0669-validate-sweeps-the-existing-corpus-for-unresolvable-selectors.md)

## Acceptance Criteria (Epic Level)

- [ ] A writer that accepts a `Verify:` line REFUSES a selector that resolves to nothing, naming the selector and, where it can, the near miss - a class of that name in another module, or a method of that name in another class, since the overwhelmingly common case is a real test named slightly wrong rather than a fabricated one.
- [ ] The check reuses `verify_ac.selector_resolves` rather than reimplementing it. A second implementation of this question is the divergent-reader defect this repo has now filed three times in one batch, and it would be especially pointless here, where the first implementation is complete and tested.
- [ ] A selector that cannot be JUDGED - an unknown runner, a shell verifier, a tool not installed - is accepted and reported as unjudged, never refused. Refusing what cannot be judged would make the writer unusable on any machine missing one runner, which is a worse failure than the one being fixed.
- [ ] `validate` reports an unresolvable selector on an artefact that already carries one, so the existing corpus is swept rather than only new writes being guarded. `unresolvable_stamps` already does this work and has no caller.
- [ ] The refusal is proven by a test that writes an artefact whose Verify line names a plausible-but-absent class, in the exact shape that recurred twice on 2026-07-30 - a real test file, a real method name, the wrong class.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
