# RFC-0030: PVD-wide dependency graph: a declared provides/consumes contract, not inferred imports

> **Status:** Draft
> **Date:** 2026-07-13
> **Created-by:** sdlc-studio file

## Summary

Split out of CR0224 on 2026-07-13. The multi-repo edge list needs a design rung before it can be built, because the obvious implementation is dishonest. `repo_map` infers edges by matching an import against a file basename; its own reference doc concedes this cross-links unrelated packages WITHIN one repo. Across repos the ambiguity is strictly worse: two services with a utils.py would be joined by a fabricated edge. Shipping a merged edge list on that basis would produce a confidently wrong artefact, which is worse than no artefact - sdlc-studio's whole claim is that its paperwork can be trusted. The question this RFC must settle: where does a cross-repo dependency edge come from, if not from inference? The PVD manifest already exists and `blocker_sweep` already resolves artefact ids across it, so the plumbing is there; what is missing is a truthful source for the edges themselves.

## Design Options

- **Declared contract: each repo's PVD manifest entry declares provides (named interfaces/APIs it exposes) and consumes (what it depends on). Edges are read, never guessed. Deterministic and honest, and a declaration that goes stale is detectable by reconcile. Costs a manifest schema change plus the discipline of maintaining the declaration.**
- **Inferred with confidence tiers: keep import inference but rank edges (exact package-name match = high, basename collision = low) and refuse to emit the low tier. Cheaper, no schema change, but it still guesses, and the tiering is a heuristic defending a heuristic.**
- **Do not build it: cross-repo dependency at the artefact level (CR0224's Depends on: resolution) may be all that is actually needed, and the code-level edge list may be a solution looking for a problem. Cheapest, and the honest default if no consuming project can name a use for it.**

## Recommendation

Option 1 (declared provides/consumes), but do not build it until a real multi-repo consuming project asks for it. CR0224's artefact-level dependency resolution ships in v4.1 and may well satisfy the actual need; if it does, option 3 wins by default. Decide after v4.1 is in the field.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Act on this finding or keep status quo | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | audit | Filed |
