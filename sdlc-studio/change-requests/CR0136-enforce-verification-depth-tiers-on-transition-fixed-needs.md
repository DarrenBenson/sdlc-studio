# CR-0136: enforce verification-depth tiers on transition (Fixed needs functional+, Close needs soak)

> **Status:** Approved
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/reference-test-best-practices.md, .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/reference-bug.md
> **Depends on:** -

## Summary

The verification-depth tiers (`reference-test-best-practices.md#verification-depth-tiers`) are a good
idea stated as rules but not enforced. The templates say plainly: *"A bug cannot be marked Fixed
until depth is at least `functional`. A production-affecting bug cannot be Closed until depth is at
least `soak`."* But `transition.py` does not read the depth field - it gates a story's Done on AC
verification being green, and nothing checks the depth tier on a bug's Fixed / Close transition
(verified: zero references to depth/functional/soak in `transition.py`). So the tier a bug records is
decorative; a `smoke`-only bug can be transitioned to Fixed with no objection.

This is the same class of gap as the assertion-integrity blind spot (CR-0131/CR-0134): the discipline
is documented, the enforcement is absent, so it holds only when the operator remembers. The tiers
are most valuable exactly where they are ignored - closing a bug on a smoke ping (the
`#smoke-fix-anti-pattern` the reference already warns about).

Proposed: `transition.py` reads the artefact's verification-depth and refuses a transition that
under-shoots the tier the target status requires, with an actionable message (per CR-0025).

1. On a **bug -> Fixed** transition, require `Verification depth` >= `functional`; refuse with
   *"depth is `smoke`; Fixed requires `functional`+ - run the round-trip the bug exercised, then set
   the depth"* otherwise.
2. On a **bug -> Closed** transition where the bug is marked production-affecting, require
   `soak`; refuse otherwise.
3. Story AC parity: where an AC carries a `Verification target`, `Done` should not out-run the
   recorded target (advisory first, to avoid destabilising existing projects, then gateable via
   config).
4. Honest degrade: a missing/unparseable depth field on a transition that requires one is refused
   (fail loud, [[LL0008]]), never treated as satisfied.

## Acceptance Criteria

- [ ] `transition.py` refuses `bug -> Fixed` when recorded depth is below `functional`, with an
      actionable message naming the current and required tier
- [ ] `transition.py` refuses `bug -> Closed` on a production-affecting bug when depth is below
      `soak`; a non-production bug is unaffected
- [ ] a missing/unparseable depth field on a depth-gated transition is refused, not passed
- [ ] story-AC verification-target parity is at least advisory (Done not out-running the recorded
      target), gateable via config; default preserves current behaviour for existing projects
- [ ] unit tests: smoke->Fixed refused, functional->Fixed allowed, prod-bug smoke->Closed refused,
      missing-depth refused, non-prod bug Close path unchanged
- [ ] `reference-bug.md` + `templates/core/bug.md` note that the depth field is now enforced, not
      advisory; `CHANGELOG.md` `[Unreleased]` ([[LL0004]])

## Out of Scope

- Auto-measuring depth (the operator/loop records it; this CR enforces the recorded value, it does
  not run the verification).
- Changing the tier definitions themselves.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Created via `new` (deterministic) |
