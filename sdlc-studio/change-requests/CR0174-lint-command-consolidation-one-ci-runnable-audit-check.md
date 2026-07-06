# CR-0174: Lint command consolidation: one CI-runnable audit-check enforcing the team-schema rules

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0013](../epics/EP0013-structured-authorship-and-policy-enforcement.md)
> **Priority:** Medium
> **Type:** Enhancement
> **Raised-by:** Sam Eriksson (QA amigo)
> **Depends on:** CR0169 (plus rule-defining CRs 0168, 0170, 0171, 0172, and RFC0024 id format)

## Summary

A single lint / audit-check command, CI-runnable, that enforces the schema-v3 team rules in
one pass: structured authorship present, evidence fields present per type, raiser and
triager distinct, indexes untouched by hand, id format valid.

## Motivation

The rules landing across CR0168 to CR0172 each ship with their own check wired into
`validate.py` or a repo guard. Left as five separately invoked checks, they will be run
unevenly and skipped individually - the exact failure mode AGENTS.md documents for this
repo's own guard suite. One command with one exit code is what CI, the pre-commit hook, and
the portable `gate.py` can hold the line with.

This is also the concrete enforcement point aligned with the publicly committed crew audit
linter: each rule here should be built as a worked example for that work - named rule,
fixture that fails, message that names the fix - so the crew linter inherits a tested rule
catalogue rather than a specification.

## Scope

**In scope**

- One command (working name `/sdlc-studio lint`, script `lint.py` or an `audit check`
  subcommand) running the full rule set:
  1. structured `raised_by`/`triaged_by` present and resolvable (CR0169);
  2. per-type evidence fields present and non-placeholder (CR0171);
  3. `triaged_by != raised_by` on triaged artefacts (CR0170);
  4. `_index.md` regenerable byte-identically, no hand edits (CR0168);
  5. id format valid for the artefact's schema era (RFC0024/CR0167);
  6. `tranche:` shape valid when present (CR0172).
- Output: one line per violation (rule id, artefact, fix hint); `--format json` for CI;
  non-zero exit on any violation.
- Wired into `gate.py`, the pre-commit hook, and documented in `reference-scripts.md`.
- Each rule implemented as an isolated, individually testable check function with its own
  failing fixture (the worked-example requirement).

**Out of scope**

- New rules beyond the six above; the frame is extensible but this CR ships only what the
  schema CRs define.
- Prose style linting (`lint-style.sh` remains separate; different audience and cadence).
- Auto-fixing; `reconcile apply` fixes what is mechanical, the lint only reports.

## Acceptance Criteria

- [ ] One command runs all six rules and exits non-zero on any violation; a clean run on
      this repo's workspace exits zero.
- [ ] Every rule has a fixture that fails it and a test asserting the failure message names
      the rule and the fix.
- [ ] `gate.py` includes the lint so consuming projects get it in the portable CI gate.
- [ ] JSON output is stable and documented (schema in help), suitable for the crew audit
      linter to consume as a reference implementation.
- [ ] Rule identifiers are stable strings (e.g. `authorship-structured`, `evidence-present`,
      `duties-separated`, `index-derived`, `id-format`, `tranche-shape`).

## Dependencies

| Artefact | Relationship |
| --- | --- |
| CR0169 | Blocking: authorship rules |
| CR0168, CR0170, CR0171, CR0172 | Blocking per rule: each defines a rule this command runs; the command can ship dark and enable rules as they land |
| RFC0024 / CR0167 | Id-format rule follows the ratified scheme |

## Effort

**M.** The rules exist in their home CRs; this CR is the runner, the stable interface, the
fixtures, and the CI wiring.

## Risk

A consolidated lint that is slow or flaky gets bypassed with `--no-verify`, taking all six
rules down with it (single point of failure is the flip side of single point of
enforcement). Mitigation: rules are pure file reads (fast), and any rule can be disabled by
config individually so one bad rule does not force bypassing the suite.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full scope drafted; six stable rule ids as crew-linter worked examples |
