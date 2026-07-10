# EP0010: Skill self-improvement: token economy + learning loop (consuming-repo lessons)

> **Status:** Done
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new

## Summary

The sprint batch distilled from the consuming repos' lessons logs: cut the routine token cost of
derived indexes and lessons, and make the learning loop honest and durable. Two CRs form the
headline spine - CR0125 (index archive) and CR0129 (sprint retro lifecycle) - flanked by two cheap
documentation enrichments (CR0126 agentic-wave doctrine, CR0127 pre-deploy readiness). CR0128
(test-strategy heuristics) is held for a dedicated test-focused sprint.

## Inherited Constraints

> See PRD and TRD for full constraint details. Key constraints for this epic:

| Source | Type         | Constraint                                                                                 | Impact                                               |
| ------ | ------------ | ------------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| PRD    | Performance  | Not applicable - skill-internal change                                                     | Token-economy work reduces load, does not regress it |
| PRD    | Security     | Not applicable - skill-internal change                                                     | No new attack surface                                |
| TRD    | Architecture | Pure-stdlib Python scripts; the file census is the authority, indexes are derived (LL0001) | Writers must keep the census the source of truth     |
| TRD    | Tech Stack   | Python 3.10+, no third-party deps; deterministic tooling that fails loud (LL0008)          | New verbs are script-backed with unit tests          |

---

## Business Context

### Problem Statement

Derived `_index.md` tables and per-project lessons grow monotonically; on a mature consuming repo
99% of index rows are terminal and the routinely-loaded index is almost pure dead weight. Separately
the closing retro is doctrine, not a gate, so it is silently skipped and hard-won lessons stay
stranded in gitignored files that never travel and were never promoted.

**PRD Reference:** [Maintenance surface](../prd.md)

### Value Proposition

Reduce the per-session token cost of indexes and lessons by relocating terminal detail to derived
archives (kept discoverable), and make the learning loop unskippable and self-distilling, so every
sprint reads a cheap, current summary instead of the full log.

### Success Metrics

| Metric                            | Current               | Target               | Measurement              |
| --------------------------------- | --------------------- | -------------------- | ------------------------ |
| Live index lines on a mature repo | ~3,500                | ~150 (-95%)          | line count after archive |
| Sprint close without a retro      | silently allowed      | fails loud           | close-gate test          |
| Cross-project lesson promotions   | 0 (until LL0009/0010) | harvested each retro | LL index growth          |

---

## Scope

### In Scope

- The index-archive writer + terminal-status vocab flag + next_id archive-union (CR0125)
- The retro close-gate, lessons re-validation, and rolling summary (CR0129)
- The agentic-wave and pre-deploy doctrine enrichments (CR0126, CR0127)
- CI/dependency maintenance: restore the coverage gate to green and adopt the Dependabot action bumps
- The blocker sweep: detect now-unblocked units (cross-project via PVD), wired pre-plan + reconcile (CR0130)

### Out of Scope

- CR0128 test-strategy heuristics (held for a test-focused sprint)
- Monolithic PRD/TRD/TSD section-sharding (separate RFC)

### Affected Personas

- **Dani (Engineering):** builds the deterministic verbs and docs
- **The operator:** reads smaller indexes and a current lessons summary; cannot skip the retro

---

## Acceptance Criteria (Epic Level)

- [ ] live indexes carry only active rows; terminal rows relocated to `<type>/archive/` stay
      censused and discoverable (reconcile drift 0)
- [ ] the sprint close fails loud without a batch retro, and a rolling `LESSONS-SUMMARY.md` is
      generated and read at sprint start
- [ ] the agentic-wave and pre-deploy doctrine are documented in the skill
- [ ] all new verbs are script-backed with unit tests; `npm test` and `npm run lint` green

---

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| ---------- | ---- | ------ | ----- |
| None       | -    | -      | -     |

### Blocking

| Item                                          | Type    | Impact                                 |
| --------------------------------------------- | ------- | -------------------------------------- |
| Future bloat-reduction across consuming repos | enables | The archive writer is the prerequisite |

---

## Risks & Assumptions

### Assumptions

- The reconcile read-path archive union (reconcile.py:240-246) is stable and complete

### Risks

| Risk                                  | Likelihood | Impact | Mitigation                                              |
| ------------------------------------- | ---------- | ------ | ------------------------------------------------------- |
| Writer drops a row it cannot classify | Low        | High   | Fail loud, no partial write (LL0008); idempotency test  |
| Status vocab differs per project      | Medium     | Medium | Terminal set derived from `status_vocab`, not hardcoded |

---

## Technical Considerations

### Architecture Impact

Extends `reconcile.py`, `next_id.py`, `lessons.py`, and `lib/sdlc_md.py`; no new dependencies. The
file census stays the authority; every new index/lessons artefact is derived and regenerable.

### Integration Points

The sprint close path (gate), `reference-sprint.md` (start-read), and the archive sub-index format
shared with `reconcile.parse_index`.

---

## Sizing

**Story Points:** 31
**Estimated Story Count:** 11

**Complexity Factors:**

- The archive writer touches the most complex file in the repo (`reconcile.py`)
- The retro lifecycle spans the gate, `lessons.py`, and the sprint references

---

## Story Breakdown

- [x] [US0040: index-archive writer + terminal-status vocab flag + dry-run (CR0125)](../stories/US0040-index-archive-writer-terminal-status-vocab-flag-dry.md)
- [x] [US0041: next_id archive-union guard so archived ids are never reallocated (CR0125)](../stories/US0041-next-id-archive-union-guard-so-archived-ids.md)
- [x] [US0042: retro hard close-gate: sprint close fails loud without a batch retro (CR0129)](../stories/US0042-retro-hard-close-gate-sprint-close-fails-loud.md)
- [x] [US0043: lessons re-validation verb: close obsolete lessons by validity (CR0129)](../stories/US0043-lessons-re-validation-verb-close-obsolete-lessons-by.md)
- [x] [US0044: rolling LESSONS-SUMMARY generator + sprint-start read (CR0129)](../stories/US0044-rolling-lessons-summary-generator-sprint-start-read-cr0129.md)
- [x] [US0045: agentic-wave worktree doctrine doc enrichment (CR0126)](../stories/US0045-agentic-wave-worktree-doctrine-doc-enrichment-cr0126.md)
- [x] [US0046: pre-deploy readiness checklist doc (CR0127)](../stories/US0046-pre-deploy-readiness-checklist-doc-cr0127.md)
- [x] [US0047: restore the runtime-scripts coverage gate to green on CI (blocks all PR merges)](../stories/US0047-restore-the-runtime-scripts-coverage-gate-to-green.md)
- [x] [US0048: adopt Dependabot CI action bumps: actions/checkout v7, actions/setup-python v6](../stories/US0048-adopt-dependabot-ci-action-bumps-actions-checkout-v7.md)
- [x] [US0049: blocker-sweep detection: now-unblocked units, in-repo census + cross-repo via PVD manifest (CR0130)](../stories/US0049-blocker-sweep-detection-now-unblocked-units-in-repo.md)
- [x] [US0050: wire the blocker sweep before sprint planning + advisory reconcile lane (CR0130)](../stories/US0050-wire-the-blocker-sweep-before-sprint-planning-advisory.md)

---

## Test Plan

**Test Spec:** [TS0001: EP0010 AC coverage - token economy + learning loop](../test-specs/TS0001-ep0010-ac-coverage-token-economy-learning-loop.md)

---

## Open Questions

- [ ] None - Owner: -

---

## Revision History

| Date       | Author | Change                                                                    |
| ---------- | ------ | ------------------------------------------------------------------------- |
| 2026-06-27 | field  | Created via `new` (deterministic)                                         |
| 2026-06-27 | Lena   | Filled to Ready; scoped to the spine + doc CRs, CR0128 held (design rung) |
