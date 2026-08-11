# CR-0508: a Verify selector naming a test that does not exist is accepted at write time, though the predicate that would refuse it already ships

> **Status:** Complete
> **Decomposed-into:** EP0215
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Date:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator), from the RUN-01KYPZ1G close; human; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`verify_ac.selector_resolves` already answers the question - does this selector name a real test - and `unresolvable_stamps` already reports the ones that do not. No writer calls either. `file_finding`, `artifact.py` and every hand-edit accept any string as a `Verify:` line, so an AC can be authored, committed and read as evidence while pointing at nothing. The error surfaces only when somebody later runs `verify_ac`, and only if they do. This is the repo's own recorded scar - four units once shipped with stale Verify lines verifying NOTHING - and it recurred twice in one session on 2026-07-30: the author typed the class name the test OUGHT to have had rather than reading the file, in both cases a single `awk` away, and in both cases the mistake was caught minutes later by `verify_ac` reporting `ac=0` and then `fail=2`.

## Impact

Who: anyone reading a `Verified: yes` stamp as proof, and every consuming project inheriting the same writers. What breaks: the AC is the unit's contract and the Verify line is the only mechanical part of it, so a selector that resolves to nothing turns a checkable claim into prose while keeping the appearance of a check. The failure is silent and time-shifted - the artefact is committed clean and only a later, optional command disagrees. It is worst exactly where it matters most: a unit being driven to Done, where the gate reads the stamp rather than the selector. Writing the reference before establishing the referent is not a knowledge gap - it is an ordering mistake that a machine can catch and a human reliably will not.

## Acceptance Criteria

- [ ] A writer that accepts a `Verify:` line REFUSES a selector that resolves to nothing, naming the selector and, where it can, the near miss - a class of that name in another module, or a method of that name in another class, since the overwhelmingly common case is a real test named slightly wrong rather than a fabricated one.
- [ ] The check reuses `verify_ac.selector_resolves` rather than reimplementing it. A second implementation of this question is the divergent-reader defect this repo has now filed three times in one batch, and it would be especially pointless here, where the first implementation is complete and tested.
- [ ] A selector that cannot be JUDGED - an unknown runner, a shell verifier, a tool not installed - is accepted and reported as unjudged, never refused. Refusing what cannot be judged would make the writer unusable on any machine missing one runner, which is a worse failure than the one being fixed.
- [ ] `validate` reports an unresolvable selector on an artefact that already carries one, so the existing corpus is swept rather than only new writes being guarded. `unresolvable_stamps` already does this work and has no caller.
- [ ] The refusal is proven by a test that writes an artefact whose Verify line names a plausible-but-absent class, in the exact shape that recurred twice on 2026-07-30 - a real test file, a real method name, the wrong class.

## Recommendation

Small and worth doing early: the predicate exists, the writers do not call it, and the whole change is a call site plus its refusal message. Do the near-miss hint in the same slice rather than deferring it - a refusal that says only 'this does not resolve' sends the author back to grep, which is the step they skipped in the first place, whereas 'no class DiscoveredHomesTests in `test_check_versions.py`; did you mean VersionHomeTests' closes the loop where it broke.

Check during refine whether the `Verified:` stamp should carry the fingerprint of the selector it was earned against, so that renaming a test invalidates the stamp rather than silently orphaning it. That is the adjacent half of the same problem and may already be covered by the AC-fingerprint work; if so, say so and keep this slice to the writer.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Darren Benson (operator), from the RUN-01KYPZ1G close | Raised |
