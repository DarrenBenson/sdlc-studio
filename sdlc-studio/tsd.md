# Test Strategy Document

> **Project:** SDLC Studio
> **Version:** 2.0.0
> **Last Updated:** 2026-06-20
> **Status:** Generated (brownfield - awaiting validation)
>
> Generated in **Generate mode** by reverse-engineering the skill's own test
> setup (`package.json` scripts, `.claude/skills/sdlc-studio/scripts/tests/`,
> `tools/`, `.markdownlint.json`). Per `reference-philosophy.md`, generated specs
> are not Done until their tests pass against the implementation; the inferred
> claims here await that validation. Confidence markers and status values are
> defined at the foot of the document. Consistent with PRD section 5
> (Non-Functional Requirements) and section 10 (Quality Assessment), and with the
> TRD component and script inventory.

---

## Overview

SDLC Studio is a coding-agent skill: a body of markdown instruction files plus a
small deterministic Python helper layer. It ships no server, UI, or database, so
the test strategy targets two surfaces only - the Python script tier and the
markdown corpus. The script tier is exercised by an executable `unittest` suite;
the markdown corpus is held to its house style and structural invariants by a set
of static checkers run under `npm run lint`. There is no application runtime to
drive, so there are no end-to-end or browser tests, and none are planned. [HIGH]

The binding quality constraint is not latency or throughput but determinism and
context economy: scripts must behave the same way every run, and the always-loaded
footprint must stay within budget. The strategy is built around those two axes.

## Test Objectives

- Prove every Python helper behaves deterministically across the artifact forms
  it must tolerate (dashed and undashed IDs, optional blockquote metadata, mixed
  case, decorated status lines).
- Guarantee read-only helpers stay read-only over the workspace and confine
  writes to `.local/` or named files (TRD section 5, contract rule 5).
- Hold the markdown corpus to its house style (British English, no em dashes, no
  banned jargon) and structural invariants (resolvable links, valid frontmatter,
  line budgets, version consistency) on every commit.
- Keep the release gate honest: all 181 unit tests pass and `npm run lint` exits 0
  before a version is tagged.
- Make the markdown-behaviour test gap explicit rather than implicit, so a future
  test backlog can close it.

## Scope

### In Scope

- Unit tests for the 10 scripts and `lib/sdlc_md.py` (the script tier).
- Static and lint checks over all markdown (house style, links, frontmatter, line
  budgets, version consistency).
- Integration-style tests that run scripts against fixture workspaces in temporary
  directories.
- The release gate (unit suite plus full lint) as a quality gate.

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

**Markdown tier - validated by linters, the script suite, and reconcile/validate,
not by executable behaviour tests.** The markdown command flows describe what the
agent should do; they have no executable harness that asserts the agent did it.
This is an honest gap [HIGH]. Three things stand in for behaviour tests today:

1. Static checkers (`tools/`) enforce house style, link integrity, frontmatter
   validity, line budgets, and version consistency across the corpus.
2. The script suite tests the deterministic helpers the flows invoke, so the
   computational spine of each flow is covered even though the prose is not.
3. `reconcile` and `validate` (read-only census helpers) catch structural and
   status drift in the artifacts a flow produces, and `validate.py instructions`
   enforces instruction-file hygiene.

That triangle is the current oracle for markdown behaviour. It is weaker than
executable conformance tests, and PRD section 10 and TRD Open Question 12.1 both
flag closing it as the main outstanding test investment.

**Generate-mode validation requirement.** Per `reference-philosophy.md`, a spec
extracted in Generate mode (this TSD, the TRD, the PRD) is not Done until its tests
pass against the implementation. For the script tier that bar is met: the 181 tests
pass. For the markdown tier it is not met, because no behaviour tests exist; the
generated claims about markdown flow behaviour remain inferred until that suite is
written. This document records that state rather than overstating coverage.

---

## Test Levels

### Coverage Targets

| Level | Target | Rationale |
| --- | --- | --- |
| Unit (scripts) | ~90% statement coverage | Core deterministic logic; the part that can and must be tested as code. [MEDIUM] |
| Static / lint (markdown) | 100% of `*.md` pass all checkers | House style and structural invariants are binary - any violation fails the gate. [HIGH] |
| Integration (scripts vs fixtures) | Every script with side effects has at least one fixture-workspace test | Confirms read-only confinement and end-to-end script behaviour against real files. [HIGH] |
| End-to-end | Not applicable | No running application or service to drive. [HIGH] |

> The ~90% unit target is a goal, not a presently measured figure. Coverage is not
> currently wired into CI; see Coverage Measurement below. [MEDIUM]

### Unit Testing

| Attribute | Value |
| --- | --- |
| Coverage Target | ~90% statement (goal) [MEDIUM] |
| Framework | Python `unittest` (stdlib) |
| Execution | `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests`, also `npm test` |
| Suite size | 181 tests, all passing; runs in ~0.13s |
| Location | `.claude/skills/sdlc-studio/scripts/tests/test_<script>.py` |

The suite is fast because the helpers are pure stdlib and operate on small
temporary fixture trees. Sub-second runtime keeps the gate cheap to run on every
change.

#### Unit coverage map

Each script and the shared library has a dedicated test module. Test-method counts
are taken from the current suite.

| Module under test | Test file | Tests | What is covered |
| --- | --- | --- | --- |
| `lib/sdlc_md.py` | `test_sdlc_md.py` | 27 | The shared parsing core: ID normalisation (dashed/undashed, mixed case), `extract_field`, `canonical_status` longest-prefix reduction, AC heading and bullet parsing, `Verify`/`Verified` line parsing, JSON helpers that never raise. |
| `verify_ac.py` | `test_verify_ac.py` | 23 | Executable AC verifier: per-AC pass/fail/manual, dry-run vs apply, in-place rewrite of the `Verified:` line, report to `.local/verify-report.json`. |
| `validate.py` | `test_validate.py` | 19 | Read-only validation, including `validate.py instructions` hygiene (AGENTS.md canonical, CLAUDE.md a pointer, doctrine and `LATEST.md` pointers, pre-release gate present). |
| `github_sync.py` | `test_github_sync.py` | 15 | `pull`/`push`/`cascade`/`state` with `gh` mocked; idempotent sync logic; no token handling. |
| `plan.py` | `test_plan.py` | 14 | Plan lifecycle; `plan archive` moving files under `~/.claude/plans/` without delete or overwrite. |
| `lessons.py` | `test_lessons.py` | 13 | Cross-project lessons registry (`_index.md`, `LL{NNNN}-*.md`) read/append. |
| `reconcile.py` | `test_reconcile.py` | 12 | Disk-census drift detection: `status-mismatch`, `missing-row`, `orphan-row`, `count-mismatch`, `missing-index`. |
| `repo_map.py` | `test_repo_map.py` | 12 | AST repo indexer: per-file symbols, imports, in-degree score; `repo-map.json` output. |
| `validate_skill.py` (tool) | `test_validate_skill.py` | 12 | Skill frontmatter validation against the Agent Skills standard. |
| `check_versions.py` (tool) | `test_check_versions.py` | 9 | Version consistency across the five authoritative homes. |
| `status.py` | `test_status.py` | 6 | Four-pillar census, status-cache behaviour. |
| `check_budgets.py` (tool) | `test_check_budgets.py` | 6 | Line-budget enforcement on always-loaded and reference files. |
| `review_prep.py` | `test_review_prep.py` | 5 | Read-only review-input preparation. |
| `next_id.py` | `test_next_id.py` | 4 | Per-type ID allocation (4-digit zero-padded, collision-aware). |
| `check_links.py` (tool) | `test_check_links.py` | 4 | Intra-skill anchor link resolution. |

> The `tools/` CI checkers are themselves unit-tested (rows for
> `test_validate_skill`, `test_check_versions`, `test_check_budgets`,
> `test_check_links`), so the static-analysis layer has executable coverage too.

### Static / Lint Testing (markdown)

This level is the primary guard on the markdown corpus. `npm run lint` chains six
checkers; any non-zero exit fails the gate.

| Check | Command | Enforces | Tooling |
| --- | --- | --- | --- |
| Markdown house style | `lint:md` | markdownlint rules per `.markdownlint.json` (MD013 off, MD024 siblings-only, MD033 off, MD041 off, MD036 off, fenced code) | markdownlint-cli 0.48.0 |
| Prose style | `lint:style` | No em dash (U+2014); no banned corporate jargon outside `tools/style-allowlist.txt` | `tools/lint-style.sh` (bash + grep) |
| Link integrity (skill subtree only) | `lint:links` | Every `path.md#anchor` reference resolves to an existing file and anchor, within the skill subtree | `tools/check_links.py` |
| Skill frontmatter | `lint:skill` | `name` 1-64 chars matching the directory and `^[a-z0-9]+(-[a-z0-9]+)*$`; `description` 1-1024 chars; `metadata.version` X.Y.Z semver; no unknown frontmatter fields | `tools/validate_skill.py` |
| Version consistency | `lint:versions` | Version agrees across package.json, `templates/version.yaml`, SKILL.md frontmatter, README.md, and (at release) CHANGELOG.md | `tools/check_versions.py` |
| Line budgets | `lint:budgets` | `SKILL.md` < 500 lines; each `reference-*.md` <= 600 lines (with a recorded allowlist and 1.05 ceiling tolerance) | `tools/check_budgets.py` |

`lint:fix` (`markdownlint --fix`) is available for auto-fixable markdown issues but
is not part of the gate.

> **Known gap:** `check_links.py` defaults to the `.claude/skills/sdlc-studio`
> subtree and the `lint:links` npm script passes no `--root`, so only the skill's
> own markdown is link-checked. The `sdlc-studio/` artifact corpus (PRD, TRD, TSD,
> personas, epics, stories, RFCs, bugs) is not link-checked, so broken anchors in
> those documents are not caught by CI. markdownlint still runs repo-wide.

### Integration Testing (scripts against fixture workspaces)

The script tests are not pure unit tests in isolation; many build a temporary
`sdlc-studio/` workspace on disk, run the script as it would run in production, and
assert on the files and JSON it produces. The verify run printed during a suite
execution (creating `.local/verify-report.json` in a temp dir, reporting per-AC
pass/fail) is an example of this fixture-workspace pattern. [HIGH]

| Attribute | Value |
| --- | --- |
| Scope | Scripts run end-to-end against a synthesised artifact tree in `tempfile` dirs |
| Framework | Python `unittest` with `tempfile`/`shutil` fixtures |
| Key assertions | Correct JSON output; writes confined to `.local/` or named files; non-zero exit on halting failures; legacy-form tolerance |
| Execution | Same command and gate as the unit level |

### End-to-End Testing

Not applicable. SDLC Studio has no server, UI, or long-running process to drive,
so there is no E2E layer and none is planned (TRD section 13, Won't Have). The
closest analogue - whether the agent executes a markdown flow correctly - is the
untested area described under Test Strategy and Philosophy.

### Performance Testing

Not gated as a runtime metric. The performance budget is context tokens, addressed
structurally by progressive disclosure (always-loaded `SKILL.md` held under 500
lines by `check_budgets.py`), not by a latency assertion. Script runtime is
observed (181 tests in ~0.13s) but not asserted against a threshold. See the
quality-gate table for the NFR mapping.

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
| **Performance** - scripts read-only, reconcile/status sub-second | Indirect: the 181-test suite runs in ~0.13s; a regression that made scripts slow would be visible. No explicit latency threshold is asserted. Treated as observed, not gated. | No | [MEDIUM] |
| **Performance** - always-loaded context minimal | `check_budgets.py`: `SKILL.md` must be < 500 lines, `reference-*.md` <= 600 lines. Hard gate via `lint:budgets`. | Yes | [HIGH] |
| **Security** - no network calls except `gh` and project Verify tools | Enforced by the script contract and the test design: `github_sync.py` tested with `gh` mocked; pure-stdlib (no third-party clients). Not gated by a network-egress scanner. | Partial (by test design, not a scanner) | [HIGH] |
| **Security** - no secrets handled by the skill | Not gated by a secret scanner in this repo. Enforced by design (no token handling; `gh` owns auth) and by code review. N/A as an automated gate. | No (design control) | [MEDIUM] |
| **Scalability** - progressive disclosure keeps always-loaded context constant | `check_budgets.py` line budgets (as above); new commands add a `help/` file and a guide row, not router bulk. | Yes | [HIGH] |
| **Scalability** - agentic waves bound concurrency | Not gated. Concurrency bounds are an instruction-level behaviour in `reference-agentic-lessons.md`; no executable test asserts wave sizing. N/A as an automated gate. | No | [MEDIUM] |
| **Availability** - offline-capable; sync aborts cleanly when `gh`/remotes absent | Offline capability comes from the core pipeline scripts, which make no network calls (verified by the no-network contract and stdlib-only design). `github_sync.py` does not soft no-op: with `gh` absent it aborts with a clear error (exit 127), asserted by `test_github_sync.py`. So the NFR is met for the offline pipeline, but `github_sync` does not degrade gracefully - callers must handle the non-zero exit. | Partial (unit) | [MEDIUM] |

Additional gates that back the NFRs but sit outside the four PRD headings:

| Gate | Criteria | Blocking |
| --- | --- | --- |
| Unit suite | All 181 tests pass | Yes |
| Markdown lint | `npm run lint` exits 0 (all six sub-checks) | Yes |
| Link integrity | `check_links.py`: every anchor resolves | Yes |
| Skill frontmatter | `validate_skill.py`: valid against Agent Skills standard | Yes |
| Version consistency | `check_versions.py`: all homes agree (CHANGELOG advisory between releases, required at release) | Yes (release) |
| Instruction hygiene | `validate.py instructions` passes | Manual (recommended; not yet CI-wired - no npm script or workflow invokes it) |

---

## Coverage Measurement

Statement coverage for the script tier is not presently collected in CI; the ~90%
target is a goal inferred from the per-script test density (every script and the
shared library has a dedicated module, totalling 181 tests). [MEDIUM] To measure it,
run the suite under `coverage.py`:

```bash
cd /home/darren/code/DarrenBenson/sdlc-studio
python3 -m coverage run -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
python3 -m coverage report -m --include='.claude/skills/sdlc-studio/scripts/*'
```

Markdown "coverage" is binary rather than percentage-based: the corpus either
passes all six lint checks or it does not. There is no partial-pass state.

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

- The entire script tier (already automated as the 181-test suite).
- All markdown structural and style invariants (already automated as the six lint
  checks).
- The release gate composition (suite plus full lint).

### Manual Testing

- The markdown command flows. Until executable conformance tests exist, flow
  correctness is judged by use and by the manual verification steps in `CLAUDE.md`
  (install the skill, run `help`, `status`, `repo map build`, and
  `reconcile --verify --dry-run` against a fixture story).
- Cross-harness install behaviour (`install.sh` / `install.ps1`) beyond the
  Windows pwsh smoke test already in CI.

### Automation Framework Stack

| Layer | Tool | Language |
| --- | --- | --- |
| Script unit / integration | `unittest` (stdlib) | Python 3.10+ |
| Markdown lint | markdownlint-cli 0.48.0 | Node |
| Prose style | `lint-style.sh` (grep) | Bash |
| Structural checkers | `check_links`, `validate_skill`, `check_versions`, `check_budgets` | Python 3.10+ |

---

## CI/CD Integration

### Pipeline Stages

1. **Pre-commit (local):** `npm run lint` and `npm test`.
2. **PR / push:** full lint chain plus the 181-test suite; a Windows pwsh smoke
   test for `install.ps1`.
3. **Pre-release tag:** all tests pass, full lint passes, and `check_versions.py`
   confirms every version home agrees including CHANGELOG. Running
   `validate.py instructions` is a recommended manual pre-release check; it is not
   yet wired into any npm script or workflow, so instruction-file drift is not
   automatically gated.

There is no merge-to-main E2E stage and no nightly performance stage, because no
running application exists to exercise.

### Quality Gates

| Gate | Criteria | Blocking |
| --- | --- | --- |
| Unit suite | 181/181 pass | Yes |
| Markdown lint (`lint:md`) | 0 violations | Yes |
| Prose style (`lint:style`) | No em dash, no un-allowlisted jargon | Yes |
| Link integrity (`lint:links`) | All anchors resolve | Yes |
| Skill frontmatter (`lint:skill`) | Valid | Yes |
| Version consistency (`lint:versions`) | All homes agree | Yes (release) |
| Line budgets (`lint:budgets`) | Within budget | Yes |

---

## Defect Management

Defects are tracked as SDLC Studio `bug` artifacts (`sdlc-studio/bugs/`, prefix
`BG`, statuses Open through Closed). The bug lifecycle is the skill's own dogfooded
workflow, so this project files its own defects through the pipeline it ships.

### Severity Definitions

| Severity | Definition | SLA |
| --- | --- | --- |
| Critical | Release gate broken: a script test fails or `npm run lint` cannot pass; a script mutates files outside its remit | Block the release; fix before tag |
| High | A helper returns wrong JSON or drift verdict; a checker misses a real violation | Next release |
| Medium | Style or doc drift a checker does not yet catch; a flagged markdown-behaviour gap | Backlog, prioritise |
| Low | Cosmetic, wording, or non-blocking allowlist tidy-up | Backlog |

---

## Tools and Infrastructure

| Purpose | Tool |
| --- | --- |
| Script test runner | Python `unittest` (stdlib) |
| Coverage (on demand) | `coverage.py` (not in CI) |
| Markdown lint | markdownlint-cli 0.48.0 |
| Prose style guard | `tools/lint-style.sh` |
| Link checker | `tools/check_links.py` |
| Frontmatter validator | `tools/validate_skill.py` |
| Version checker | `tools/check_versions.py` |
| Budget checker | `tools/check_budgets.py` |
| Task runner | `npm` (lint and test scripts in `package.json`) |

---

## Test Organisation

```text
.claude/skills/sdlc-studio/scripts/
  <script>.py
  lib/sdlc_md.py
  tests/
    test_<script>.py        # one module per script and per tool checker
tools/
  check_links.py            # CI checkers, themselves unit-tested
  validate_skill.py
  check_versions.py
  check_budgets.py
  lint-style.sh
  style-allowlist.txt
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

---

> **Confidence Markers:** [HIGH] clear from the test setup | [MEDIUM] inferred from
> patterns | [LOW] speculative
>
> **Status Values:** Draft | Ready | In Progress | Complete | Superseded
