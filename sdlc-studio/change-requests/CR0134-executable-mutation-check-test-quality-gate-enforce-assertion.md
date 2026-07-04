# CR-0134: executable mutation-check / test-quality gate (enforce assertion integrity, not just document it)

> **Status:** Approved
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/ (new), .claude/skills/sdlc-studio/reference-test-best-practices.md, .claude/skills/sdlc-studio/reference-verify.md, .claude/skills/sdlc-studio/templates/workflows/release-gate.md, .claude/skills/sdlc-studio/help/
> **Depends on:** CR-0131 (the assertion-integrity discipline this CR makes executable), RFC-0022 (settles the fault-injection design; blocks the epic decomposition)
> **Epic-sized:** yes - on acceptance, decompose into an epic (and likely a preceding RFC for the cross-language fault-injection design)

## Summary

This is the skill's biggest blind spot, named plainly. The skill has strong gates for **document
integrity** (did you produce the artefact, is its status propagated, do the indexes reconcile) and
almost none for **test integrity** (does the test actually fail when the feature breaks). CR-0131
added the *discipline* - the mutation check, the assertion-integrity anti-patterns - but it is
**prose that relies on the agent remembering**. Nothing executable enforces it.

The cost is not hypothetical. In the field (a consuming project) a governance surface shipped marked
"renders + initiates + audits" while, on the real data path, it did none of the three - a green,
vacuous suite over dead code. Every existing gate passed. `verify_ac.py` confirms an AC's test
*passes*; it does not ask whether the test would *fail* if the feature were broken, nor whether a
component test injects data past the real wiring. That question is the whole game, and it is
currently unenforced.

Proposed: an executable **mutation-check gate** - the cheap, language-agnostic core of mutation
testing, scoped to the changed surface rather than the whole tree:

1. Given a test (or the set named by a story's ACs), apply a small set of **targeted mutations** to
   the code under test - the fault classes that actually recur: unset/return-undefined for a field
   a loader delivers, invert a boolean guard, stub a component's return to null, no-op a mapper.
2. Re-run the associated test. **A mutation that leaves the test green is a finding** - the test
   does not pin that behaviour. Report per test: killed (good) vs survived (the assertion is not
   load-bearing).
3. Wire it as (a) an on-demand `code verify --mutation` lane over a story's ACs, and (b) a
   release-gate check over the release's changed navigable surfaces. Deterministic and bounded:
   a fixed, declared mutation set over a named file set, not an unbounded fuzz.

Design is genuinely unsettled (how to inject faults portably across TS/Python/Go without a
per-language mutation framework; how to bound cost; how to map an AC to its test set reliably), so
this should open with an **RFC** before the epic - hence epic-sized, filed as a CR to capture the
problem and the field evidence first.

## Acceptance Criteria

> High-level, for the epic to refine. The RFC settles the fault-injection mechanism first.

- [ ] a declared, bounded mutation set (unset-delivered-field, invert-guard, stub-return-null,
      no-op-mapper, at minimum) is applied to a named file set and the associated tests re-run
- [ ] the gate reports per test **killed vs survived**; a surviving mutation (test still green) is a
      finding surfaced to the operator/loop, not a silent pass
- [ ] available as an on-demand `code verify` lane over a story's AC test set, and as a
      release-gate check over the release's changed navigable surfaces
- [ ] deterministic and bounded (standing directive): same code + same mutation set -> same report;
      no unbounded fuzzing; cost is proportional to the changed surface, not the whole tree
- [ ] degrades honestly: a language/framework the injector cannot mutate is **reported as
      un-checked**, never reported as passed ([[LL0008]])
- [ ] the discipline prose (CR-0131) links to the executable gate as its enforcement
- [ ] `CHANGELOG.md` `[Unreleased]` + `help/` + `reference-verify.md` updated

## Out of Scope

- Full-tree mutation testing / a coverage-style mutation score (this is a targeted, changed-surface
  gate, not a whole-repo mutation-testing product).
- Replacing `verify_ac.py` (this complements it: verify_ac checks pass, this checks can-fail).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Created via `new` (deterministic); flagged epic-sized, RFC-first |
| 2026-07-04 | claude | RFC-0022 authored (sprint 2026-07): 4 design options, recommendation B-core + C-lane + D-prefilter, open decisions D1-D6. CR Blocked pending the RFC decision; decompose to an epic on acceptance |
