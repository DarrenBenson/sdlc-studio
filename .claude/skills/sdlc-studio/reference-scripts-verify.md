# Script Catalogue - Reconcile, verify & checks

<!-- Load when: you need the full detail for a script in this group. The lean
     index with all groups is reference-scripts.md. -->

Detail pages for the **reconcile, verify & checks** scripts. See
[reference-scripts.md](reference-scripts.md) for the full index across all groups.

## Scripts

### `gate.py`

Portable, ecosystem-neutral CI quality gate. Aggregates the deterministic checks
(conformance, reconcile drift, validate, constitution, integrity) into one consolidated
pass/fail and exits non-zero only when a blocking check fails. `--only` / `--skip` select
checks; constitution blocks only when `constitution.enforce` is set. No network, no CI
assumption - runnable in any CI or a pre-commit hook (see `help/gate.md` for wiring). The
check registry is injectable, so the aggregation logic is unit-tested without a full repo.
`--require-retro RETROxxxx` adds a blocking close-gate check: the sprint/review close fails
loud until the named batch retro exists in `sdlc-studio/retros/` (the hard retro gate).

### `verify_ac.py`

Executes AC verifiers defined in story files and updates each AC's
`Verified:` line. Drives `/sdlc-studio reconcile --verify`.

- `run`: walk stories, run verifiers, write report (`--id USNNNN` resolves one story)
- `report`: print the latest verification report
- `lint`: advisory - flag Verify lines that fall through to `shell` as mis-written runner
  calls (`npm test -- ... -t`, `curl ... returns N`), nudging to the DSL
- `ts-check --spec <ts>`: validate a test-spec's AC Coverage Matrix is not decorative -
  every AC mapped to a passing test case, no placeholders; `--verify-report` cross-checks the
  matrix's claimed status against the live report
- `epic-ts --epic EPxxxx`: require an epic to have a test-spec (linked by its `Epic:` field)
  whose matrix passes `ts-check` - the hard epic-scope TS requirement, gated by
  `quality.epic_requires_test_spec` (default true; single-story work is exempt)

Full workflow: `reference-verify.md`. User-facing help:
`help/verify.md`.

### `mutation.py`

The executable mutation-check gate - the complement of `verify_ac.py`: verify_ac
confirms an AC's tests PASS; mutation asks whether they would FAIL if the feature
broke. Applies a declared, bounded set of textual mutations (invert-guard,
stub-return-null, unset-delivered-field, no-op-mapper) to a selected surface via
per-language pattern profiles, re-runs the test command per mutation, and reports
**killed vs survived** - a survivor is a finding. Deterministic (same code plus the
same set gives the same report); honest degrade (an un-mutatable file/class is
reported un-checked, a red baseline yields error verdicts, ceiling truncation is
counted, never silent).

- `run --test CMD` with a surface: `--files a.py ...`, `--since REF` (git diff),
  or `--story USxxxx` (the story's epic/CR `Affects`); `--max-mutations N`
  (default `quality.mutation_max`, else 25); writes
  `sdlc-studio/.local/mutation-report.json`; exits non-zero on survivors/errors
- `prefilter --tests <paths>`: advisory list of test files with no recognisable
  assertion - the cheap static signal for which tests to mutate first

The gate's `mutation` lane surfaces the report (advisory in v1; an absent report
reads not-run, never PASS). User-facing help: `help/mutation.md`.

### `reconcile.py` (read-only)

Builds the artifact-file census and reports `_index.md` drift as JSON.

- `detect`: census + drift report (`--scope`, `--write-report`)
- `apply`: mechanical fixes - status cells + summary counts, behind `--dry-run`
- `fields`: project file-owned cells (Title, Points, Persona) from the files into the index, so
  it is fully derived; `--apply` writes, default reports. A field absent in the
  file is left untouched. Persona reads the canonical `> **Persona:**` story field

Drift kinds: `status-mismatch`, `missing-row`, `orphan-row`, `count-mismatch`,
`missing-index`. Claude consumes the report, applies the edits, and handles the
checkbox/dependency/PRD-feature and CR-cascade drift that needs judgement.
Full workflow: `reference-reconcile.md`.

### `status.py` (read-only)

- `pillars`: four-pillar census (Requirements/Code/Tests/Reviews) as JSON
- `hint`: the next mechanical action
- `backlog [--type <t>]`: the non-terminal (open) artefacts per type and status, from a file
  census - the deterministic "what is left in the backlog?" answer. Terminal detection uses the
  shared vocab's full terminal set (`is_terminal_status`), not a hardcoded Done/Closed subset, so
  every terminal status (e.g. a bug's Fixed/Verified/Superseded) is excluded; an empty backlog
  says so explicitly. `--format json` for tooling.
- `tranche --value <ref>`: list every artefact carrying `> **Tranche:** <ref>` (the
  "what shipped in tranche X" query; the reference is orchestrator-set, never allocated)
- `triage-metrics`: schema-v3 triage quality (false-positive rate + severity inflation)

Live metrics (lint, type-check, coverage) are left to Claude to run. Help:
`help/status.md`, `help/hint.md`.

### `validate.py` (read-only)

- `check`: lint artifact structure (ID, Status vocabulary, title, AC presence, an optional
  record-only `Tranche` reference whose only shape rule is non-empty-when-present)
- `instructions`: hygiene-check the project's `AGENTS.md` / `CLAUDE.md` (AGENTS.md
  canonical, CLAUDE.md a `@AGENTS.md` pointer, operating-doctrine + `LATEST.md`
  pointers present, pre-release gate + compaction rule present, no per-ship-narrative
  bloat). Used by `/sdlc-studio init` (seed-or-check) and `/sdlc-studio review`.
- `personas`: cast-role-aware well-formedness for design personas plus the stakeholder
  panel schema (advisory; its one error is two Primary personas declaring the same
  `Interface:`)
- `seats`: error-level floor for working-team seat cards (role, review render,
  demographic denylist, cast cap, provenance-stamp grammar); `--require-stamp FILE...`
  additionally requires a valid stamp or reviewed marker on each named just-generated
  card and fails loudly on any path it cannot match
- `serves`: persona-coverage report over `**Serves:**` tags (dormant until the first
  tag or `serves_coverage: true`; resolves names to persona files, flags units serving
  nobody, prints a coverage table keyed on the resolved file; advisory). Granularity is
  per FILE: each story is a unit and prd.md is one unit, so a PRD with one tagged
  feature passes - tag per feature if you want per-feature accountability. Fenced code
  blocks are ignored (quoting the convention never activates the check)

Exits non-zero when any error-severity violation is found. Used by Ready-status
checks (`reference-decisions.md`) and as a reconcile pre-step.

### `conformance.py`

The lifecycle-conformance gate. `detect_conformance` reports per-story stages (decomposed -> AC -> verifiable -> verified -> reconciled -> critiqued -> documented) and hard-fails any terminal unit with a stage missing. Repo-global signals (reconciled, documented) apply to every Done unit.

A failure does not just print a count. The gate and `conformance check` name the two whole-batch remedies inline: set `conformance.adopt_after` (forward-only adoption - accepts a bare id `103` or prefixed `US0103`, and ids up to and including the cutoff are exempt), or run `verify_ac` and back-annotate `- **Verified:**` to clear per-unit debt. The output also distinguishes unadopted-discipline debt (most units mass-missing the same stage - pre-existing, forward-only) from scattered per-unit gaps that may be a regression, so a grown-but-accepted count is not mistaken for a fresh breakage. The cutoff is parsed by the shared `sdlc_md.parse_cutoff` (one parser for both gates), which raises a clear error on an unparseable value rather than silently disabling the cutoff.

### `doc_coverage.py`

The documentation-coverage check - the `documented` DoD floor. Hard-fails when a Type-Reference command lacks a help/help.md catalogue entry or a script lacks a reference-scripts.md entry; warns on an empty CHANGELOG [Unreleased]. No-op for consuming repos (no SKILL.md). Wired into the gate + conformance.

### `doc_freshness.py`

Advisory freshness check for `sdlc-studio/reviews/LATEST.md` - the state anchor drifts silently. Compares the facts LATEST.md *claims* (version, script-test count, disclosure count) against reality (SKILL.md version, the `def test_` census, `disclosure.check`) and flags mismatches. Only checks a fact LATEST.md actually states; never blocks; no-op off the skill repo. Wired into the gate as advisory.

### `integrity.py`

Referential integrity. `detect_integrity` flags missing required links (e.g. a story with no epic) and dangling references across the artifact graph; errors vs advisories.
