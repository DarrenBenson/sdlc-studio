# RFC-0025: Evidence and benchmark harness: measure sdlc-studio against plain Claude Code

> **Status:** Accepted
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Raised-by:** Sam Eriksson (QA amigo)
> **Related:** CR0178 (implementation), CR0177 (positioning refresh - the claims this harness must back), reference-audit.md

## Summary

A small measurement harness comparing sdlc-studio against plain Claude Code with a good
CLAUDE.md on a fixed task set (brownfield fixes plus a feature addition), measuring tokens,
wall time, defect escapes, and rework rate. The tool's own doctrine is evidence over intent
and verification over confidence; its marketing claims are currently the one surface that
doctrine does not reach. This RFC commits, before any numbers exist, to publishing results
regardless of outcome, including unflattering ones.

## Context & Problem

sdlc-studio positions itself as the antidote to vibe coding: files over chat, evidence over
intent, verification over confidence. Every one of those claims is testable, and none has
been tested. The README refresh (CR0177) will sharpen the differentiators; without
measurement, those are assertions of the exact kind the tool exists to eliminate. In a
category full of framework hype, even a small n with honest error bars is unique.

There are no technical dependencies on the schema work, but the results validate or falsify
every other CR in this set: if structured process does not beat a good CLAUDE.md on defect
escapes and rework, the enforcement layer is ceremony and we should know.

## Goals / Non-Goals

**Goals**

- A repeatable harness: fixed task set, pinned model and version, scripted runs, recorded raw
  transcripts.
- Four metrics per run: tokens consumed, wall time, defect escapes (bugs surviving to the
  "done" claim, caught by a held-back test suite), rework rate (share of runs needing a
  follow-up fix pass).
- Pre-registered protocol: task set, metrics, and comparison baseline are committed before
  the first measured run, so the result cannot be quietly reshaped.
- Published results either way, in keeping with the anti-hype editorial stance.

**Non-Goals**

- A general agent benchmark or leaderboard; this measures one tool against one baseline.
- Statistical significance at small n; we report effect sizes with honest error bars instead.
- Marketing copy; CR0177 consumes the numbers, this RFC only produces them.

---

## Design Options

### Option A - Fixture-repo harness with held-back test suites (recommended)

**Approach:** two or three small fixture repos (one greenfield feature addition, two
brownfield bug-fix tasks) each with a hidden acceptance test suite the agent never sees.
Each task runs N times per arm (sdlc-studio arm vs plain-Claude-Code-with-good-CLAUDE.md arm).
Defect escape = hidden suite fails after the arm declares done. Harness is a bash/Python
runner in `tools/bench/` recording tokens and wall time from transcripts.

**Pros:** defect escapes are measured by an oracle, not judged; fully repeatable; fixtures
version with the repo.
**Cons:** fixture construction effort; risk that fixtures flatter the pipeline shape.
**Effort / risk:** M-L; fixture bias is the main validity threat, mitigated by publishing
fixtures with results.

### Option B - Live-project A/B on real backlog items

**Approach:** run alternating real CRs in this repo with and without the pipeline.

**Pros:** ecological validity.
**Cons:** no two backlog items are comparable; unblinded; unrepeatable; n effectively 1 per
task. Rejected as the primary method; acceptable as a clearly labelled anecdotal supplement.

### Option C - Third-party benchmark reuse (SWE-bench-style subset)

**Approach:** adapt a public benchmark subset as the task set.

**Pros:** external credibility; no fixture-authoring bias.
**Cons:** tasks are bug-patch-shaped only, which measures none of the lifecycle claims
(specs, drift, verification); heavy setup. Rejected for v1, revisit if results are contested.

---

## Recommendation

Option A, with Option B anecdotes clearly labelled as such. Pre-register the protocol in the
RFC before the first measured run.

## Open Decisions

| # | Decision | Options | Owner | Resolution | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | N per arm per task (cost vs error-bar width) | 3 / 5 / 10 | Sam | **N=5** as the default, with a de-risking spike first: run N=1 across the fixtures to prove the harness and get a rough effect-size read before committing the full 5x. Report error bars honestly at whatever N the budget allows. | Resolved |
| D2 | What "a good CLAUDE.md" is for the baseline arm (must be genuinely good, or the comparison is a straw man) | adapt Anthropic best-practice template / commission one blind | Sam | **Adapt the published best-practice template**, then have a review seat that is NOT the harness author sign it off as genuinely good - a straw-man baseline fails the CR's acceptance criteria. | Resolved |
| D3 | Publication venue (repo docs/ vs blog) | repo-first (leaning) | Lena | **Repo-first** (`docs/benchmarks/`), operator may additionally publish externally. The commitment is to publish regardless of outcome, wherever it lands. | Resolved |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Results are unflattering | Medium | Reputational | Publish anyway - that is the point; unflattering numbers with error bars beat flattering assertions |
| Fixture bias favours the pipeline | Medium | High (validity) | Publish fixtures and protocol with results; invite replication |
| Model drift invalidates comparisons over time | High | Medium | Pin model version per run; report it; treat cross-version comparison as out of scope |

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | Protocol pre-registration (task set, metrics, baseline CLAUDE.md) | CR0178 (scoped item) | RFC acceptance |
| WS2 | Harness runner + fixtures + hidden suites | CR0178 | WS1 |
| WS3 | First measured run + published report | CR0178 (scoped item) | WS2 |

## Decision

**Outcome:** Accepted - Option A (fixture-repo harness with held-back test suites), with
Option B anecdotes clearly labelled. Protocol pre-registered before the first measured run.
**Rationale:** It is the only option whose defect-escape metric is measured by an oracle, not
judged, and it exercises the lifecycle claims a bug-patch benchmark (Option C) cannot. The
publish-regardless-of-outcome commitment stands; the honest-error-bars stance makes even a
small n unique in the category. N=5 with an N=1 de-risking spike first, an independently
reviewed baseline, repo-first publication.
**Spawned CRs:** [CR-0178](../change-requests/CR0178-benchmark-harness-implementation-fixed-task-set-tokens-wall.md)
(WS1 protocol pre-registration, WS2 harness + fixtures + hidden suites, WS3 first run +
published report). Note: the WS1 de-risking spike should run EARLY - it validates or falsifies
the premise of the whole v4 investment, so it is worth pulling ahead of the full build.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Drafted protocol options; committed to publish-regardless-of-outcome |
| 2026-07-06 | Sam Eriksson (QA amigo) | Open decisions resolved; accepted for v4; WS1 spike pulled early |
