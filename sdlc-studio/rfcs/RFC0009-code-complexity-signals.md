# RFC-0009: Code-complexity signals for estimation, token budgeting, refactor-first and test risk

> **Status:** Accepted
> **Priority:** High
> **Author:** Darren Benson
> **Date:** 2026-06-20
> **Spans:** sdlc-studio skill (repo_map / a complexity helper, code plan, project plan, TSD/test-spec, autonomous-loop budget)
> **Related:** RFC0001 (loop budget), RFC0004 (repo_map ranking), RFC0006 (execution model), reference-repo-map.md, reference-code.md, reference-test-best-practices.md
> **Supersedes / Superseded by:** --

## Summary

Compute code-complexity metrics (cognitive + cyclomatic, per function and per change
blast-radius) from the AST `repo_map` already builds, and surface them as a planning
signal that feeds four jobs: code analysis, effort estimation (greenfield vs
brownfield), token budgeting with a refactor-first recommendation, and test-risk
prioritisation. The metric is advisory, not a gate.

## Context & Problem

SDLC Studio estimates effort and sizes agentic waves largely from story shape, not from
the difficulty of the code a story must touch. That leaves three costs on the table:

1. **Estimation is blind to brownfield difficulty.** A story adding a new file and a
   story modifying a 40-branch function look the same to the planner, but cost very
   differently in tokens, iterations and error rate.
2. **Token budget is uniform.** RFC0001's loop has no per-story budget signal, yet
   agentic tasks run 1-3.5M tokens with up to 10x variance - and complexity is a known
   predictor of which tasks land in the expensive tail.
3. **Test depth is uniform.** Coverage targets and verification tiers are set by policy,
   not by where the defect risk actually is (complexity correlates with defect density).

The research is settled enough to act on: complexity metrics correlate positively with
LLM code-generation failure rate (LiveCodeBench; logistic-regression studies on
Pass@1), an LLM-tuned complexity metric (LM-CC) outperforms classic cyclomatic
complexity, the "planner computes complexity first" pattern exists (RefAgent), and
LLMs measurably perform better on complexity-reduced code (refactor-first). What does
not exist anywhere is the integration of all of this into one SDLC pipeline. SDLC Studio
already owns every hook.

## Goals / Non-Goals

**Goals**

- A deterministic complexity signal per function and per change blast-radius.
- `code plan` estimates that reflect the difficulty of the touched code.
- A **refactor-first recommendation** when blast-radius complexity exceeds a
  configurable threshold.
- A complexity-weighted token budget for the autonomous loop (RFC0001).
- Complexity-driven test risk: coverage targets, edge-case scenario counts and
  verification-depth tiers scaled by where the risk is.

**Non-Goals**

- A hard gate that blocks work on complex code (recommendation only).
- Speculative or wholesale refactoring (scope is the change's blast radius, not the file).
- A new third-party dependency in the core path (stdlib first; richer tools are soft deps).
- Replacing `repo_map` ranking (RFC0004) - this enriches it.

---

## Tooling (how cognitive complexity is computed, and what exists)

Cognitive complexity (SonarSource, Campbell 2018) scores understandability by three
rules: no increment for readable shorthand (a `switch` is +1, not +1 per case); +1 for
each break in linear flow (`if`/`else`, ternary, loops, `catch`, a sequence of `&&`/`||`,
label jumps); and an extra **+1 per nesting level** for flow-breakers nested inside
others - the part cyclomatic complexity ignores. SonarSource flags a function above
**15** as high. It predicts agent difficulty better than raw cyclomatic, which is why
this RFC leans on it.

Open-source landscape (verified 2026-06-20):

| Tool | Metric | Languages | Deps | Licence |
| --- | --- | --- | --- | --- |
| complexipy | cognitive | Python | pip (Rust wheel) | MIT |
| cognitive_complexity | cognitive | Python | pip, pure-Python AST | MIT |
| lizard | cyclomatic | 15+ (C/C++, Java, JS, Py) | pip, pure-Python | MIT |
| radon | cyclomatic, Halstead, MI | Python | pip, pure-Python | MIT |
| SonarQube | cognitive | ~30 | server, heavyweight | LGPL/commercial |

**Key finding:** there is no clean, embeddable, multi-language cognitive-complexity
library - SonarSource is the only broad implementation and it is a server, not a lib.
The cognitive algorithm is small and fully specified, so the pragmatic split is: write
our own Python cognitive scorer (~120-150 lines of stdlib `ast`, zero deps) for the
language we most need, and soft-depend on `lizard` for multi-language cyclomatic
breadth. That is Option A + B below.

---

## Design Options

### Option A - Complexity in `repo_map.py` (stdlib-first)

**Approach:** extend the existing AST walk to compute cyclomatic and cognitive
complexity per function for Python (the skill's own language), emit per-file and
per-function scores in the repo-map JSON. Other languages get a regex-heuristic or are
marked unscored. `code plan` reads the JSON.
**Pros:** no new dependency; reuses the AST already built; fits the pure-stdlib principle.
**Cons:** Python-rich, weaker for other languages without a soft dep.
**Effort / risk:** Low / low.

### Option B - A complexity helper with a soft dependency

**Approach:** a `scripts/complexity.py` that uses our own stdlib AST scorer for Python
and shells out to `lizard` (pure-Python, multi-language cyclomatic, MIT) or
`radon`/`complexipy` when present, degrading to the stdlib path otherwise - the same
soft-dep pattern as `gh` and the test runners.
**Pros:** real multi-language coverage; battle-tested metric implementations.
**Cons:** an optional dependency to document and detect.
**Effort / risk:** Medium / low.

### Option C - A composite implementation-difficulty score

**Approach:** blend cognitive complexity with git churn, coupling/fan-in (from
`repo_map`) and test coverage into one difficulty score that drives estimation, token
budget, wave sizing and test risk.
**Pros:** the most predictive signal; serves all four jobs from one number.
**Cons:** most to build and, critically, to calibrate; risks Goodhart gaming.
**Effort / risk:** High / medium.

---

## Recommendation

**Option A now** (stdlib cognitive + cyclomatic complexity for Python, surfaced in the
repo-map), **plus Option B's soft dependency** for multi-language projects, evolving
toward **Option C's composite score** once there is real calibration data. Lean
**cognitive complexity** over raw cyclomatic (it predicts agent difficulty and human
maintainability better; SonarQube's >15 "high" threshold is a sane default). Keep every
output advisory.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Which metric(s) | cyclomatic only / + cognitive **[leaning]** (own stdlib scorer or complexipy) / + Halstead / track LM-CC | Design | start cognitive + cyclomatic; revisit with data | Resolved |
| D2 | Core dependency | own stdlib cognitive scorer **[leaning]** / soft-dep lizard for multi-language / required dep | Operator | stdlib-first + lizard soft dep; no embeddable multi-language cognitive lib exists | Resolved |
| D3 | Refactor-first behaviour | recommend **[leaning]** / block above threshold / silent score only | Operator | recommend, configurable threshold | Resolved |
| D4 | Unit of measure | function / file / change blast-radius (function + repo_map neighbourhood) **[leaning]** | Design | blast-radius best predicts agent cost | Resolved |
| D5 | What consumes it | estimation / token budget (RFC0001) / wave sizing / test risk - which first | Operator | phase: estimation + refactor reco first | Resolved |
| D6 | Refactor-scope guard | how to stop speculative over-refactoring (Beck "make the change easy", scoped) | Design | scope the refactor CR to the change only | Resolved |

---

## Architecture Impact

| Layer / System | Impact | Change Type |
| --- | --- | --- |
| `repo_map.py` / `scripts/complexity.py` | Compute + emit complexity per function/file | New / Enhancement |
| `code plan` (reference-code.md) | Complexity-weighted estimate + refactor-first recommendation | Enhancement |
| `project plan` (reference-project.md) | Complexity-weighted wave sizing | Enhancement |
| Autonomous loop (RFC0001) | Per-story token budget scaled by blast-radius complexity | Enhancement |
| TSD / test-spec | Coverage targets, scenario counts, verification tier by complexity | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Metric gaming / Goodhart (optimise CC, not quality) | Medium | Medium | advisory only; cognitive over raw CC; pair with the audit/verify oracle |
| Over-refactoring on a complexity flag | Medium | Medium | recommend not block; scope the refactor CR to the change (D6) |
| Cyclomatic blindness to nesting/readability | Medium | Low | prefer cognitive complexity (D1) |
| Weak multi-language coverage without a dep | Medium | Low | soft-dep lizard/radon (D2); mark unscored honestly |
| Thresholds wrong without calibration | High | Medium | configurable; start from SonarQube >15; tune from real runs |

---

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | Complexity computation in repo_map / complexity.py (stdlib + soft dep) | CR (TBD) | D1, D2, D4 |
| WS2 | `code plan` estimation + refactor-first recommendation | CR (TBD) | WS1, D3, D6 |
| WS3 | Complexity-weighted token budget for the autonomous loop | CR (TBD) | WS1, RFC0001 |
| WS4 | Complexity-driven test risk (coverage / scenarios / verify tier) | CR (TBD) | WS1 |
| WS5 | `project plan` complexity-weighted wave sizing | CR (TBD) | WS1 |

---

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** Accepted (scoped)

**Rationale:** Adopt cognitive + cyclomatic complexity from the AST repo_map (D1); stdlib-first cognitive scorer + lizard soft dep (D2); recommend-not-block, configurable threshold (D3); change blast-radius unit (D4); estimation + refactor-first first (D5); refactor CR scoped to the change (D6).

**Spawned CRs:** WS1 (complexity in repo_map) + WS2 (code plan estimation + refactor-first reco) - created when picked up. WS3 (loop token-budget, unlocks --order wsjf) deferred until RFC0001 consumes it; WS4/WS5 and the composite score deferred until calibration data exists.

---

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| RFC | RFC-0001 | Autonomous Delivery Loop | Draft | consumes (token budget) |
| RFC | RFC-0004 | repo_map ranking | Draft | enriches the same index |
| RFC | RFC-0006 | Autonomous execution model | Draft | sibling (effort/isolation) |
| Reference | -- | reference-repo-map.md / reference-code.md / reference-test-best-practices.md | Live | extends |

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (rfc-decide session) | Accepted in the RFC decision session - Accepted (scoped) |
| 2026-06-20 | Darren Benson | RFC drafted - complexity signals for estimation, token budget, refactor-first, test risk |
| 2026-06-20 | Darren Benson | Folded in the cognitive-complexity algorithm + open-source tooling landscape (complexipy/lizard/radon); sharpened D1/D2 to "own stdlib Python scorer + lizard soft dep" |
