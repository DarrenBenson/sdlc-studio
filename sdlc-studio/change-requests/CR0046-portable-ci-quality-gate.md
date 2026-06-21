# CR-0046: portable quality-gate entrypoint for CI (ecosystem-neutral)

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Darren Benson (from the v2.2 usage retrospective)
> **Date:** 2026-06-21
> **Affects:** scripts/gate.py (new), reference-doctrine.md, docs/ (CI wiring), templates/ci/ (examples)
> **Depends on:** conformance.py, reconcile.py, validate.py, constitution.py
> **GitHub Issue:** --

## Summary

The deterministic checks (conformance, reconcile, validate, constitution, integrity) are
ideal PR gates, but the skill ships its own CI only - a consuming project has no drop-in
way to **enforce** the discipline on its PRs. This makes the discipline *available* but
not *enforced*. Ship a single **ecosystem-neutral** `gate` entrypoint that runs the
checks and exits non-zero on failure, so **any** CI (GitHub Actions, GitLab, Jenkins,
Buildkite, a local pre-commit hook) can call it - no GitHub lock-in.

## Problem

Each check is a separate script with its own flags/exit codes. There is no one command a
CI step can run to assert "the artifact graph is conformant + drift-free + valid +
constitution-clean," and no shipped wiring. Without enforcement, drift creeps back.

## Proposed Changes

- **`scripts/gate.py`** - a single aggregator: run conformance + reconcile (drift) +
  validate + constitution (when present) + integrity; print a consolidated report; exit
  non-zero if any *blocking* check fails. Flags to select/skip checks and to set the
  severity floor. Pure stdlib; no network; no ecosystem assumption.
- **Portable wiring docs** - `reference-doctrine.md` + `docs/`: "run `gate` in CI" with
  copy-paste examples for **multiple** systems (a GitHub Action, a GitLab job, a generic
  shell step, a pre-commit hook). The GitHub Action is **one example, not the mechanism**.
- Optional `templates/ci/` snippets per system.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/gate.py | the one-command CI gate over the existing checks | New |
| reference-doctrine.md / docs / templates/ci | portable wiring (multi-system examples) | New / Modified |

### Breaking Changes

None. Additive; reuses the existing checks.

## Acceptance Criteria

- [x] `gate` runs conformance + reconcile + validate + constitution (+ integrity), prints a consolidated pass/fail, and exits non-zero only when a blocking check fails; `--skip`/`--only` select checks.
- [x] It makes no network call and assumes no CI ecosystem - runnable as a bare shell command.
- [x] Wiring docs show **at least three** CI systems (GitHub Action, GitLab, generic shell / pre-commit), with GitHub presented as one example among equals.
- [x] Unit-tested (aggregation + exit codes incl. a passing and a failing fixture); independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0046) | Complete - US0031: gate.py + CI wiring; critic REJECT->fixed (root guard) |
| 2026-06-21 | Darren Benson | Raised - turn the deterministic checks into an enforceable, ecosystem-neutral CI gate (portable-first; GitHub is just one example) |
