# CR-0193: Benchmark v2: tiered fixtures, auditability metric, protocol re-registration

> **Status:** Proposed
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** P2
> **Type:** design-change
> **RFC:** RFC-0025 (fixture-design decision after the N=1 spike, D0012)

## Summary

Benchmark v2, the D0012 fixture-design decision made openly: (1) two new Tier-1 fixtures
sized to cross the pipeline's engagement threshold - `multifile-notify-digest`
(hidden-requirement discovery: under-specified ticket, ~7 interdependent files, a SPEC.md
whose requirements silently interact with the ticket) and `change-request-ledger-drift`
(drift control: a CR whose tempting implementation breaks adjacent spec'd behaviours) - each
with a validated hidden suite and a reference/ solution + seeded-bug variant; the 3 small v1
fixtures kept as a Tier-2 scale-down control. (2) A fifth pre-registered metric,
**Auditability**: held-back audit quizzes scored on outcome answerability (never artifact
presence; reviewer-independence reported descriptively at weight 0), graded by
`tools/bench/audit_quiz.py` (deterministic evidence checks against per-question mutants +
citation-validated auditor-agent answers). (3) Harness hardening: score() subdirectory
support, environmental arm isolation (skill copied INTO A/R workspaces, absent from B),
`transcript_metrics.py` automatic token/time capture with manual fallback flagged
`metrics_source: manual`, summary min/max. (4) `docs/benchmarks/protocol-v2.md` - a new
pre-registration superseding the frozen v1 (one status line appended to v1, body untouched),
with a pre-declared calibration rule and cut order.

## Acceptance Criteria

- [ ] Both Tier-1 fixtures' hidden suites fail on their seeded-bug variant and pass on their reference solution before any arm runs
- [ ] Everything needed to pass a hidden suite is present in the visible workspace (spec + code) - fairness invariant, checked in review
- [ ] Audit quizzes are held back (never copied by prepare), independently reviewed for fairness, and contain no question naming or presupposing an sdlc-studio artifact
- [ ] Class-D grading proves cited evidence is real (test passes on workspace, fails on the per-question mutant); Class-T validation rejects a fabricated citation
- [ ] protocol-v2.md pre-registers task set, five metrics, N (Tier 1 N=5, Tier 2 N=2), calibration rule and cut order; v1 body unchanged apart from a superseded status line
- [ ] score() handles hidden/ subdirectories; arm B workspaces contain no .claude/skills/sdlc-studio; tokens/time captured via transcript_metrics.py with manual fallback disclosed
- [ ] test_benchmark_protocol.py gains a v2 class; test_bench_runner.py covers the new harness behaviour

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | spike D0012 fixture-design decision | Created via `new` (deterministic) |
