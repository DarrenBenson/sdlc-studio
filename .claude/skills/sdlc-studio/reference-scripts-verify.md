# Script Catalogue - Reconcile, verify & checks

<!-- Load when: you need the full detail for a script in this group. The lean
     index with all groups is reference-scripts.md. -->

Detail pages for the **reconcile, verify & checks** scripts. See
[reference-scripts.md](reference-scripts.md) for the full index across all groups.

## Scripts

### `gate.py`

Portable, ecosystem-neutral CI quality gate. Aggregates the deterministic checks
(conformance, reconcile drift, validate, constitution, integrity, the engagement floor) into
one consolidated pass/fail and exits non-zero only when a blocking check fails. `--only` / `--skip` select
checks; constitution blocks only when `constitution.enforce` is set. No network, no CI
assumption - runnable in any CI or a pre-commit hook (see `help/gate.md` for wiring). The
check registry is injectable, so the aggregation logic is unit-tested without a full repo.
`--require-retro RETROxxxx` is the **sprint-close** form: it binds three blocking lanes, because
the close is one obligation and a flag per step is a flag that gets forgotten.

- `retro` - the named batch retro must exist in `sdlc-studio/retros/`.
- `lessons-summary` - the committed `retros/LESSONS-SUMMARY.md` must be the digest of the CURRENT
  lessons log. The lane **recomputes** that digest and compares, rather than reading a freshness
  stamp: nothing to forge, and a lesson **closed** since the last regeneration fails it exactly as
  an added one does. Layout and whitespace are not compared, so reformatting the file cannot
  false-fire it. Fix: `lessons summary`.
- `lessons-validity` - no open lesson may sit past its `Review-by` horizon, and none may carry no
  horizon at all (unprovable is not proven - a lane that reported only expiries would pass a legacy
  log vacuously). Fix: `lessons revalidate --close` / `--extend` / `--stamp`.

`--require-lessons` binds the two lessons lanes alone (a close with no retro due). They pass on a
project with no lessons **and no summary claiming any** - a greenfield repo has nothing to
summarise, and the detail says so rather than reading as a silent green. They do **not** pass when
the log is missing while the committed summary still lists lessons: the log is gitignored, so
deleting it costs nothing and shows in no diff, and a check that read that as "nothing to
summarise" could be defeated with one `rm`. The summary is the tracked half and the one making a
claim, so the contradiction is refused (restore the log, or run `lessons summary` to clear the
digest).

`--require-close` is the **push/release close guard**: it binds a blocking `close-owed` lane that
fails when any delivery unit reached a terminal state since the close-owed baseline with no retro
accounting for it - a skipped close-down. Unlike the standard checks it is **not** in the plain
gate: a normal gate makes no claim about close-ownership, so it never wears one. The soft,
discoverable half of the same signal is on `status`/`hint` (an advisory line); this is the hard
half that lands where shipping happens. Deselecting the bound `close-owed` lane under it is refused,
as every bound lane is. Backed by `close_owed.py`.

Deselecting a **bound** lane (`--skip lessons-summary`, or an `--only` that omits it) is refused,
not honoured, in every mode: no verdict is printed over the lane that defines it.

`--release` is the **pre-tag** form and the only command needed before a tag: it adds a blocking
`verify` lane that **executes** every story's `Verify:` expression through `verify_ac` and names
each red AC, so the gate and the AC layer fail as ONE exit code instead of two an operator must
remember to read. The lane executes rather than reading the stored `verify-report.json` (a merged
report carries a story's last green forward - a stale green is how a rotted verify layer reaches a
tag), and it writes nothing: no `- **Verified:**` back-annotation, no report rewrite, so the gate
stays read-only and hook-safe. The lane is absent without `--release` - the standard gate does not
run test suites.

`--release` binds a second lane, `review-legs`: every required document leg (PRD/TRD/TSD/Persona)
must be PRESENT or explicitly WAIVED against a recorded decision id, so a tag cannot pass over a
silently-missing required artefact. A prose review can call an absent leg "optional polish"; the
lane cannot be talked around - only the artefact, or a `decisions.py waive --leg <leg>` row, turns
it green. It reads `review_prep.required_legs`. The CODE leg is out of scope (no single testable
artefact) and every verdict states so. It is release-only for the same reason as `verify`: a leg
legitimately absent mid-build is not a standard-gate failure. Deselecting it under `--release` is
refused, as `verify` is.

Nothing to prove is not proof, so the lane fails rather than passing quietly when it has examined
nothing: an empty story set fails, and so does any story carrying an **unspecified** AC - one with
no `Verify:` line at all - which is named (otherwise deleting a rotted verifier would be the way to
a green release). This guard is **per-story**, not repo-wide: `verify_ac` counts an omitted
`Verify:` line (unspecified - nothing was asserted) separately from a declared `Verify: manual` one
(a human-checked judgement call), so one green executable AC elsewhere no longer lets a verifier-less
story ride along, and a story whose ACs are all declared `Verify: manual` passes without being
over-fired on. Deselecting the lane
under `--release` (`--skip verify`, or an `--only` that omits it) is **refused**, not honoured: no
release verdict is printed over an unexamined AC layer. A verifier the trust boundary refused to
run - a shell-backed verb on a story stamped `Provenance: external` - is reported **BLOCKED and
unproven**, never red, since an unrun verifier is not evidence about the code; it still fails the
lane, and `--allow-external` runs it once the content is trusted. `--verify-batch` runs jest once
and resolves jest verifiers from the cached result rather than a cold start per AC.

### `close_owed.py`

The deterministic answer to "is a sprint close owed right now?" - the detector behind the
`status`/`hint` nudge and the gate's `--require-close` lane. A delivery unit (epic / story / bug)
that is terminal is **covered** when some retro's `> **Batch:**` names it; an uncovered terminal
unit is a candidate for an owed close. Because a project that adopts this mid-life carries a large
tail of historically-closed units that predate story-level retro batches, the detector
**baselines**: `close_owed.py baseline` snapshots the exact **set** of ids terminal at adoption into
a committed `.close-owed-baseline.json`, and from then on only a unit that reaches terminal **later**
(one not in that set) can owe a close. A set, not a per-prefix id cutoff: a highest-id cutoff would
silently forgive any unit that was in flight at adoption and closes later - the precise false "none
owed" this feature exists to kill - and breaks entirely on non-numeric (ULID / schema-v3) ids. The
pre-adoption tail is recorded and forgiven, never enforced retroactively, and until a baseline is
stamped the detector reports every uncovered unit and both `detect` and the `status`/`hint` advisory
nudge you to stamp one, rather than enforcing nothing in silence.

- `detect [--format json]` - report the owed units; exits non-zero only when baselined AND a close
  is genuinely owed, so a gate or hook can branch on the exit code. Unbaselined is a soft state
  (exit 0), not a failure.
- `baseline [--date] [--note]` - stamp the grandfather set once, at adoption.

`hooks/close_guard.py` is the optional **Stop hook** built on it: wired into a project's
`.claude/settings.json` under `hooks.Stop`, it reminds the agent of an owed close at the moment a
turn would end (the Definition of Done's close clause, enforced by the harness rather than recall).
It is default-allow on any doubt - malformed input, unbaselined project, or detector error all let
the turn end - and never hard-locks. See `help/gate.md`.

### `verify_ac.py`

Executes AC verifiers defined in story files and updates each AC's
`Verified:` line. Drives `/sdlc-studio reconcile --verify`.

- `run`: walk stories, run verifiers, write report (`--id USNNNN` resolves one story)
- `report`: print the latest verification report
- `lint`: advisory - flag Verify lines that fall through to `shell` as mis-written runner
  calls (`npm test -- ... -t`, `curl ... returns N`), nudging to the DSL
- `ts-check --spec <ts>`: validate a test-spec's AC Coverage Matrix is not decorative -
  every AC mapped to a passing test case, no placeholders; `--verify-report` cross-checks the
  matrix's claimed status against the live report. A spec that is not there is **refused**
  (exit 2, the path named on stderr) rather than read as an empty one: a typo'd `--spec`
  used to produce a clean matrix and exit 0, so a broken invocation passed as green. Exit 1
  stays "a matrix with findings", so the two are distinguishable by exit code alone
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

Reconcile does **not** archive. Index archival is `archive.py` alone (one layout, one
writer); reconcile only reads the archive sub-indexes into the census.

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
  record-only `Tranche` reference whose only shape rule is non-empty-when-present, and a
  `Template:` tier drawn from `minimal|planning|full` - an unrecognised tier is an error,
  because it would read as "not planning" and silently disable the promotion gate)
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

The lifecycle-conformance gate. `detect_conformance` reports per-story stages (decomposed -> AC -> verifiable -> verified -> reconciled -> critiqued -> documented -> promoted) and hard-fails any terminal unit with a stage missing. Repo-global signals (reconciled, documented) apply to every Done unit.

`promoted` is the backstop to the planning-tier transition gate, sharing its one authority (`lib/tiers.py`): a Done story that is missing the sections the full template carries is non-conformant, because the transition gate that normally refuses it can be walked around by hand-editing the status. It is keyed on the sections, not on the tier stamp - an unknown tier fails closed, and a `full` stamp over missing sections is refused as a claim rather than believed. A story with no tier stamp - every artefact predating the tier - is promoted by definition and never flagged, unless the project sets `quality.require_full_sections: true`, which judges every story on its sections. Remedy: `artifact.py promote --id <ID> --to full`.

A failure does not just print a count. The gate and `conformance check` name the two whole-batch remedies inline: set `conformance.adopt_after` (forward-only adoption - accepts a bare id `103` or prefixed `US0103`, and ids up to and including the cutoff are exempt), or run `verify_ac` and back-annotate `- **Verified:**` to clear per-unit debt. The output also distinguishes unadopted-discipline debt (most units mass-missing the same stage - pre-existing, forward-only) from scattered per-unit gaps that may be a regression, so a grown-but-accepted count is not mistaken for a fresh breakage. The cutoff is parsed by the shared `sdlc_md.parse_cutoff` (one parser for both gates), which raises a clear error on an unparseable value rather than silently disabling the cutoff.

### `engagement_floor.py`

The deterministic engagement floor - the measured rule that a multi-file change gets the planning pass, made mechanical rather than left to the model's own scale-to-size judgement (the weaker-model failure the 2026-07 benchmark rerun exposed). `detect` judges each shipped implementation unit (a story Done, a bug Fixed/Verified/Closed, a CR Complete). A unit may skip the planning pass only by showing it is below the floor: it carries a planning artefact (an acceptance criterion, a `Verify:` line, or a linked plan PL), or it DECLARES a single-file footprint in an `Affects` field. A unit with more than one source file and no planning artefact fails as `unplanned`; a unit that neither plans nor declares fails as `undeclared`. The whole fire/skip decision is a file count and a presence check, with no model call, so it cannot re-introduce the judgement gap it exists to close.

The guarantee, stated precisely (D0026 - it does not overclaim). The floor deterministically catches **pure omission**: a shipped unit that neither planned nor declares a real single-file footprint fails `undeclared`. A declaration must be a **checkable file path** - a path whose basename looks like a file: a dotted path (`src/x.py`), an extension-less real file (`Makefile`, `Dockerfile`, `LICENSE`, `Containerfile`), or a dotfile (`.gitignore`, `.env`). Prose like `n/a`, `various`, `see the commits`, or a version string like `v1.2` can be held to nothing, so it is omission-equivalent and does not count. It also catches **understatement in a solo-id commit**: where a unit declares one file but its commit (naming only that unit) touched more, the git cross-check (`git log --grep=<id>`) raises the count and the floor fires (git only ever raises a count). **Understatement in a shared commit** - a unit sharing its commit with another judged id - was a disclosed limit and is now closable with a `Refs:` trailer (below); a bare co-named subject is still skipped, because git cannot attribute a file to one id among several. This is why requiring the declaration is what closes pure omission: git and `Affects` share a blind spot (git sees a unit only when its commit solely names its id, or a `Refs:` trailer names it), so with no way to skip planning except by declaring, a blank or prose-only `Affects` is itself the failure - and that still catches the benchmark's observed failure, a weak model shipping a multi-file change with no planning. A `.md`/`.yaml` change is not a source change (`complexity.py`'s one suffix set), so a docs-only unit is below the floor.

**Per-id attribution with a `Refs:` trailer.** A commit body line `Refs: <id>` is an explicit statement of which work-item owns the change. The git leg reads it and attributes that commit's files to each id a `Refs:` trailer names, even when the subject co-names other ids - the per-id attribution a bare shared-commit subject cannot give. Grammar: one or more `Refs:` lines, each listing ids separated by commas and/or spaces (`Refs: US0301`, `Refs: US0301, US0302`, or repeated `Refs:` lines); the dashed spelling (`US-0301`) matches too. The trailer is trusted because it is explicit, and it is strictly **additive**: the batch test that decides whether a commit is apportionable reads the **subject line only**, never the body, so a body `Refs:` line can never turn a solo-subject commit into a pseudo-batch and strip that subject id's own cross-check. It therefore only ever raises a count, never lowers one, whatever the body contains - including the conventional see-also use of `Refs:` naming an unrelated id. Each named id gets the commit's full file set (never a divided share). An understated `Affects` in a commit shared with another id is caught once the owning unit carries a `Refs:` trailer.

**The `check-commit-msg` subcommand** is the commit-msg hook's brain: `engagement_floor.py check-commit-msg <file>` warns when a subject names more than one work-item id without a `Refs:` trailer covering them (the case where the git leg would skip the commit). It warns to stderr and exits 0 by default; `--strict` blocks (exit 1) instead. It never blocks on a message it cannot parse. The tracked, opt-in `.githooks/commit-msg` shim wires it in (see reference-config, Engagement Floor); a consuming project opts in per project by pointing its own commit-msg hook at the shipped script.

Three auditable escape valves, no silent judgement: `engagement_floor.adopt_after` in `.config.yaml` grandfathers pre-adoption ids forward-only (the `conformance.adopt_after` precedent) - a cutoff ABOVE the highest existing id is a forward disarm, not grandfathering, and is refused, and exempt units that would violate stay counted so a cutoff cannot hide them; `engagement_floor: judgement` is the project-global opt-out the doctrine and agent-instructions already document, under which the lane still reports but never blocks; and a recorded waiver (`decisions.py waive --subject rule:engagement-floor:<id>` for one unit, or `--subject rule:engagement-floor` for the whole project) - a decisions-log row with a rationale, not a config boolean. Wired into the gate as the blocking `engagement-floor` lane (advisory under judgement mode). The `Affects` field is on the story/bug/CR templates so the declaration has a home.

### `doc_coverage.py`

The documentation-coverage check - the `documented` DoD floor. Hard-fails when a Type-Reference command lacks a help/help.md catalogue entry or a script lacks a reference-scripts.md entry; warns on an empty CHANGELOG [Unreleased]. No-op for consuming repos (no SKILL.md). Wired into the gate + conformance.

### `doc_freshness.py`

Advisory freshness check for `sdlc-studio/reviews/LATEST.md` - the state anchor drifts silently. Compares the facts LATEST.md *claims* (version, script-test count, disclosure count) against reality (SKILL.md version, the `def test_` census, `disclosure.check`) and flags mismatches. Only checks a fact LATEST.md actually states; never blocks; no-op off the skill repo. Wired into the gate as advisory.

### `integrity.py`

Referential integrity. `detect_integrity` flags missing required links (e.g. a story with no epic) and dangling references across the artifact graph; errors vs advisories.
