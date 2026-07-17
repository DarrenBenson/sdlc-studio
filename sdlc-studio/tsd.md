# Test Strategy Document

> **Project:** SDLC Studio
> **Version:** 4.1.0
> **Last Updated:** 2026-07-14
> **Status:** Generated (brownfield - awaiting validation)
>
> Generated in **Generate mode** by reverse-engineering the skill's own test
> setup (`package.json` scripts, `.claude/skills/sdlc-studio/scripts/tests/`,
> `tools/`, `.markdownlint.json`, `scripts/gate.py`, `scripts/mutation.py`). Per
> `reference-philosophy.md`, generated specs are not Done until their tests pass
> against the implementation; the inferred claims here await that validation.
> Confidence markers and status values are defined at the foot of the document.
> Consistent with PRD section 5 (Non-Functional Requirements) and section 10
> (Quality Assessment), and with the TRD component and script inventory.
>
> **Coverage:** v4.1.0 as released, plus the `[Unreleased]` work on `main`. The
> document version tracks the product version; it is not itself a release artefact.

---

## Overview

SDLC Studio is a coding-agent skill: a body of markdown instruction files plus a
deterministic Python helper layer. It ships no server, UI, or database, so the test
strategy targets two surfaces only - the Python script tier and the markdown corpus.
The script tier is exercised by an executable `unittest` suite; the markdown corpus
is held to its house style and structural invariants by static checkers run under
`npm run lint`. There is no application runtime to drive, so there are no end-to-end
or browser tests, and none are planned. [HIGH]

The binding quality constraint is not latency or throughput but determinism and
context economy: scripts must behave the same way every run, and the always-loaded
footprint must stay within budget.

A third axis arrived with v4 and it is the one this document most needed to learn:
**a passing test is not evidence that a test can fail.** `verify_ac` proves an
acceptance criterion's tests pass; `mutation.py` proves they would fail if the code
broke. The two are complementary and neither substitutes for the other. Every gate
this project ships is now held to the same rule it applies to a consuming project's
tests - assert on content, degrade honestly, and never let an absent report read as
a pass.

## Test Objectives

- Prove every Python helper behaves deterministically across the artifact forms
  it must tolerate (sequential and ULID ids, dashed and undashed, optional
  blockquote metadata, mixed case, decorated status lines).
- Guarantee the read path stays read-only over the workspace, and that every write
  is bounded, tested and atomic for shared files (TRD section 5, contract rule 5).
- Prove the tests can FAIL: the mutation gate applies a bounded fault set to a
  surface and reports killed against survived, so a green suite over dead code is
  visible rather than reassuring.
- Hold the markdown corpus to its house style (British English, no em dashes, no
  banned jargon, no private project names) and structural invariants (resolvable
  links, valid frontmatter, line budgets, version consistency) on every commit.
- Keep the release gate honest: `gate.py --release` EXECUTES every story's `Verify:`
  expression rather than reading a report that could carry a stale green, and refuses
  to print a release verdict over an unexamined AC layer.
- Make the markdown-behaviour test gap explicit rather than implicit, so a future
  test backlog can close it.

## Scope

### In Scope

- Unit tests for the 58 scripts and the six-module `lib/` (the script tier).
- Static and lint checks over all markdown (house style, links, frontmatter, line
  budgets, version consistency, neutrality, action pins).
- Integration-style tests that run scripts against fixture workspaces in temporary
  directories, including a create-then-validate round trip across every creator,
  artefact type and schema era.
- Mutation checking of the script tier (assertion integrity).
- The eval scenarios (`tools/eval_run.py`): a fixture project built from a
  machine-readable spec, driven through a flow, with a per-behaviour verdict recorded
  and a gate failure on any blocking behaviour left ungraded.
- The gate (`gate.py`), including the release gate, as the quality gate of record.

### Out of Scope

- Executable behaviour tests for the markdown command flows in `reference-*.md`.
  This is the acknowledged gap (PRD section 10 Untested Areas); it is stated
  honestly below rather than papered over.
- End-to-end, browser, UI, or load tests - there is no running application or
  service to drive.
- The consuming project's own test suite. Each project that installs the skill
  supplies the Verify-line tools (`pytest`, `jest`, `go`, `curl`, and so on) its
  acceptance criteria reference; those run under that project's TSD, not this one.
- GitHub network behaviour. `github_sync.py` is tested with `gh` mocked; live
  GitHub calls are not part of the suite.

---

## Test Strategy and Philosophy

The skill splits into two tiers (TRD section 3), and each tier gets the test
approach that fits it.

**Script tier - test-driven, executable.** The deterministic Python helpers are
the part of the system that can be tested as code, so they are. Every script has a
matching `test_<script>.py` under `scripts/tests/`, and the contract (TRD section 5,
rule 8) mandates this. New script behaviour is expected to land with its tests; the
release gate refuses to tag until the suite is green.

**Markdown tier - validated by linters, the script suite, the gates, and the eval
scenarios, not by executable behaviour tests.** The markdown command flows describe
what the agent should do; they have no executable harness that asserts the agent did
it in the general case. This is an honest gap [HIGH]. Four things stand in for
behaviour tests today:

1. Static checkers (`tools/`) enforce house style, link integrity, frontmatter
   validity, line budgets, version consistency, neutrality, and pinned CI actions
   across the corpus.
2. The script suite tests the deterministic helpers the flows invoke, so the
   computational spine of each flow is covered even though the prose is not.
3. `reconcile`, `validate` and the `gate` lanes catch structural, status and
   conformance drift in the artifacts a flow produces, and `validate.py instructions`
   enforces instruction-file hygiene.
4. The **eval scenarios** (`tools/eval_run.py`) drive a synthesised fixture project
   through a flow and record a per-behaviour verdict, failing the gate on any blocking
   behaviour that failed or was left ungraded. This is the closest thing to a
   conformance test the markdown tier has; it covers named surfaces (schema-v3
   identity, the independence gate, team generation on an ambiguous-by-design fixture,
   persona arbitration), not the whole corpus.

That is the current oracle for markdown behaviour. It is weaker than executable
conformance tests over every flow, and PRD section 11 and TRD Open Question 12.1 both
flag closing it as the main outstanding test investment.

**Executable verifiers are a STORY-only surface.** Only a story carries a
`- **Verify:**` line, and only a story's Done is gated on one passing. A CR or bug
acceptance criterion is prose - the creators refuse a command-shaped `Verify:` in one
at creation, because nothing executes it: a wrong one is a permanent false RED that
nobody ever sees fail, and a loose one is a false GREEN. This is why the pipeline
pushes a Large or wide-footprint CR to be decomposed into stories: an un-decomposed CR
reaches Done on prose alone, and prose is not an oracle.

**Generate-mode validation requirement.** Per `reference-philosophy.md`, a spec
extracted in Generate mode (this TSD, the TRD, the PRD) is not Done until its tests
pass against the implementation. For the script tier that bar is met: the script
suite passes (run `python3 -m unittest discover` for the live count; do not pin a
number here - it drifts). For the markdown tier it is not met, because no behaviour
tests exist; the generated claims about markdown flow behaviour remain inferred
until that suite is written. This document records that state rather than
overstating coverage.

> **Run the static-checker gate before every commit, not only before a tag.** Every
> guard except markdownlint is npm-independent Python/bash (AGENTS.md "Testing the
> Skill" lists the direct commands). A 2026-07-04 retrospective found a session break
> the gate four ways by not running it locally - the checks catch style, neutrality,
> line-budget, and version breakage that the unit tests never see. That is now
> un-skippable rather than remembered: `tools/enable-hooks.sh` installs a pre-commit
> hook that runs the whole gate and blocks a breaking commit, printing for each
> failure what the guard enforces, the offending line, and how to fix it. The
> assertion-integrity discipline
> (`reference-test-best-practices.md#assertion-integrity`) asks "would this test fail
> if the feature broke?" - and it is now executably enforced by the mutation gate
> below, rather than being a rule that holds when the author remembers it.

---

## Test Levels

### Coverage Targets

| Level | Target | Rationale |
| --- | --- | --- |
| Unit (scripts) | ~90% statement coverage | Core deterministic logic; the part that can and must be tested as code. [MEDIUM] |
| Static / lint (markdown) | 100% of `*.md` pass all checkers | House style and structural invariants are binary - any violation fails the gate. [HIGH] |
| Integration (scripts vs fixtures) | Every script with side effects has at least one fixture-workspace test; write-confinement asserted by a snapshot before/after; a create-then-validate round trip covers every creator, artefact type and schema era | Confirms the write boundary, and that content supplied to a creator actually reaches the artefact. [HIGH] |
| Mutation (assertion integrity) | Survived mutants are findings, triaged; an un-mutatable surface is reported un-checked, never passed | A passing suite over dead code is the failure this level exists to expose. Advisory lane, not yet blocking. [HIGH] |
| Eval scenarios (flow conformance) | Every blocking behaviour in every scenario graded; an ungraded blocking behaviour fails the gate - `report` enumerates the scenarios on disk, so a scenario nobody touched fails rather than vanishing | The nearest thing the markdown tier has to a behaviour test. Covers named surfaces, not the whole corpus. [HIGH] |
| End-to-end | Not applicable | No running application or service to drive. [HIGH] |

> The ~90% unit target is a goal, not a presently measured figure. Coverage is not
> currently wired into CI; see Coverage Measurement below. [MEDIUM]

### Unit Testing

| Attribute | Value |
| --- | --- |
| Coverage Target | ~90% statement (goal) [MEDIUM] |
| Framework | Python `unittest` (stdlib) |
| Execution | `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests` (shipped scripts) and `-s tools/tests` (repo-only checkers); `npm test` runs both |
| Suite size | 2151 tests across 76 modules at the time of writing, under a minute. Run the discover command for the live count rather than trusting a pinned number - it drifts every sprint |
| Location | `.claude/skills/sdlc-studio/scripts/tests/test_<script>.py`; `tools/tests/` for the repo-only checkers |

The suite operates on small temporary fixture trees, which is what keeps a
2000-plus-test run cheap enough to sit in a pre-commit hook.

**A passing suite is silent.** Tests that feed a validator a deliberately-broken
fixture capture and assert on its diagnostics rather than letting them escape to the
console. This is not cosmetic: a green run that prints `ERROR` lines trains every
reader, human and agent, to skim past `ERROR`, which is the exact reflex that lets a
real one through. A `test-noise` gate leg keeps it that way.

#### Unit coverage map

Most scripts and shared-library modules have a dedicated `test_<name>.py`; the script
contract (TRD section 5, rule 8) mandates one as a convention. It is a convention held in
review, not an automated build gate: no sweep enumerates the scripts and fails a build on
a module that arrives without a test. A handful are exercised indirectly under a
differently-named module rather than a dedicated one - `refine` and `triage` under the
triage suites, `lib/run_state` under the loop-guard, handoff and sprint-report suites, and
`lib/tiers` under the planning-tier and routing suites - and `autosprint` and `lib/xrepo`
currently have no direct test. Rather than pin per-module test counts that are stale within
a sprint, the map below records what each tier is responsible for.

| Tier | Representative modules | What the tests hold |
| --- | --- | --- |
| Parsing core | `lib/sdlc_md.py`, `lib/conventions.py` | Id normalisation across both eras (sequential and ULID, dashed and undashed, mixed case), `extract_field`, `canonical_status` longest-prefix reduction, AC heading and bullet parsing, fenced-block awareness (an example `Verify:` line in a code block is never executed), JSON helpers that never raise, `atomic_write`, `allocation_lock`. |
| Creators | `artifact.py`, `file_finding.py` | Collision-free id + index row + epic wiring by construction; refusal of a line break in any field written into a metadata line or table cell (the class that let a `--title` forge a `Status` line and an `--ac` inject a sibling `Verify:` line); refusal of a command-shaped `Verify:` in a CR or bug AC; a refused create writes nothing and burns no id. |
| Verification | `verify_ac.py`, `mutation.py`, `transition.py` | Per-AC pass/fail/manual/unspecified; in-place `Verified:` rewrite; the Done gate; the verification-depth gate on a terminal bug status; killed / survived / error / unviable verdicts and the STALE-on-edit rule. |
| Drift and census | `reconcile.py`, `status.py`, `validate.py`, `conformance.py` | Disk-census drift kinds and their remediation hints (a check must expose the kinds it can emit, pinned to the real emission sites, so a new kind without a hint fails the build); the four-pillar census; structure and status-vocabulary validation; seat validation. |
| Gates | `gate.py`, `engagement_floor.py`, `retro.py`, `lessons.py` | Lane verdicts and the bound-lane refusals; the floor's file-count and declaration recognisers (one recogniser, so they cannot disagree); retro content validation and finding disposition; lessons ranking, staleness by recomputed digest rather than a stamp. |
| Planning | `sprint.py`, `loop_guard.py`, `telemetry.py` | WSJF order, dependency waves, shared-file clusters, the breakdown refusal, appetite resolution at plan time and read-back by the breaker, the forecast band. |
| Integrations | `github_sync.py`, `repo_map.py`, `plan.py` | `pull`/`push`/`cascade`/`state` with `gh` mocked; the AST indexer; plan-file archive without delete or overwrite. |
| Repo CI checkers (`tools/tests/`) | `check_links`, `validate_skill`, `check_versions`, `check_budgets`, `check_neutrality` | The static-analysis layer has executable coverage too - a checker that misses a real violation is a High defect. |

### Static / Lint Testing (markdown)

This level is the primary guard on the markdown corpus. `npm run lint` chains eight
checkers; any non-zero exit fails the gate. Every one except markdownlint runs as a
plain Python or bash command, so a machine without Node still runs seven of the eight.

| Check | Command | Enforces | Tooling |
| --- | --- | --- | --- |
| Markdown house style | `lint:md` | markdownlint rules per `.markdownlint.json` (MD013 off, MD024 siblings-only, MD033 off, MD041 off, MD036 off, fenced code) | markdownlint-cli |
| Prose style | `lint:style` | No em dash (U+2014); no banned corporate jargon outside `tools/style-allowlist.txt`; no Americanised spelling (a bounded auto-checked list); no internal provenance tags in consuming-facing files | `tools/lint-style.sh` (bash + grep) |
| Link integrity | `lint:links` | Every `path.md#anchor` reference inside the skill subtree resolves to an existing file and anchor; the repo-root docs' markdown links resolve to existing files | `tools/check_links.py` |
| Skill frontmatter | `lint:skill` | `name` 1-64 chars matching the directory and `^[a-z0-9]+(-[a-z0-9]+)*$`; `description` 1-1024 chars; `metadata.version` X.Y.Z semver; no unknown frontmatter fields | `tools/validate_skill.py` |
| Version consistency | `lint:versions` | Version agrees across package.json, `templates/version.yaml`, SKILL.md frontmatter, README.md, and (at release) CHANGELOG.md | `tools/check_versions.py` |
| Line budgets | `lint:budgets` | `SKILL.md` < 500 lines; each `reference-*.md` within its declared ceiling (with a recorded allowlist and a tolerance factor) | `tools/check_budgets.py` |
| Neutrality | `lint:neutrality` | No private consuming-project name in a tracked file | `tools/check_neutrality.py` |
| Action pins | `lint:action-pins` | CI actions pinned, not floating | `tools/check_action_pins.sh` |

`lint:fix` (`markdownlint --fix`) is available for auto-fixable markdown issues but
is not part of the gate.

> **Known gap:** `check_links.py` link-checks the skill subtree (anchored references)
> and the repo-root docs (file existence). The `sdlc-studio/` artifact corpus (this
> document, the PRD, TRD, personas, epics, stories, RFCs, bugs) is not anchor-checked,
> so a broken anchor inside an artefact is not caught by CI. markdownlint still runs
> repo-wide.

### Mutation Testing (assertion integrity)

The level that answers "would this test fail if the feature broke?". `verify_ac`
proves an AC's tests pass; `mutation.py` proves they can fail.

| Attribute | Value |
| --- | --- |
| Scope | A declared, bounded fault set - `invert-guard`, `stub-return-null`, `unset-delivered-field`, `no-op-mapper` - applied to a surface selected by `--files`, `--since <rev>` or `--story` |
| Method | Confirm a green baseline (a red baseline cannot judge - every mutation records `error`, never a fake kill), apply one mutation, re-run the suite, restore the bytes, verdict it |
| Verdicts | **killed** (the test pins the behaviour), **survived** (a finding: the suite stayed green over broken code), **error** (the runner broke; never a kill), **unviable** (a mutant that cannot even parse - evidence of nothing, since any suite fails on it) |
| Output | `.local/mutation-report.json`, carrying the git rev and a content hash per target |
| Gate | An advisory `mutation` lane in `gate.py`. An absent report reads **not-run**, never PASS; a rev change or an edited target reads **STALE**, so a dirty tree cannot ride an old green |
| Honest degrade | A file or construct the language profiles cannot mutate is listed **un-checked**, never passed |

It is advisory rather than blocking because a full mutation run costs one suite
execution per mutant - minutes, not seconds - so it cannot sit on the fast path. That
is a deliberate trade, and the not-run-is-not-a-pass rule is what keeps it from
becoming a green light nobody earned.

### Integration Testing (scripts against fixture workspaces)

The script tests are not pure unit tests in isolation; many build a temporary
`sdlc-studio/` workspace on disk, run the script as it would run in production, and
assert on the files and JSON it produces. The verify run printed during a suite
execution (creating `.local/verify-report.json` in a temp dir, reporting per-AC
pass/fail) is an example of this fixture-workspace pattern. [HIGH]

| Attribute | Value |
| --- | --- |
| Scope | Scripts run end-to-end against a synthesised artifact tree in `tempfile` dirs |
| Framework | Python `unittest` with `tempfile`/`shutil` fixtures; a shared `gitutil` helper neutralises the host git config so a developer's `commit.gpgsign` cannot make the suite fail or hang |
| Key assertions | Correct JSON output; writes bounded to the named target; non-zero exit on halting failures; tolerance of both id eras and legacy artefact forms; a created artefact both validates AND carries the content the caller supplied |
| Execution | Same command and gate as the unit level |

**Reproduce through the public path.** A hazard proven by calling a private helper
directly is a statement about the helper, not about the pipeline - and the pipeline is
the only thing that ships. A High bug was once filed, and had to be withdrawn, on
exactly that mistake: the hazard was real, the exposure was zero, and the guard was
already there at the only call site that mattered. A confident false finding is not
free, because a process that turns findings into work will faithfully manufacture work
from a wrong one. Tests that assert a guard fires must drive it the way a caller does.

### Eval Scenarios (flow conformance)

| Attribute | Value |
| --- | --- |
| Scope | A fixture project built from a machine-readable spec, driven through a named flow |
| Method | `tools/eval_run.py`: build the fixture, run the flow, record a per-behaviour verdict |
| Gate | Fails on any blocking behaviour that failed **or was left ungraded** - a behaviour nobody graded is not a pass. `report` enumerates `evals/scenarios/*.json`, so a scenario with zero recorded verdicts fails on its blocking behaviours rather than being skipped for its absence from the results file |
| Coverage | Named v3/v4 surfaces: schema-v3 identity (ULID allocation, ULID-epic wiring, reconcile coverage), the independence gate (author != reviewer, verified depth on a terminal status), team generation on an ambiguous-by-design fixture, persona arbitration. Not the whole markdown corpus |

### End-to-End Testing

Not applicable. SDLC Studio has no server, UI, or long-running process to drive,
so there is no E2E layer and none is planned (TRD section 13, Won't Have). The
closest analogue - whether the agent executes a markdown flow correctly - is the
untested area described under Test Strategy and Philosophy.

### Performance Testing

Not gated as a runtime metric. The performance budget is context tokens, addressed
structurally by progressive disclosure (always-loaded `SKILL.md` held under 500
lines by `check_budgets.py`), not by a latency assertion. Script runtime is
observed (2151 tests in under a minute) but not asserted against a threshold. See the
quality-gate table for the NFR mapping.

The **token forecast is not a test-strategy instrument and must not be read as one.**
`sprint plan` estimates a batch's token cost, `retro accuracy` compares that against
what telemetry measured, and `retros/VELOCITY.md` records the history. The forecast is
currently falsified out-of-sample (0.55x; the predictor, not the coefficient, is at
fault - see PRD section 10). It warns and never gates, nothing auto-recalibrates from
it, and a unit with no telemetry is reported **UNMEASURED** and excluded from both
sides of the ratio, with every report stating how many of the batch it speaks for.
Silence is not a measurement.

### Security Testing

No dedicated security scanner is wired. The security posture (TRD section 9) is
enforced structurally rather than by a scan: the script contract forbids network
calls except the `gh` wrapper and forbids token handling, the suite mocks `gh`, and
the pure-stdlib constraint removes third-party supply-chain surface. See the
quality-gate table for the NFR mapping and the explicit gaps.

---

## Quality Gates (PRD section 5 NFR mapping)

Every PRD Non-Functional Requirement is mapped to a concrete gate or an explicit
not-gated rationale. This closes the PRD-to-TSD traceability gap.

| NFR (PRD section 5) | Quality gate | Blocking | Confidence |
| --- | --- | --- | --- |
| **Performance** - read path sub-second, writes bounded | Indirect: the suite runs 2151 tests in under a minute; a regression that made scripts slow would be visible. No explicit latency threshold is asserted. Treated as observed, not gated. `mutation` is exempt by design (minutes per run). | No | [MEDIUM] |
| **Performance** - always-loaded context minimal | `check_budgets.py`: `SKILL.md` must be < 500 lines, each `reference-*.md` within its declared ceiling. Hard gate via `lint:budgets`. | Yes | [HIGH] |
| **Security** - no network calls except `gh` and project Verify tools | Enforced by the script contract and the test design: `github_sync.py` tested with `gh` mocked; pure-stdlib (no third-party clients). Not gated by a network-egress scanner. | Partial (by test design, not a scanner) | [HIGH] |
| **Security** - no secrets handled by the skill | Not gated by a secret scanner in this repo. Enforced by design (no token handling; `gh` owns auth) and by code review. N/A as an automated gate. | No (design control) | [MEDIUM] |
| **Scalability** - progressive disclosure keeps always-loaded context constant | `check_budgets.py` line budgets (as above); new commands add a `help/` file and a guide row, not router bulk. | Yes | [HIGH] |
| **Scalability** - agentic waves bound concurrency | Not gated. Concurrency bounds are an instruction-level behaviour in `reference-agentic-lessons.md`; no executable test asserts wave sizing. N/A as an automated gate. | No | [MEDIUM] |
| **Availability** - offline-capable; sync aborts cleanly when `gh`/remotes absent | Offline capability comes from the core pipeline scripts, which make no network calls (verified by the no-network contract and stdlib-only design). `github_sync.py` does not soft no-op: with `gh` absent it aborts with a clear error (exit 127), asserted by `test_github_sync.py`. So the NFR is met for the offline pipeline, but `github_sync` does not degrade gracefully - callers must handle the non-zero exit. | Partial (unit) | [MEDIUM] |

Additional gates that back the NFRs but sit outside the four PRD headings:

| Gate | Criteria | Blocking |
| --- | --- | --- |
| Unit suite | The full unittest suite passes (`npm test` exits 0) | Yes |
| Markdown lint | `npm run lint` exits 0 (all eight sub-checks) | Yes |
| Link integrity | `check_links.py`: every anchor resolves | Yes |
| Skill frontmatter | `validate_skill.py`: valid against Agent Skills standard | Yes |
| Version consistency | `check_versions.py`: all homes agree (CHANGELOG advisory between releases, required at release) | Yes (release) |
| Neutrality | `check_neutrality.py`: no private consuming-project name in a tracked file | Yes |
| Instruction hygiene | `validate.py instructions` passes | Manual (recommended; not yet CI-wired - no npm script or workflow invokes it) |

### The artefact gate (`gate.py`)

Distinct from the lint chain: the lint chain guards the *corpus*, `gate.py` guards the
*workspace and the delivery*. One portable, ecosystem-neutral exit code over the
deterministic checks, read-only and therefore hook-safe.

| Lane | Fails on | Blocking |
| --- | --- | --- |
| `conformance` | A unit that has not reached its declared stage | Yes |
| `reconcile` | Any drift item in the census | Yes |
| `index-derived` | An index edited as though it were authoritative | Yes |
| `validate` | A structural or status-vocabulary error | Yes |
| `integrity`, `duplicate-id` | A corrupt or duplicated id | Yes |
| `doc-coverage` | A shipped command with no help or reference file | Yes |
| `engagement-floor` | A shipped multi-file unit with no planning pass (see PRD section 3) | Yes |
| `doc-freshness` | Stale facts in `LATEST.md` | No (advisory) |
| `constitution`, `provenance`, `disclosure` | Project-rule and stamping findings | Advisory |
| `mutation` | Nothing (report only). An absent report reads not-run; a rev change or edited target reads STALE | Advisory |
| `hook-enabled` | The tracked pre-commit hook not installed | No (advisory) |

Bound lanes attach to a specific obligation and **cannot be skipped or excluded
away** - a deselected bound lane is refused rather than honoured, which closes the
route by which `--skip retro` once silently voided the retro gate:

| Bound lane | Attached to | What it asserts |
| --- | --- | --- |
| `--require-retro RETROxxxx` | Sprint close | The retro's **content** (required sections, at least one real lesson, every finding dispositioned) - not its existence, because a gate that tests for a file is satisfied by `touch`, and this one once was. Implies the lessons half |
| `--require-lessons` | Sprint close | `LESSONS-SUMMARY.md` is the **recomputed** digest of the current lessons log (not a stamp, a count or an mtime - there is nothing to forge), and no open lesson is past its validity horizon |
| `--require-review` | Sprint close | `reviews/LATEST.md` is at least as new as every artefact. Currency, not presence |
| `--require-handoff HOxxxx` | A run that stopped short of its goal | The handoff exists and a retro links it |
| `--require-close` | A push or release close guard | The **close-owed** lane (RFC0042's machine half): no delivery unit that reached a terminal status since the baseline is left with no retro accounting for it - a skipped close-down. An unbaselined project reports zero (stamping the baseline is the operator's one-time acknowledgement of the pre-adoption tail). Blocking |
| `--release` | The pre-tag gate | Binds two lanes. **verify**: EXECUTES every story's `Verify:` expression for real, rather than reading a report that could carry a stale green. Deselecting the verify lane under `--release` is **refused** - no release verdict is printed over an unexamined AC layer. A story with an *unspecified* AC (no `Verify:` line) fails and is named; a story whose ACs are all declared `manual` passes. A story set with no executable verifier at all fails, because a lane with nothing to prove must not read as proof. A verifier blocked by the external-provenance trust boundary reports as **unproven**, never as a red AC. **review-legs** (the BG0110 fix): every required DOCUMENT leg (PRD/TRD/TSD/Persona) must be present or explicitly waived against a recorded decision id, so a tag over a silently-missing required artefact is refused; the CODE leg is out of scope (D0022) and every verdict states that exclusion |

---

## Coverage Measurement

Statement coverage for the script tier is not presently collected in CI; the ~90%
target is a goal inferred from the per-script test density (every script and every
shared-library module has a dedicated test module). [MEDIUM] To measure it, run the
suite under `coverage.py` from the repository root:

```bash
python3 -m coverage run -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
python3 -m coverage report -m --include='.claude/skills/sdlc-studio/scripts/*'
```

Statement coverage is the weaker of the two questions, and it is worth saying which is
which. Coverage asks *was this line executed*; the mutation gate asks *would a test
have noticed if the line were wrong*. A tier can sit at 90% coverage with surviving
mutants, and that combination is the one worth hunting.

Markdown "coverage" is binary rather than percentage-based: the corpus either
passes all eight lint checks or it does not. There is no partial-pass state.

> If async or subprocess code ever shows artificially low coverage, see the
> Coverage Troubleshooting notes in `help/tsd.md` (greenlet/thread concurrency and
> hidden conditional assertions).

---

## Test Data Strategy

### Approach

Tests synthesise their own fixtures: a temporary `sdlc-studio/` workspace built in
a `tempfile` directory, populated with the minimal artifacts a given assertion
needs (a story with ACs, an index table, a malformed file for negative tests).
Fixtures are torn down per test, so the suite leaves no state and can run in any
order. No shared mutable fixture database exists.

### Sensitive Data

None. The skill handles no secrets and the tests touch no real credentials.
`github_sync.py` tests mock the `gh` subprocess, so no live GitHub token is needed
and none is present in the suite.

---

## Automation Strategy

### Automation Candidates

- The entire script tier (already automated as the unittest suite).
- All markdown structural and style invariants (already automated as the eight lint
  checks).
- The artefact and delivery invariants (already automated as the `gate.py` lanes).
- The release gate composition (suite, full lint, `gate.py --release`).

### Manual Testing

- The markdown command flows not covered by an eval scenario. Flow correctness is
  judged by use and by the manual verification steps in `CLAUDE.md` (install the
  skill, run `help`, `status`, `repo map build`, and `reconcile --verify --dry-run`
  against a fixture story).
- Cross-harness install behaviour (`install.sh` / `install.ps1`) beyond the
  Windows pwsh smoke test already in CI.
- Triage of surviving mutants: the tool reports them, a human decides which are real.

### Automation Framework Stack

| Layer | Tool | Language |
| --- | --- | --- |
| Script unit / integration | `unittest` (stdlib) | Python 3.10+ |
| Mutation / assertion integrity | `scripts/mutation.py` | Python 3.10+ |
| Flow conformance | `tools/eval_run.py` | Python 3.10+ |
| Artefact and delivery gate | `scripts/gate.py` | Python 3.10+ |
| Markdown lint | markdownlint-cli | Node |
| Prose style | `lint-style.sh` (grep) | Bash |
| Structural checkers | `check_links`, `validate_skill`, `check_versions`, `check_budgets`, `check_neutrality` | Python 3.10+ |

---

## CI/CD Integration

### Pipeline Stages

1. **Pre-commit (local, and enforced):** `tools/enable-hooks.sh` installs a hook that
   runs the whole gate on every commit and blocks a breaking one, printing for each
   failure what the guard enforces, the offending line, and how to fix it. The gate is
   un-skippable by default rather than something an agent has to remember (emergency
   bypass: `git commit --no-verify`). If Node is absent the hook prints a visible SKIP
   for markdownlint and CI still enforces it - so a markdown-mechanics error can pass a
   Node-less machine and fail on push. `npm install` closes that gap.
2. **PR / push:** the full lint chain plus both unittest suites; a Windows pwsh smoke
   test for `install.ps1`.
3. **Sprint close:** `gate.py --require-retro RETROxxxx --require-review`. Reconcile
   blocks on drift, the retro is checked on its content, and the review anchor must be
   current - a stale `LATEST.md` once sat claiming "ready to tag" long after that
   stopped being true, which is why currency and not presence is the test.
4. **Pre-release tag:** `gate.py --release` - the standard gate plus an executing pass
   over every story's `Verify:` DSL, as ONE exit code. This exists because the previous
   arrangement (two exit codes an operator had to remember to read) let a rotted verify
   layer reach a release candidate: 43 acceptance criteria pointing at renamed test
   files, refactored test names and retired scripts, accumulated silently across months
   of refactors. `check_versions.py` must also agree across every version home including
   CHANGELOG. Running `validate.py instructions` remains a recommended manual check; it
   is not wired into any npm script or workflow.

There is no merge-to-main E2E stage and no nightly performance stage, because no
running application exists to exercise.

### Quality Gates

| Gate | Criteria | Blocking |
| --- | --- | --- |
| Unit suite | full suite passes (`npm test` exits 0) | Yes |
| Markdown lint (`lint:md`) | 0 violations | Yes |
| Prose style (`lint:style`) | No em dash, no un-allowlisted jargon, no Americanised spelling | Yes |
| Link integrity (`lint:links`) | All anchors resolve | Yes |
| Skill frontmatter (`lint:skill`) | Valid | Yes |
| Version consistency (`lint:versions`) | All homes agree | Yes (release) |
| Line budgets (`lint:budgets`) | Within budget | Yes |
| Neutrality (`lint:neutrality`) | No private project name in a tracked file | Yes |
| Artefact gate (`gate.py`) | Every blocking lane PASSes | Yes |
| Release gate (`gate.py --release`) | Every story `Verify:` expression executes green; no unspecified AC; no unexamined AC layer | Yes (release) |

---

## Defect Management

Defects are tracked as SDLC Studio `bug` artifacts (`sdlc-studio/bugs/`, prefix
`BG`, statuses Open through Closed). The bug lifecycle is the skill's own dogfooded
workflow, so this project files its own defects through the pipeline it ships.

### Severity Definitions

| Severity | Definition | SLA |
| --- | --- | --- |
| Critical | Release gate broken: a script test fails, `npm run lint` cannot pass, or a blocking `gate.py` lane fails; a script writes outside its tested boundary; a gate reports a success it did not achieve | Block the release; fix before tag |
| High | A helper returns wrong JSON or drift verdict; a checker misses a real violation; a guard is applied inconsistently across its call sites | Next release |
| Medium | Style or doc drift a checker does not yet catch; a flagged markdown-behaviour gap; a surviving mutant on a live surface | Backlog, prioritise |
| Low | Cosmetic, wording, or non-blocking allowlist tidy-up | Backlog |

### Verification depth

A bug does not reach a terminal status on an assertion. `transition.py` requires a
recorded **verification depth** before Fixed or Closed, and refuses a claim of proof
above the depth actually performed - a `smoke`-depth check cannot close a bug whose
`Verified:` line claims a functional or live proof. The depth field exists because the
depth tiers were documented for a release without any code reading them, which is the
general failure this document keeps naming: a rule nothing executes is a rule that
holds only when someone remembers it.

---

## Tools and Infrastructure

| Purpose | Tool |
| --- | --- |
| Script test runner | Python `unittest` (stdlib) |
| Mutation / assertion integrity | `.claude/skills/sdlc-studio/scripts/mutation.py` |
| Artefact and release gate | `.claude/skills/sdlc-studio/scripts/gate.py` |
| Flow conformance (eval scenarios) | `tools/eval_run.py` |
| Coverage (on demand) | `coverage.py` (not in CI) |
| Markdown lint | markdownlint-cli (devDependency; `npm install` provides it locally) |
| Prose style guard | `tools/lint-style.sh` |
| Link checker | `tools/check_links.py` |
| Frontmatter validator | `tools/validate_skill.py` |
| Version checker | `tools/check_versions.py` |
| Budget checker | `tools/check_budgets.py` |
| Neutrality checker | `tools/check_neutrality.py` |
| Pre-commit hook installer | `tools/enable-hooks.sh` |
| Task runner | `npm` (lint and test scripts in `package.json`); every check except markdownlint also runs without it |

---

## Test Organisation

```text
.claude/skills/sdlc-studio/scripts/
  <script>.py               # 58 shipped helpers
  lib/                      # 6 shared modules; sdlc_md.py is the parsing core
  tests/
    test_<script>.py        # one module per script; 76 modules, 2151 tests
tools/
  check_links.py            # repo-only CI checkers, themselves unit-tested
  validate_skill.py
  check_versions.py
  check_budgets.py
  check_neutrality.py
  check_action_pins.sh
  lint-style.sh
  style-allowlist.txt
  eval_run.py               # eval-scenario runner
  enable-hooks.sh           # installs the pre-commit gate
  tests/                    # the checkers' own suite (not shipped in the skill)
.markdownlint.json          # markdownlint config
package.json                # lint and test entry points
```

---

## Related Specifications

- [Product Requirements Document](./prd.md)
- [Technical Requirements Document](./trd.md)
- [User Personas](./personas.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Generate mode (brownfield extraction) | Initial TSD reverse-engineered from the skill's actual test setup |
| 2026-07-14 | Generate mode (v4 refresh) | Added the mutation gate (assertion integrity), the eval scenarios (flow conformance), the artefact and release gates with their bound lanes, the story-only rule for executable verifiers, verification depth on a terminal bug status, and the enforced pre-commit hook. Corrected the lint chain (six checks was stale; it is eight), the suite size (181 was stale; it is 2151), the script count (10 was stale; it is 58), and the link-check scope |

---

> **Confidence Markers:** [HIGH] clear from the test setup | [MEDIUM] inferred from
> patterns | [LOW] speculative
>
> **Status Values:** Draft | Ready | In Progress | Complete | Superseded
