# RFC-0004: repo_map ranks by import in-degree plus token overlap only; decide between an Aider-style PageRank symbol graph or explicitly scoping it down

> **Status:** Draft
> **Priority:** Medium
> **Author:** Adversarial Audit
> **Date:** 2026-06-20
> **Spans:** sdlc-studio skill
> **Related:** RV0002 (audit run)
> **Supersedes / Superseded by:** --

## Summary

repo_map.py builds no definition/reference graph - it extracts definitions only and ranks by import in-degree (basename-heuristic, self-described 'intentionally crude') plus token overlap, materially weaker than Aider's tree-sitter def+ref multigraph with weighted edges and personalised PageRank fitted to a token budget.

## Context & Problem

repo_map.py compute_in_degree (repo_map.py:289-321) resolves imports by basename-substring match (docstring 293-295 calls it 'intentionally crude', 'not build a call graph'), counts only import edges, and score_file (369-397) adds in_degree*0.5 as a flat hub bonus after a token match - no reference edges, no edge weighting, no personalisation, no per-symbol rank, no token-budget fitting. Only Python uses a real parser (ast); the other 13 supported extensions are shallow regex (SUPPORTED_EXTENSIONS:35-51). Aider's benchmark builds an identifier-keyed directed multigraph over both definitions and references across 130+ languages, weights edges (10x mentioned, 10x well-named, 50x chat files), runs personalised PageRank, distributes rank back to definition tags, and fits to --map-tokens. This is not 'pure-stdlib vs richer parser' - it is a fundamentally less informative ranking that Aider's own benchmarks show underperforms on edit accuracy.

## Design Options

### Option A - act on the finding

Decide between (a) adopting the Aider/RepoMapper approach - extract references (new pass), build a weighted def->ref identifier graph, run a stdlib power-iteration personalised PageRank seeded from story tokens, fit to a --map-tokens budget; or (b) explicitly scoping repo_map down and documenting it as a lexical relevance ranker, deferring graph ranking to Aider/RepoMapper as a soft dependency. RFC because (a) adds a reference-extraction pass the parsers don't currently do and (b) reduces an advertised capability.

### Option B - status quo

Keep the current behaviour and accept the trade-off described above.

## Recommendation

TBD - pending the Open Decision below.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Act on this finding or keep status quo | Option A / Option B | Operator | spike or operator call | Open |

## Evidence

repo_map.py:293-295 (docstring: import in-degree, 'intentionally crude', 'not build a call graph') and :395 (score = token matches + in_degree*0.5); benchmark <https://aider.chat/2023/10/22/repomap.html>

## Impact

repo map build feeds the Agent Prompt Template's ranked file list - the implementing agent's primary context selector. Import-popularity ranking surfaces config/util hubs over the functions a story actually needs, the exact failure Aider's PageRank exists to prevent. Quality risk medium.

## Decision

**Outcome:** TBD
**Rationale:** TBD

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: external-benchmark) |
