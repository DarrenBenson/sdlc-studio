# CR-0161: LATEST.md is a window, not a ledger: history one-liners plus a freshness ceiling

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-05
> **Created-by:** sdlc-studio file

## Summary

The session-start anchor grows ~15 dense lines per sprint because every past sprint keeps its full paragraph, duplicating its retro - 165 lines re-read at every context reset. Restructure to header + gates + current sprint + open backlog + one History line per past sprint pointing at its retro, and add a doc_freshness advisory when LATEST.md exceeds docs.latest_max_lines (default 80). Codify the window rule in reference-operator-heuristics for consuming projects.

## Acceptance Criteria

- [ ] LATEST.md holds only the current sprint in paragraph form; past sprints are one-line History pointers to retros
- [ ] doc_freshness reports an advisory naming the remedy when LATEST.md exceeds the configurable ceiling; under-ceiling stays silent
- [ ] reference-operator-heuristics documents the anchor-window rule

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-05 | audit | Raised |
| 2026-07-05 | Claude (tranche close) | Delivered in the token-optimisation tranche (pre-v3.5.0): Sam Eriksson (QA seat, review render) APPROVE after two adversarial rounds; details in CHANGELOG [Unreleased] |
