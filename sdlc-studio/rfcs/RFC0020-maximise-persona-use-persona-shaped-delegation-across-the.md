# RFC-0020: Maximise persona use - persona-shaped delegation across the SDLC lifecycle

> **Status:** Draft
> **Date:** 2026-06-25
> **Created-by:** sdlc-studio file

## Summary

The skill has rich persona machinery (RFC0016 review seats - Product/Engineering/QA Three Amigos + document owners; RFC0017 Cooper design personas) but uses it ONLY for review/consult: the independent critic, spec review, and WSJF seat scoring. The WORKERS that author specs/stories, build code, and write tests are generic and unframed - the main loop, or a blank general-purpose subagent (a field agent built the whole EP0005 SPA with a generic general-purpose agent). Operator direction: MAXIMISE persona use - each lifecycle role should be performed by a subagent framed as the relevant persona/seat. Proposed role->seat mapping for the WORKERS: Product Owner/Manager authors PRD + stories (create-mode authoring + story decomposition); Engineering implements (the agentic wave / build sub-agent); QA authors test-specs + tests + runs verification. The review seats keep reviewing - but the LOAD-BEARING invariant is that the reviewing seat is ALWAYS a separate instance from the authoring seat (never self-review; author/critic separation). Open decisions: (D1) which stages get framing; (D2) main-loop-adopts-the-seat vs only-delegated-subagents-are-framed; (D3) how independence is enforced; (D4) charter source - extend the review-seat charters with build/author/test variants, or reuse; (D5) degradation without personas (--skip-personas -> generic); (D6) interplay of review-seats (RFC0016) and design-personas (RFC0017). Implementing the full vision is feature-sized (a later minor release), not the v3.0.2 patch.

## Design Options

- **A (recommended): persona-shape all three worker roles (Product authors, Engineering builds, QA tests) at the subagent-delegation layer, reusing/extending the review-seat charters, independence invariant preserved (reviewer always a separate seat instance), degrade to generic without personas. Slice into CRs: CR0116 (Engineering build) + QA-test + Product-author**
- **B: persona-shape only the highest-value delegations (Engineering build + QA test); leave PRD/story authoring to the main loop**
- **C: status quo - personas review only; workers stay generic**

## Recommendation

A - the role->seat mapping is the natural completion of the Three Amigos model (they already review; let them also author/build/test as separate seats), maximising persona use while preserving author/critic separation. Frame at the delegation layer; degrade gracefully. CR0116 is the proven first slice (Engineering build); add QA-test and Product-author slices on acceptance

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Act on this finding or keep status quo | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | audit | Filed |
