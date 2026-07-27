# RFC-0056: Keep the TRD and TSD true: mechanical claim-drift detection and a consumption path

> **Status:** Draft
> **Size:** M
> **Affects:** sdlc-studio/trd.md, sdlc-studio/tsd.md, .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/scripts/gate.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; skill v5.0.0

## Summary

The 2026-07-27 project audit surfaced eleven PRD/TRD/TSD drift findings (BG0308-BG0311, CR0427-CR0432, BG0332): both documents declared version 4.1.0 against shipped 5.0.0, claimed a under-a-minute suite against a measured ~200s run inside a 316s gate, carried a rotted ADR-011, and pinned counts (30/41 command types, 58/70 scripts) the repo contradicts. The structural cause is consumption, not authorship: the PRD steers because epics and stories decompose from it and traceability is checked; nothing consumes the TRD or TSD, so they are write-only between reactive spec-truth refresh epics (EP0071 was one) and rot at the rate the code moves. This RFC explores how to make them self-truing rather than periodically repaired.

## Design Options

- **O1 Mechanical spec-claim drift detector: derivable claims in TRD/TSD (version strings, counts of commands/scripts/lanes, timing claims, enumerated surfaces) are checked against the repo at commit time, extending `doc_freshness` and the numeric-claim drift pattern. Catches the whole audited drift class for zero tokens; requires a convention marking which claims are derivable.**
- **O2 TSD as consumed contract: a gate lane derives (or at minimum existence-checks) the gate set from the gates the TSD declares, so a declared-but-not-running gate fails loud and the TSD becomes load-bearing for CI rather than descriptive.**
- **O3 Plan-cites-TRD: code plan requires naming the TRD section or ADR the implementation builds under, so architecture drift surfaces at planning time in the unit that causes it, not at the next audit.**
- **O4 Status quo: keep periodic spec-truth refresh epics and audit lenses; accept drift between passes as the cost of keeping the documents cheap to write.**

## Recommendation

Adopt O1 as the floor - it is the cheapest and covers every finding class the audit paid ~14M tokens to re-derive - and explore O2 and O3 as follow-on CRs once O1 establishes the derivable-claim convention. Decompose after acceptance.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Choose between: O1 Mechanical spec-claim drift detector: derivable claims in TRD/TSD (version strings, counts of commands/scripts/lanes, timing claims, enumerated surfaces) are checked against the repo at commit time, extending `doc_freshness` and the numeric-claim drift pattern. Catches the whole audited drift class for zero tokens; requires a convention marking which claims are derivable., O2 TSD as consumed contract: a gate lane derives (or at minimum existence-checks) the gate set from the gates the TSD declares, so a declared-but-not-running gate fails loud and the TSD becomes load-bearing for CI rather than descriptive., O3 Plan-cites-TRD: code plan requires naming the TRD section or ADR the implementation builds under, so architecture drift surfaces at planning time in the unit that causes it, not at the next audit. or O4 Status quo: keep periodic spec-truth refresh epics and audit lenses; accept drift between passes as the cost of keeping the documents cheap to write. | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 | Filed |
