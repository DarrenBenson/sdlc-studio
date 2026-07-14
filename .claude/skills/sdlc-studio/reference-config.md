# SDLC Studio Configuration Reference

<!-- Load when: reading or changing project configuration, thresholds, or quality-gate knobs -->

## Contents

- [Configuration Files](#configuration-files)
- [Configuration Loading](#configuration-loading)
- [Coverage Targets](#coverage-targets)
- [Story Quality Gates](#story-quality-gates)
- [TDD Trigger](#tdd-trigger)
- [E2E Limits](#e2e-limits)
- [Epic Perspectives](#epic-perspectives)
- [Review Configuration](#review-configuration)
- [Persona Staleness](#personas-staleness-days)
- [Lessons Validity](#lessons-validity)
- [Skill Source Repo](#skill-source-repo)
- [Contract Tables](#contract-tables)
- [Release Strategy](#release-strategy)
- [Using Config in Templates](#using-config-in-templates)
- [Example Project Config](#example-project-config)
- [Version File](#version-file)
- [Project Implementation](#project-implementation)
- [See Also](#see-also)

Project-level configuration for customising SDLC Studio behaviour.

> `config-defaults.yaml` (in `templates/`) is the single source of truth for default values; the Default columns below mirror it and are guarded against drift by `scripts/tests/test_config.py`. Scripts read it via `scripts/config.py`. Project overrides go in `sdlc-studio/.config.yaml`.

## Configuration Files

| File | Location | Purpose |
| --- | --- | --- |
| `config-defaults.yaml` | `templates/` (skill) | Default values (do not modify) |
| `.config.yaml` | `sdlc-studio/` (project) | Project-specific overrides |
| `.version` | `sdlc-studio/` (project) | Version tracking for upgrades |

## Configuration Loading

```text
1. Load templates/config-defaults.yaml (skill defaults)
2. Check for sdlc-studio/.config.yaml (project overrides)
3. Merge: project values override defaults
4. Use merged config for all commands
```

Project config only needs to specify values that differ from defaults.

**PyYAML dependency (graceful):** parsing `.config.yaml` needs PyYAML (`pip install pyyaml`).
Without it, the scripts do not crash: `config.get` degrades to the built-in default with a
one-line stderr warning, so a stdlib-only machine runs on the defaults. A project that ships a
`.config.yaml` should install PyYAML so its declared conventions are actually applied.

---

## Coverage Targets

Control test coverage thresholds used in TSD, status dashboard, and test specs.

| Setting | Default | Used In | Notes |
| --- | --- | --- | --- |
| `unit` | 90 | TSD, status, test-spec | Core business logic coverage |
| `integration` | 85 | TSD | API and database interaction coverage |
| `e2e` | 100 | TSD, e2e-guidelines | Feature file coverage target |

### When to Adjust

- **Lower for legacy code**: Brownfield projects may need 70-80% initially
- **Higher for critical systems**: Financial/medical may require 95%+
- **Lower for prototypes**: Experimental code may use 60%

---

## Story Quality Gates

Control minimum requirements for story readiness.

### Edge Cases

| Setting | Default | Used In |
| --- | --- | --- |
| `edge_cases.api` | 8 | story template, reference-story |
| `edge_cases.other` | 5 | reference-story, reference-decisions |

**API stories require more edge cases** because they handle:

- Input validation
- Authentication/authorisation
- Rate limiting
- Concurrent access
- Network failures

### Test Scenarios

| Setting | Default | Used In |
| --- | --- | --- |
| `test_scenarios.api` | 10 | story template |
| `test_scenarios.ui` | 8 | reference-story |

### Story Sizing

| Setting | Default | Meaning |
| --- | --- | --- |
| `max_ac` | 10 | Story too large if > 10 AC |
| `max_points` | 13 | Story too large if > 13 points |
| `recommended_ac.min` | 3 | Suggest more AC if < 3 |
| `recommended_ac.max` | 5 | Optimal upper bound |

---

## Engagement Floor {#engagement-floor}

Default-on (NOT advisory): governs when the planning pass may be skipped.

| Setting | Default | Used In |
| --- | --- | --- |
| `engagement_floor` | `floor` | reference-doctrine rule 16, agent-instructions, `engagement_floor.py` |

`floor` (default): a multi-file change in a spec-bearing repo REQUIRES the planning
pass - a spec delta naming each interacting requirement plus one acceptance criterion
per interaction - before any code. This is the measured rule from the skill's 2026-07
benchmark rerun (judgement-gated engagement matched no-process on base models; the
mandated pass cut escapes 4-5x for ~10-20% more tokens). `judgement`: the operator
accepts that risk and restores pure scale-to-size judgement everywhere.

**Mechanically enforced** by the blocking `engagement-floor` gate lane (`engagement_floor.py`, see reference-scripts-verify): a shipped unit skips the planning pass only by planning (AC / `Verify:` / linked plan) or DECLARING a real single-file `Affects` path (prose like `n/a` does not count); a multi-file unit with no plan fails `unplanned`, one that neither plans nor declares fails `undeclared`. The guarantee is precise: pure omission is caught, and understatement is cross-checked by git in a solo-id commit. Understatement in a commit shared with another judged id was a disclosed limit, now closable with a `Refs: <id>` commit trailer: the git leg attributes a commit's files to each id its `Refs:` trailer names, so a shared commit becomes per-id attributable (a bare co-named subject is still skipped). See reference-scripts-verify for the trailer grammar. Two config shapes so mode and cutoff never collide - scalar `engagement_floor: judgement` opts out everywhere (lane reports, never blocks), or a mapping with `adopt_after:` (forward-only id cutoff; above the highest existing id is refused as a silent disarm) and optional `mode:`. `decisions.py waive --subject rule:engagement-floor[:<id>]` waives the project or one unit.

**Opt-in commit-msg nudge.** A tracked `.githooks/commit-msg` hook warns when a commit subject names more than one work-item id without a `Refs:` trailer disambiguating them - the nudge to add one so the floor can attribute the shared commit per id. It is opt-in and never forced on a consuming project: this repo enables it with `bash tools/enable-hooks.sh` (it also carries the pre-commit gate); a consuming project opts in per project by pointing its own commit-msg hook at `engagement_floor.py check-commit-msg`. It warns by default and does not block; export `SDLC_ENGAGEMENT_STRICT=1` to make it block instead. It degrades honestly - with no git, no script, or an unparseable message it exits without blocking.

---

## TDD Trigger

Control when TDD mode is recommended over Test-After.

| Setting | Default | Used In |
| --- | --- | --- |
| `edge_case_threshold` | 5 | reference-decisions, help/code |

**Rationale**: Stories with many edge cases benefit from TDD because:

- Tests clarify expected behaviour before implementation
- Edge cases are harder to retrofit
- TDD prevents "happy path only" implementations

---

## E2E Limits

Control when to split E2E spec files.

| Setting | Default | Used In |
| --- | --- | --- |
| `max_tests_per_spec` | 50 | reference-test-e2e-guidelines |

**Why 50?** Larger spec files:

- Take longer to run
- Are harder to parallelise
- Make failures harder to isolate

---

## Epic Perspectives

Available perspectives for epic breakdown.

```text
epic:
  perspectives:
    - engineering   # TRD-aligned (components, APIs, data)
    - product       # PRD-aligned (value, metrics, stakeholders)
    - test          # TSD-aligned (coverage, risk, automation)
```

Used by `/sdlc-studio epic --perspective {name}`.

---

## Review Configuration

Severity levels for review findings.

```text
review:
  severity_levels:
    - critical      # Must address before merge
    - important     # Should address
    - suggestion    # Consider addressing
```

---

## Persona Staleness {#personas-staleness-days}

The Persona Review pass of `/sdlc-studio review` uses this window to decide whether a persona is "stale" (no consult / story / CR reference within the window).

| Setting | Default | Notes |
| --- | --- | --- |
| `staleness_days` | 90 | Days without a touch before a persona is flagged stale |

A project where personas are consulted rarely by design (e.g. stable archetypes) can extend this; a project where personas are expected to be high-touch can shorten it. See `reference-review.md` for the cross-doc check that reads this value.

---

## Lessons Validity {#lessons-validity}

How long a project lesson holds before it must be re-validated.

| Setting | Default | Notes |
| --- | --- | --- |
| `lessons.validity_days` | 90 | Days from `Added:` to the `Review-by:` horizon stamped by `lessons add` |

At the sprint close, `gate --require-retro` (or `--require-lessons`) **fails** while an open lesson sits past its horizon: it is either closed (`lessons revalidate --close`, no longer true) or extended (`--extend`, still true). A lesson carrying no horizon at all fails the same lane - unprovable is not proven - and `revalidate --stamp` backfills one. Shorten the window on a fast-moving codebase where lessons rot quickly; lengthen it in a stable domain. See `reference-agentic-lessons.md#close-loop`.

```text
# sdlc-studio/.config.yaml
lessons:
  validity_days: 30
```

---

## Run Appetite {#appetite}

The unattended-run circuit breaker: how much a run may spend before it stops cleanly.

| Setting | Default | Notes |
| --- | --- | --- |
| `appetite.minutes` | 0 | Wall-clock ceiling in minutes; 0 = unbounded |
| `appetite.units` | 0 | Unit-count ceiling; 0 = unbounded |

The breaker (`loop_guard budget`) is evaluated at unit boundaries and stops the run cleanly when the appetite is spent - a distinct exit code from a per-unit quarantine, with units left in their true status. `sprint plan --write --appetite-minutes N --appetite-units N` overrides these defaults per run (e.g. `appetite: {minutes: 180, units: 8}`). Both axes are deterministic (wall-clock from the run start, units from those now terminal); tokens are a forecast only, never a gate. The appetite is never auto-extended - a fresh run resets it. See `reference-sprint.md#appetite`.

---

## Skill Source Repo {#skill-source-repo}

Where a **promoted** lesson (`lessons add --global`) is written.

| Setting | Default | Notes |
| --- | --- | --- |
| `skill_source_repo` | unset | Path to the sdlc-studio source checkout that `add --global` writes into |

An installed or vendored skill copy is a deployment artefact: an update replaces the whole folder, so a lesson authored inside it is destroyed and nothing warns you. `lessons add --global` therefore writes only where git actually holds the file - inside a work tree, not gitignored, and with the lessons registry (`_index.md`) version-controlled - and refuses otherwise (non-zero exit, naming the reason and the remedy) instead of reporting a success it did not achieve. Work-tree membership alone is not enough: a vendored `.claude/skills/` copy is inside the consuming project's work tree and is normally gitignored.

```text
# sdlc-studio/.config.yaml
skill_source_repo: ~/code/sdlc-studio
```

With the key set, a promoted lesson lands in `<skill_source_repo>/.claude/skills/sdlc-studio/lessons/`, `git status` in that repo shows it, and committing it ships the lesson with the next skill release. Unset, promotion is refused and the project tier (`sdlc-studio/.local/lessons.md`, the default, no config needed) still works. See `reference-agentic-lessons.md#lessons-accumulation`.

---

## Contract Tables {#contract-tables}

The structured tables in PRD and TRD that **are** the feature contract. The default anchors (`§3 Feature Inventory`, `§6 Data Models`) match the v2 PRD/TRD templates.

```text
contract_tables:
  prd: "§3 Feature Inventory"
  trd: "§6 Data Models"
```

Override per-project if the project's PRD/TRD use different section anchors. Strings are matched literally against the document's section headings. Setting either to `null` disables the cross-check for that document.

The `code implement` workflow uses these anchors for the **ship-time contract sync** check: when a commit touches files that imply a feature surface change (anything matching `contract_table_paths`, derived per language) but does not touch the named anchors, the workflow warns. See `reference-code.md#ship-time-contract-sync`.

---

## Release Strategy {#release-strategy}

Determines which ship-time guidance the workflow emits.

```text
release_strategy: pr-required    # solo-dev | pr-required | staged-rollout
```

| Value | Ship guidance | When appropriate |
| --- | --- | --- |
| `solo-dev` | Direct commit to `main`, or branch + `git merge --ff-only main` + `git push`. **No PR.** | Single-developer projects (operator + AI assistant). The PR ceremony is friction; reviews happen via Three Amigos consult + verify + check. |
| `pr-required` | `gh pr create` + review + merge. **Default.** | Team projects where PR review is the change gate. |
| `staged-rollout` | Tag + deploy + soak window + promote. The "live" verification depth requires a stable soak before a feature can be marked Done. | Production systems with multi-environment deploys. |

`/sdlc-studio code implement` and `/sdlc-studio epic implement` branch their final-step ship guidance on this value. See `reference-code.md#release-strategy-branch` and `reference-decisions.md#release-strategy-decision`.

---

## Deploy Contract {#deploy}

The orchestrate-only deploy last-mile. The skill **gates** before and **verifies** after a
deploy; it never holds the production trigger, never auto-rolls-back, and never deploys inside the
autonomous loop. Secrets are never read - only the command you configure is invoked, and only on an
explicit, interactive `/sdlc-studio deploy`. All keys are optional; with none set, `deploy` is a pure
gate + verification harness around a deploy you trigger yourself.

```text
deploy:
  command: ""        # (optional) project's own deploy command; invoked only after a green gate and
                     #  only on an interactive deploy - never in sprint
  smoke: ""          # post-deploy check (a verify_ac expression). Smoke green == "rolled out"
  soak_minutes: 0    # soak window before a deploy is "verified" (Done). Smoke alone is not enough
  rollback: ""       # a documented PROCEDURE; the agent never fires it - deploy SURFACES it on a fail
```

| Key | Meaning | Default |
| --- | --- | --- |
| `deploy.command` | The project's own deploy command (any ecosystem). Invoked only after the pre-deploy gate is green, and only on an interactive `deploy` - never by sprint. Leave empty to keep the skill gate-and-verify only. | `""` |
| `deploy.smoke` | Post-deploy smoke check, a `verify_ac` expression (e.g. `http GET /health -- .status == "ok"`). Smoke green marks the deploy **rolled out**. | `""` |
| `deploy.soak_minutes` | Minutes a rolled-out deploy must soak before it is **verified** (Done). Smoke alone never means verified. | `0` |
| `deploy.rollback` | A documented rollback **procedure** (steps, or a command an operator runs by hand). The agent never executes it; `deploy` surfaces it on a failed smoke. | `""` |

See `reference-deploy.md` for the workflow and `reference-deploy-readiness.md` for the verification
patterns (cold-spawn, smoke budget, soak).

---

## Model-Tier Routing {#routing}

Difficulty-aware model-tier routing. **Advisory and opt-in** - no gate ever reads
a tier, and the skill never calls a model API: model ids are opaque strings the orchestrating
agent passes to its own worker-spawn mechanism, so the feature is tool-neutral across agent
CLIs. With `enabled: false` (the default) the sprint plan still carries each unit's
difficulty band; `tier` and `model` appear only when enabled.

```text
routing:
  enabled: false
  models: {}              # e.g. {tiny: claude-haiku-4-5, medium: claude-sonnet-5, xlarge: claude-fable-5}
  floor: {bug: small, security: medium}
  critic_tier: match      # match | above
  thresholds: {tiny: 20, small: 40, medium: 60, large: 80}
  escalation: {max_same_tier: 2}
```

| Key | Meaning | Default |
| --- | --- | --- |
| `routing.enabled` | Emit `tier`/`model` recommendations in the sprint plan. | `false` |
| `routing.models` | Sparse map of abstract tiers (`tiny/small/medium/large/xlarge`) to the project's own model identifiers. An undeclared tier degrades **upward** to the nearest declared larger tier - never downward; above the largest declared, the largest is used. | `{}` |
| `routing.floor` | Minimum tier per unit kind: bands below are lifted. `security` applies when the churn-weighted risk band is high. | `{bug: small, security: medium}` |
| `routing.critic_tier` | The independent critic's tier relative to the author: `match` (same, code units floored at medium) or `above` (one step up). The critic is never a smaller tier than the author; independence (reviewer != author) stays the enforced floor either way. | `match` |
| `routing.thresholds` | Difficulty-score cutpoints - each value is the score at which the next band starts. | `{tiny: 20, small: 40, medium: 60, large: 80}` |
| `routing.escalation.max_same_tier` | Failed attempts at the assigned tier before escalating one declared tier (within loop_guard's unchanged total attempt cap). | `2` |

The difficulty score is deterministic (`scripts/route.py estimate`): blast-radius cognitive
complexity + churn-weighted risk (`complexity.assess`), file scope, unresolved-path novelty,
AC count and story points. A signal that does not resolve defaults its subscore to 0.5 (never
0 - unknown difficulty is never minimal) and lowers confidence; low confidence bumps the
picked tier up one step. See `reference-sprint.md#model-tier-routing` for the policy.

## Plan-Review Gate {#plan-review}

Schema v3 only (dormant under `schema_version: 2`). Before a story with spec-derived ACs is
implemented, an independent reviewer must challenge its ACs against the source spec
(`scripts/plan_review.py`, wired into `transition.py` at entry to In Progress, Review, or Done
so a direct Ready->Done close cannot skip it). The trigger is **deterministic** - no model
judgement in the fire/skip decision (TRD ADR-006) - so it cannot be skipped under effort
pressure. A skip is possible only via a recorded `> **Plan-Review-Override:**` field on the
story (auditable).

| Key | Purpose | Default |
| --- | --- | --- |
| `plan_review.affects_files_threshold` | A story touching at least this many files trips the gate. | `5` |
| `plan_review.min_difficulty` | Routed band at/above this trips the gate (`trivial<low<medium<high<extreme`). | `medium` |
| `plan_review.spec_globs` | A story whose Affects/ACs cite a path matching one of these globs is spec-derived (a document reference, not the word "spec"). Kept in step with `review.spec_paths` so both spec-protection features draw one boundary. | `[*prd*.md, *trd*.md, *tsd*.md, *requirements*, *spec*.md, specs/*, spec/*, requirements/*]` |

The gate fires when **any** signal is true. Record the verdict with `plan_review.py record
--id US.. --verdict approve --reviewer <seat> --author <plan-author>`: it writes to the
plan-review log (so it never satisfies the delivery critique gate), must be independent
(reviewer != plan author), and **pins the reviewed ACs by fingerprint** - a later edit to the
ACs invalidates the approval, so a benign plan cannot be approved then quietly inverted. The
bare `critic.py record --phase plan-review` form also records a verdict but does not pin the
ACs (back-compatible, unprotected) - prefer `plan_review.py record`.

## Spec-Edit Guard {#spec-guard}

Schema v3 only (dormant under `schema_version: 2`). A delivery must not silently falsify the
source of truth: in the N=5 benchmark a worker edited the requirements spec to match its wrong
implementation and the change passed review because nothing distinguished a requested spec edit
from an unrequested one. `scripts/spec_guard.py check --changed <files> --story
<file>` surfaces, deterministically and **per edited file**, which changed files are
requirements/spec documents and which of them the story never references. An edited spec file
the story does not name is `untraced` - the critic charter turns that into a **blocking
finding**. An edited spec file the story *does* name is reported separately: a reference is not
proof the CHANGE was requested (a `Verify: grep` line references a spec without asking to edit
it), so the critic must still confirm those. Matching is per-file so an untraced edit to one
spec cannot ride on a mention of another.

| Key | Purpose | Default |
| --- | --- | --- |
| `review.spec_paths` | Globs identifying requirements/spec documents whose unrequested semantic edit is a blocking finding. Matched against each changed file's full path and basename. | `[*prd*.md, *trd*.md, *tsd*.md, *spec*.md, *requirements*, */specs/*, specs/*, */spec/*, spec/*]` |

The pre-check only guarantees the edit is surfaced (TRD ADR-006); the traceability judgement -
was this edit actually requested by the ticket/story? - stays with the critic.

---

## Using Config in Templates

Templates can reference config values using `{{config.path.to.value}}` syntax:

```markdown
| Level | Target | Rationale |
|-------|--------|-----------|
| Unit | {{config.coverage.unit}}% | Core business logic |
| Integration | {{config.coverage.integration}}% | API interactions |
```

---

## Example Project Config

```text
# sdlc-studio/.config.yaml
# Legacy Python project with relaxed targets

coverage:
  unit: 75
  integration: 70

# quality.done_requires_verified (default true): when true a story cannot transition
# to Done while its executable ACs are red/never-run (the Done-gate blocks); set false to
# downgrade the gate to advisory-warn for the whole project (per-call --force always overrides).
quality:
  done_requires_verified: true
  # epic_requires_test_spec (default true): an epic must have a test-spec (linked by its
  # Epic: field) whose AC Coverage Matrix passes `verify_ac epic-ts`. Single-story work is exempt.
  epic_requires_test_spec: true
  # depth_parity_gate (default false): the story->Done depth-parity check (an AC's declared
  # `Verification target` above `functional` must not out-run the recorded depth) is advisory
  # by default; true upgrades it to a refusal. The BUG depth tiers (Fixed needs functional+,
  # production-affecting Closed needs soak) are always enforced by `transition.py` - --force
  # overrides per call.
  depth_parity_gate: false
  # mutation_max (default 25): the mutation-check gate's cost ceiling per run
  # (scripts/mutation.py); enumerations beyond it are counted as truncated -
  # un-checked coverage, never silently clean.
  mutation_max: 25
  # require_full_sections (default false): the template-tier gate refuses a story or epic that
  # reaches In Progress/Review/Done while missing the sections the full template carries. By
  # default it judges only artefacts that declare a tier (`> **Template:**`) - an unstamped bare
  # story is structurally identical to the pre-tier stories that reach Done today, so refusing
  # it would refuse them. Set true to drop the stamp from the decision entirely and judge EVERY
  # story and epic on its sections: the same rule applied universally, and the close for a
  # project that does not want a hand-removed stamp to be worth anything. `conformance.py`'s
  # `promoted` stage follows the same setting. Remedy either way: `artifact.py promote`.
  require_full_sections: false

story_quality:
  edge_cases:
    api: 6
  sizing:
    max_points: 8     # Prefer smaller stories

tdd:
  edge_case_threshold: 3  # TDD for most stories
```

---

## Conventions (tolerant convention layer)

Declare your house conventions once under `conventions:` and every adopting
check (reconcile's status column, artifact scaffolding, and other consumers of
`lib/conventions.py`) reads them from the one place. Every key defaults to the
historical behaviour, so an unconfigured project changes nothing. A
wrong-shaped value fails loud naming the offending key - the layer never
guesses.

```text
conventions:
  # Extra index header names accepted as the status column (exact cell
  # match, case-insensitive). Without this only 'Status' pins the column,
  # and reconcile diagnoses a mis-named header instead of parsing it.
  status_column:
    - Effective Status
  # Stem suffixes marking a file as a companion doc filed under an
  # artifact's id (EP0244-...-decisions.md). Default: [consultations].
  companion_suffixes:
    - consultations
    - decisions
  # Heading vocabularies the bug-readiness audit accepts. A plain string
  # is one accepted heading (word-order-insensitive: 'Fix (proposed)'
  # equals 'Proposed Fix'); a nested list is a combo - all must be present.
  bug_ready_sections:
    repro:
      - Steps to Reproduce
      - [Symptom, Root cause]
    fix:
      - Proposed Fix
  # Scaffold templates per artifact type (repo-root-relative). `new`/`batch`
  # graft the declared body onto the deterministic provenance head; a
  # declared-but-missing path is an error, never a silent fallback.
  templates:
    bug: sdlc-studio/templates/bug.md
```

---

## Version File

The `.version` file tracks schema version for upgrades:

```text
# sdlc-studio/.version
schema_version: 2
upgraded_from: 1          # null for new projects
upgraded_at: 2026-01-27T10:30:00Z
skill_version: "1.3.0"
created_at: 2026-01-15T09:00:00Z
```

| Field | Purpose |
| --- | --- |
| `schema_version` | Current template schema (1=legacy, 2=modular, 3=distributed identity + triage) |
| `upgraded_from` | Previous version (for migration tracking) |
| `upgraded_at` | When upgrade was performed |
| `skill_version` | SDLC Studio version |
| `created_at` | When project was initialised |

### Schema v3 triage lane {#triage-vocab}

Under `schema_version: 3`, findings (bug/cr/rfc) gain an `inbox` triage lane prepended to
their status vocabulary. A freshly filed finding lands in `inbox`; a `triaged` transition then
promotes it into the workflow proper, and a *different* seat must perform it (separation of
duties). The triaged target is type-specific - a finding skips the human proposal state it never
occupied:

| Type | Files into | Triages into |
| --- | --- | --- |
| bug | `inbox` | `Open` |
| cr | `inbox` | `Approved` |
| rfc | `inbox` | `In Review` |

`transition --id <ID> --status <target> --triaged-by "Name; type; version"` gates the transition:
it requires a structured `triaged_by` (type is `human`/`persona`/`agent`) and refuses loudly
without one, and rejects a triager who is the raiser (a solo human self-triage warns instead, so a
lone operator never deadlocks). `--triage-severity` records the triager's severity alongside the
raiser's for later triage-quality metrics. All of this is dormant under `schema_version: 2`;
stories and epics are authored, not triaged, so they are unaffected.

**Noise controls** (`triage:` config block) keep a flood of agent-filed findings from burying
the few that matter:

| Key | Default | Effect |
| --- | --- | --- |
| `triage.session_cap` | `20` | Max findings one session may file; the N+1th is refused loudly. A session is keyed by the `SDLC_TRIAGE_SESSION` environment variable (set a new value to start a fresh budget); the count lives in `.local/triage-session.json`. |
| `triage.low_consolidation` | `true` | A Low-severity finding folds into a themed consolidation CR (one per theme) rather than minting its own artefact; Medium and above always get individual artefacts. |
| `triage.sample_rate` | `0.20` | Fraction of the non-always-sampled triaged findings a human audits. |
| `triage.always_sample` | `[Critical, disagreement]` | Always audited: every Critical-severity finding, and every raiser/triager severity disagreement. |

Both the finding filer and `artifact new` enforce the noise controls, so neither creation path is
a bypass. The sampling policy and its triage-quality metrics (false-positive rate, severity
inflation) live in `triage_sampling.py`, surfaced by `status triage-metrics`.

---

## Pipeline Profile {#profile}

`profile` selects how much of the pipeline a project runs.

| Value | Pipeline | Use when |
| --- | --- | --- |
| `full` (default) | PRD -> TRD -> TSD -> personas -> epics -> stories -> implement | Any project that benefits from the full layer set |
| `lite` | PRD -> story -> implement | A small repo where the ceremony would outweigh the source |

```text
# sdlc-studio/.config.yaml
profile: lite
```

Under `lite`, a story is created without an epic, `status`/`hint` never nag about a
missing TRD/TSD/persona/epic, and executable-AC verification and reconcile behave
identically. Promote to `full` when the project outgrows it with
`scripts/lite_profile.py promote`, which inserts one umbrella epic above the existing
stories, wires them to it, and flips the profile. An unrecognised value degrades to
`full` - the profile only ever relaxes discipline when explicitly asked.

---

## Project Implementation

Control behaviour of `/sdlc-studio project implement`.

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `commit_strategy` | enum | `per-epic` | When to auto-commit: after each wave, each epic, or at project end |
| `review_interval` | int | `3` | Run `review --quick` after this many epics |
| `auto_reconcile` | bool | `true` | Automatically reconcile after each epic completes |
| `auto_commit` | bool | `true` | Automatically commit at strategy boundaries |

---

## See Also

- `templates/config-defaults.yaml` - Default values
- `help/init.md` - Project initialisation
- `reference-upgrade.md` - Upgrading between versions
- `reference-project.md` - Project-level orchestration
