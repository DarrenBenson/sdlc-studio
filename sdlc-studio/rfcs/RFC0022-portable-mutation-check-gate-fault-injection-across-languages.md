# RFC-0022: Portable mutation-check gate: fault injection across languages without a per-language framework

> **Status:** Draft
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

CR-0134 makes the assertion-integrity discipline executable: apply a bounded, declared mutation set to the changed surface, re-run the AC-mapped tests, and report killed vs survived - a surviving mutation is a finding. The unsettled design is the injection mechanism: how to mutate TS/Python/Go (and unknown ecosystems) deterministically and cheaply, how to map an AC to its test set reliably, and how to degrade honestly when a surface cannot be mutated. The gate must satisfy: same code + same mutation set -> same report; cost proportional to the changed surface; an un-mutatable surface reported as un-checked, never passed.

## Design Options

- **A: Per-language AST mutators shipped in the skill (Python ast stdlib; TS/Go need parsers). Highest fidelity, but each language is a parser dependency and a maintenance surface - the exact per-language framework burden the CR wants to avoid; unknown ecosystems get nothing.**
- **B: Declared textual mutations - a per-fault-class spec (unset-delivered-field, invert-guard, stub-return-null, no-op-mapper) expressed as deterministic, anchored source-text transforms with language-profile pattern tables; tests re-run through the existing Verify DSL runners. Language-agnostic core, honest degrade by construction (no anchor match -> un-checked), bounded and deterministic; lower fidelity than AST on unusual code shapes.**
- **C: Adapter lane over existing mutation frameworks (mutmut, Stryker, go-mutesting) - highest power where installed, but heavyweight soft dependencies, per-tool report shapes, and cost/determinism vary by tool; unusable as the portable floor.**
- **D: Static assertion-integrity heuristics only (no execution): flag tests with no load-bearing assertion on the changed surface. Cheapest, but never answers can-it-fail - fails the CR's core question; at most a pre-filter.**

## Recommendation

B as the portable core (the floor every project gets), with C as an opt-in per-ecosystem power lane surfaced through the same killed/survived report, and D's static scan as a cheap pre-filter that orders which tests to mutate first. AC-to-test mapping rides the existing bridge: the story's Verify lines + the test-spec AC Coverage Matrix, so the gate needs no new mapping metadata. A per the fidelity need only if B's field survival rate proves insufficient - measure before building parsers.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Injection mechanism: adopt the recommendation (B core + C opt-in lane + D pre-filter), or another option mix | Open |
| D2 | Mutation-set v1: are the four declared fault classes (unset-delivered-field, invert-guard, stub-return-null, no-op-mapper) the right bounded floor | Open |
| D3 | Anchor form for textual mutations: how a mutation names its target (file + pattern + occurrence index?) so the report is stable across unrelated edits | Open |
| D4 | Surface selection: changed-files-since-ref (git diff) vs the story's Affects field vs both, and which is the release-gate default | Open |
| D5 | Report home: a `.local/mutation-report.json` beside verify-report, and whether `gate` consumes it as PASS/advisory in v1 | Open |
| D6 | Cost ceiling: max mutations per run / per file before the gate truncates - and truncation must be REPORTED as un-checked coverage, never silent | Open |

## Spawned By

- [CR-0134](../change-requests/CR0134-executable-mutation-check-test-quality-gate-enforce-assertion.md) - executable mutation-check / test-quality gate (epic-sized; this RFC settles the design before decomposition)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Filed |
| 2026-07-04 | claude | Open decisions D1-D6 drawn from CR-0134's unsettled-design list; linked the spawning CR |
