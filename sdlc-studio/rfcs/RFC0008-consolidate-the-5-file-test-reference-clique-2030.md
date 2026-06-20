# RFC-0008: Consolidate the 5-file test reference clique (~2030 lines, triplicated anti-patterns, two files unreachable from the router)

> **Status:** Draft
> **Priority:** Medium
> **Author:** Adversarial Audit
> **Date:** 2026-06-20
> **Spans:** sdlc-studio skill
> **Related:** RV0002 (audit run)
> **Supersedes / Superseded by:** --

## Summary

Five mutually-linking test reference files total ~2030 lines; two (test-pitfalls, test-validation) appear nowhere in the Progressive Loading Guide and are reachable only via the clique, and anti-patterns are catalogued three times across the set.

## Context & Problem

reference-test-best-practices.md (606), -validation.md (509), -e2e-guidelines.md (516), -automation.md (461), -pitfalls.md (145) cross-reference each other heavily but the router exposes a single test slot (Choosing TDD loads test-best-practices.md as secondary). test-pitfalls.md and test-validation.md appear nowhere in SKILL.md or any help/*.md, so the reader must traverse the clique to find them. Anti-patterns are catalogued three times: the whole of reference-test-pitfalls.md, reference-test-best-practices.md#test-anti-patterns (line 479), and reference-test-best-practices.md#common-ai-testing-mistakes (line 118), which drift independently.

## Design Options

### Option A - act on the finding

Fold reference-test-pitfalls.md (145 lines) and the #common-ai-testing-mistakes section into the single #test-anti-patterns section of reference-test-best-practices.md, deleting the standalone file. Either merge test-validation.md and test-e2e-guidelines.md into test-best-practices.md (one progressively-anchored test reference) or, if they stay separate, add explicit Progressive Loading Guide rows so they are reachable from the router rather than only via the clique. RFC because it removes/merges capability files and needs a call on the desired number of test references.

### Option B - status quo

Keep the current behaviour and accept the trade-off described above.

## Recommendation

TBD - pending the Open Decision below.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Act on this finding or keep status quo | Option A / Option B | Operator | spike or operator call | Open |

## Evidence

reference-test-pitfalls.md (whole file) plus reference-test-best-practices.md:479 and :118 = three anti-pattern catalogues; grep shows test-pitfalls.md and test-validation.md absent from SKILL.md and all help/*.md

## Impact

Choosing TDD pulls test-best-practices.md (24KB) which fans out across four more files (~1500 lines, much overlapping) to answer one question; two of five files are undiscoverable from the router so they are paid for in maintenance and repo weight but rarely loaded, and the triplicated anti-pattern lists drift. Token/maintenance risk medium.

## Decision

**Outcome:** TBD
**Rationale:** TBD

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: over-engineering) |
