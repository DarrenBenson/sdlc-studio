# RFC-0027: Roadmap to world-class: reliability tier, gate integrity, era completion and evidence-backed maturity

> **Status:** Accepted
> **Date:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

Synthesis of RV0007 (42 verified findings over code, architecture, reliability, test/CI, defensive security), the RV0005-RV0006 trajectory, and the N=5 benchmark evidence base into a strategic roadmap. Diagnosis: the unit tier, security posture and files-are-truth core are already at or above category norm; what separates this project from world-class is (1) a RELIABILITY TIER - multi-step writers (migrate, archive, batch, sync, close cascade) need journalled/resumable execution, universal atomic writes and locking (finish BG0076), fault-injection and concurrency tests, because every reproduced High this round lives in a crash/resume/concurrent window; (2) GATE INTEGRITY - the meta-layer must verify itself (hook-enablement detection CR0202, gate.py in CI BG0096, fail-loud on crashing checks BG0090, advisory lanes that earn their signal CR0203, machine-generated hygiene claims), because six breaking commits reached main through gaps between green gates; (3) ERA COMPLETION - v3 identity must hold without the single-writer convention (randomness in short ids BG0086, era-aware filing BG0077, alias-aware allocation BG0074, migration journal BG0073, era-aware cascade regexes per the deferred LATEST lens) before multi-agent waves become the normal mode the benchmark positioning sells; (4) EVIDENCE-BACKED MATURITY - anchor docs carry computed numbers not remembered ones, eval scenarios cover each major's breaking surface (BG0079, CR0208 item 19), the benchmark N grows past significance, and cross-platform (Windows) reliability gets CI teeth. Sequencing decided by the operator via the options below.

## Design Options

- **A: Blockers-only then tag. Fix the nine rc-blockers (BG0071-BG0075, BG0077-BG0080), re-run the checklist with the eval row, tag v4.0.0-rc.1; defer all four themes to 4.1+. Fastest tag; ships known post-v4 defect mass.**
- **B: Reliability-first pre-tag. Fold theme 1 (reliability tier: BG0076/81/82/86/91/92, CR0205/0206/0207) into the rc alongside the blockers; tag a heavier but crash-safe 4.0. Slowest tag; strongest first impression for consuming projects.**
- **C: Blockers pre-tag, then three themed epics post-v4 - EP(reliability tier), EP(gate integrity: CR0202/0203, BG0090/0096, hook/CI parity), EP(era completion + DX: BG0086/0077 follow-through, CR0208, json/exit conventions) - sequenced by consuming-project exposure, each closing with a reconcile + eval run.**

## Decision

**Accepted 2026-07-10 by the operator: Option C.** The pre-tag half is already delivered
(the nine blockers shipped as the RV0007 fix pack, RETRO0017; the rc checklist reads green).
The post-tag sequence stands as recommended: (1) gate-integrity epic (CR0202/CR0203,
BG0090/BG0096, hook/CI parity - now joined by CR0209's unit-lifecycle ergonomics as natural
companions), then (2) the reliability tier (BG0076/81/82/86/91/92, CR0205/0206/0207), then
(3) era completion + DX (CR0208/CR0210/CR0211, json/exit conventions, cascade era lens).
Each epic closes with a reconcile + eval run per the recommendation.

## Recommendation

Option C. The nine blockers are surgical (S/M effort) and make the tag honest; holding the tag for the full reliability tier repeats the freeze that made CI dark. Post-tag, gate integrity goes FIRST (it is what lets every later epic trust its own green), then the reliability tier, then era completion/DX. Re-run the four eval scenarios at each epic close and grow the benchmark N alongside - the positioning docs already cite it honestly; make the number decisive.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Act on this finding or keep status quo | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
