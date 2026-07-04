# CR-0131: assertion-integrity discipline: mutation-check gate + templates + reference

> **Status:** Complete
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/reference-test-best-practices.md, .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/templates/workflows/release-gate.md
> **Depends on:** -

## Summary

The skill teaches verification *depth* (`reference-test-best-practices.md#verification-depth-tiers`
- how far a claim was exercised) but never the prior question the tiers silently assume: **would
this test go red if the feature were broken?** A green suite over a dead feature is worse than no
suite - it manufactures false confidence and lets a non-functional surface ship as Done.

This gap was found in the field (agent-crew, EP-0291): a governance surface shipped marked
"renders + initiates + audits" while, on the real data path, it did none of the three. Two
permanently-green test shapes hid it, neither of which any existing anti-pattern names:

1. **Vacuous / tautological assertions** - an e2e that asserts two locators both derived from the
   same boolean (they can never disagree), and an `if/else` whose only reachable branch is a trivial
   `expect(0).toBe(0)` because the content was counted before it rendered. The spec passes even if
   the feature is deleted.
2. **Injected-data unit tests that bypass the real wiring** - `render(<Panel agent={{field}}/>)`
   passes forever while the production loader drops `field` and the panel receives `undefined`. The
   test proves rendering, not delivery; the delivery bug (the field the enrichment forgot to copy)
   ships green.

The fix is a small, high-leverage discipline addition, echoed across the reference, the two artefact
templates that carry verification fields, and the release gate:

- **`reference-test-best-practices.md`** gains a top-level `#assertion-integrity` section (the two
  failure modes with bad/good code, plus **the mutation check** - break the feature on purpose,
  confirm the test goes red, restore), a Contents entry, and a pointer from the anti-patterns list
  (over-mocking is the same disease at the unit boundary).
- **`templates/core/story.md`** gains a per-AC `- **Mutation-checked:**` field + a note: for any
  behaviour-bearing AC (`functional`+), the AC's test must have been seen to fail against the broken
  feature.
- **`templates/core/bug.md`** gains a `Mutation-checked` verification checklist item + note: the
  regression test must have been seen red against the *unfixed* code, proving it pins the fix.
- **`templates/workflows/release-gate.md`** §1 gains a gate: this release's navigable-surface e2e
  specs are mutation-checked, and any loader-fed surface has a spec driving the real data path.

## Acceptance Criteria

- [x] `reference-test-best-practices.md` carries an `#assertion-integrity` section covering the
      vacuous/tautological assertion, the injected-data-bypass unit test, and the mutation check,
      with the Contents entry and the anti-patterns cross-link
- [x] `templates/core/story.md` AC blocks carry a `Mutation-checked` field and the explanatory note
      tying it to `functional`+ behaviour-bearing ACs
- [x] `templates/core/bug.md` Verification section carries a `Mutation-checked` item requiring the
      regression test to have been seen red against the unfixed code
- [x] `templates/workflows/release-gate.md` §1 carries the e2e-mutation-checked + real-data-path gate
- [x] all four surfaces cross-reference each other and use the same vocabulary
      (assertion integrity / mutation check), British English, no em dashes
- [x] `CHANGELOG.md` `[Unreleased]` entry ([[LL0004]])

## Out of Scope

- Automating the mutation check (a script that injects faults and re-runs). Valuable, but a larger
  piece - the discipline lands first as a recorded field + gate; automation can follow as its own CR.
- Retrofitting the field onto already-Done stories/bugs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Created via `new` (deterministic) |
| 2026-07-04 | claude | Filled in + implemented across the four surfaces; Complete |
