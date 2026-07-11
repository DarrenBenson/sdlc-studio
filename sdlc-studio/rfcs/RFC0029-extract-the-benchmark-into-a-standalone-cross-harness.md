# RFC-0029: Extract the benchmark into a standalone cross-harness project

> **Status:** Draft
> **Date:** 2026-07-11
> **Created-by:** sdlc-studio file

## Summary

The v4 benchmark measured the method axis (process absent / optional / mandated), which
no public benchmark covers - but it lives inside the repo of the tool it flatters and
only drives Claude Code. Extract `tools/bench` into a standalone project that runs any
harness x model x method triple (cursor-cli, codex, opencode...), prices runs via the
Artificial Analysis API, emits an HTML report, and maintains an append-only cross-run
comparison table published at sdlc-studio.com. sdlc-studio becomes one entry in the
method column; reproducibility is the credibility mechanism.

## Context

The 2026-07-10 v4 rerun (82 runs, three models, four arms) produced the quadrant that
carries the white paper and the launch positioning: on the base models, judgement-gated
process converges on unaided behaviour exactly when the process is needed, and mandated
process cuts escapes four to five times for 1.07-1.18x tokens. The measurement outgrew
its housing in three ways:

1. **The question is bigger than the tool.** SWE-bench, Aider polyglot and
   Terminal-Bench all measure model capability on tasks. None measures the method axis:
   same model, same task, process absent / optional / mandated. That axis is the
   question every engineering leader adopting agents actually has, and nobody publishes
   it.
2. **The benchmark is vendor-housed.** It lives inside the repo of the tool it
   flatters. Structural extraction does not make the author neutral, but it changes
   what the artefact is: a harness anyone can point at their own stack, with sdlc-studio
   as one row in the method column.
3. **It only drives Claude Code.** The governor is repo-side (scripts and gates), so
   any harness that can run shell in a repo can be governed. The runner is already
   harness-agnostic by design (prepare/score/record/summary; the agent run is the
   operator's job). The Claude Code coupling is convention, not architecture.

A feasibility spike (this RFC's companion work) runs the digest fixture through
cursor-agent + Composer 2.5, arms B and mandated, n=1 each, to validate headless
viability, gate behaviour in a foreign harness, and token accounting before any code
moves. Spike rows are calibration-phase only, never pooled with measured data.

## Design

### What extracts, what stays

- **Moves:** `tools/bench/` wholesale (runner, arms, fixtures, audit_quiz,
  transcript_metrics, results log) becomes the seed of the new repo.
- **Stays:** `docs/benchmarks/*.md` historical reports remain here as dated evidence
  with a pointer forward; the white paper's claims register keeps resolving.
- **Link back:** the new repo pins sdlc-studio releases by version tag as its method
  entries (the skill under test is an installable artefact, not a submodule of dev
  HEAD).

### Run record schema (the contract everything else serves)

One row per run, append-only JSONL, superset of today's `record()` schema:

- identity: `run_id`, `date`, `phase` (measured / calibration / spike)
- triple: `harness` + version, `model` + version/effort, `method` arm
  (vibe / available / mandated / routed) + method artefact version (e.g.
  `sdlc-studio@v4.0.0`)
- task: `fixture` + generation id
- outcomes: `defect_escape`, hidden-suite detail, `rubric_score`, `audit_score`,
  `spec_mutated` (deterministic diff of protected files against the fixture)
- economics: `tokens_in`/`tokens_out`, `tokens_source: reported|estimated`,
  `wall_time_s`, `cost_usd` + `price_date` + pricing source
- evidence: transcript hash (and, for community rows, the transcript itself)

The existing no-pooling and never-fabricate-zero rules carry over unchanged.

### Fixture generations (leakage policy)

Public fixtures leak into training data and are web-searchable; Fable 5 already passes
the current set clean. Fixtures are versioned as frozen **generations**
(`gen-2026a`...). A generation retires when any frontier model goes clean unaided on
its trap arms. Hidden suites of the LIVE generation are not published; their hashes are
published at generation freeze (tamper-evidence), and the suites themselves are
disclosed when the generation retires. Rows always carry their generation id, so
cross-generation comparison is visible, never silent.

### Task-family breadth (operator requirement)

One trap retold is not a benchmark. The current five fixtures cover two task families;
each new generation should widen coverage, drawing from: brownfield change against a
long-lived spec (the current family), greenfield-from-PRD, refactoring under frozen
behaviour, multi-ticket sequences where later tickets depend on earlier artefacts (the
auditability story), conflicting-requirements tickets (does the method surface the
conflict or ship a guess), and non-Python stacks so the scoring harness is not
accidentally Python-shaped. The rerun's own caveat applies: the mandated arm and any
new family enter as first-class, pre-registered cells in protocol v3, not post-hoc
addenda.

### Harness adapters

A thin adapter per harness owns three things only: (1) instruction-file mapping (the
arm's CLAUDE.md becomes AGENTS.md / .cursor rules as the harness requires - already
confirmed necessary for cursor-agent), (2) headless invocation (command, model flag,
non-interactive/trust flags), (3) usage extraction (where token counts live in the
harness's output, stamped `reported`; `estimated` when the harness reports nothing).
Everything else - workspace prep, scoring, recording - is shared and
harness-independent. Launch set: claude-code, cursor-agent, copilot-cli; codex,
opencode and others follow the same shape (the operator has several more installed).

### Pricing (Artificial Analysis API)

A pricing module resolves model id -> $/Mtok in/out at report time, caching the quote
with its retrieval date; every cost figure in a report names the price date. Removes
the hand-maintained price sheet from the July pricing appendix. Manual override stays
for models the API does not carry (e.g. subscription-bundled harness models priced as
effective rates, disclosed as such).

### Report and site

The report generator renders the runs table to static HTML: leaderboard
(harness x model x method per fixture generation), escape/cost quadrants, per-run
drill-down to disclosed evidence. Published via GitHub Pages on the sdlc-studio.com
domain - zero hosting, versioned with the data. The site carries three things: the
skill, the white paper, the live leaderboard.

### Official vs community rows

Two tables, never merged. Community-submitted rows require the raw transcript attached
and are re-scored from evidence before appearing (verdicts recomputed from the
artefact, never trusted from the submitter - the review-ledger principle applied to
strangers). Vendor authorship is disclosed on every page; the credibility claim is
"run it yourself", not neutrality.

## Design Options

- **O1: Keep the benchmark in-repo** and bolt harness adapters onto `tools/bench` -
  lowest effort, but the vendor-judging-own-product optics remain and the repo's
  neutrality guard fights fixture/report content forever.
- **O2: New standalone repo under the sdlc-studio brand** (e.g.
  `DarrenBenson/sdlc-bench`), sdlc-studio pinned as one method entry, results site on
  GitHub Pages at the domain - honest vendor-authored framing, structural independence,
  zero hosting cost.
- **O3: Neutral-named independent project** with no brand tie - maximum perceived
  neutrality, but the authorship is public anyway, the pretence costs credibility, and
  the domain plus site tie-in is lost.

## Recommendation

O2 - structurally independent, honestly branded, reproducible by anyone; the spike
(cursor-agent + Composer 2.5 on the digest fixture) validates the adapter premise
before any code moves.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Adopt O2 (standalone branded repo) or an alternative | Open |
| D2 | Repo name (`sdlc-bench` proposed) and site placement (apex vs `bench.` subdomain) | Open |
| D3 | Run-record schema v1 fields as specified above | Open |
| D4 | Fixture-generation retirement rule (frontier-clean trigger) and hash-at-freeze disclosure | Open |
| D5 | Launch adapter set (claude-code + cursor-agent + copilot-cli; codex/opencode next) | Open |
| D6 | Community-row policy (transcript-attached, re-scored, separate table) | Open |
| D7 | Protocol v3 lives in the new repo (carries the mandated arm as first-class, per the rerun's caveat) | Open |
| D8 | Task-family expansion order for gen-2026b (brownfield-long-history, multi-ticket sequences, conflicting requirements, non-Python) | Open |

## Spike results (2026-07-11, digest fixture, n=1 per arm)

Feasibility evidence for D5, two foreign harnesses. Spike rows are NOT recorded in
`runs.jsonl` (they are neither measured nor calibration rows of the current protocol);
raw outputs live in the session scratchpad and this summary is the durable record.

**cursor-agent + Composer 2.5:**

| Arm | Hidden suite | Wall time | Usage (in / out / cache-read) | Planning artefact |
| --- | --- | --- | --- | --- |
| B (vibe) | PASS, no escape | 54 s | 19.7k / 7.9k / 206k | n/a |
| Mandated | PASS, no escape | 125 s | 60.2k / 12.5k / 952k | PLAN.md: full R1-R10 interaction table, R5 resolved correctly |

**copilot CLI + ollama/qwen3-coder** (the CLI's default resolved to the operator's
configured BYOK model - see the model-pinning finding):

| Arm | Hidden suite | Wall time | Usage | Planning artefact |
| --- | --- | --- | --- | --- |
| B (vibe) | FAIL, defect escape | 157 s | no token counts reported | n/a |
| Mandated | FAIL, defect escape | 109 s | no token counts reported | plan written OUTSIDE the workspace (`~/.copilot/session-state/`); R5 surfaced and resolved WRONGLY |

The copilot mandated run is a rich negative datum: its plan named R5 explicitly and
resolved it wrongly ("digest notifications are deferred for digest batching, not quiet
hours"), implemented the wrong call faithfully, shipped - the July bad-plan-propagates
mode reproduced on a third model in a third harness - and then **edited `docs/SPEC.md`**
to document digest mode with no quiet-hours interaction, codifying its own misreading
into the project spec. Mandated planning moves where the error occurs; only plan review
catches a wrong plan, and only protected-file tracking catches spec tampering.

Findings:

- **Headless viability: confirmed.** `cursor-agent -p --output-format json --force
  --trust --model composer-2.5` runs a fixture workspace to completion unattended and
  exits 0/JSON; `runner.py prepare`/`score` needed zero changes.
- **Token accounting: confirmed, with a normalisation caveat.** The result JSON carries
  `usage` (input/output/cacheRead/cacheWrite tokens) plus `duration_ms` and
  `session_id` - stampable `tokens_source: reported`. Cache accounting differs from
  Claude Code's transcript metrics, so cross-harness token comparisons need the
  schema's per-harness normalisation note; raw fields must be kept, not just a total.
- **The method travels: confirmed.** The mandated arm produced the written spec-delta,
  per-rule interaction analysis and ACs before code, and resolved the quiet-hours trap
  exactly as the mandate intends - in a harness the skill was never written for.
- **Adapter surface as designed:** instruction-file mapping is real (cursor-agent reads
  `AGENTS.md`, not `CLAUDE.md`) and the pipeline arm's instruction file is Claude
  Code-specific (`/sdlc-studio help` invocation), so arm instruction files need a
  harness-neutral core plus per-harness invocation lines.
- **Model pinning is mandatory.** copilot's default model resolved to the operator's
  configured `ollama/qwen3-coder`, not a GitHub model - a run must pin `--model`
  explicitly and record what the harness actually used (the event stream carries the
  model id per tool call; the adapter reads it back rather than trusting the flag).
- **Token reporting varies from full to none.** cursor-agent reports
  input/output/cache tokens; copilot reports request counts, durations and code-change
  stats only. The schema's `tokens_source: reported|estimated` split is load-bearing,
  not decorative.
- **Planning artefacts need a workspace-rooted requirement.** copilot wrote its plan to
  its own session-state directory outside the repo; the mandate prompt must require the
  artefact at a named path in the workspace, and scoring should verify its existence
  deterministically.
- **New measured column: spec mutation.** The copilot mandated run edited the fixture's
  `docs/SPEC.md` to match its implementation. A deterministic diff of protected files
  (spec, ticket) against the fixture yields a `spec_mutated` boolean per run - an
  auditability axis no other benchmark measures, and cheap to compute.
- **Hermeticity flag per harness.** copilot auto-connects a built-in GitHub MCP server;
  protocol runs must disable external tools (`--disable-builtin-mcps`) so an agent
  cannot research the trap outside the workspace. The adapter owns this flag.
- **Behavioural n=1, not evidence:** Composer 2.5 passed the trap on BOTH arms,
  including unaided baseline - a genuinely interesting data point given Sonnet 5's 2/5
  baseline escapes - while qwen3-coder escaped on both, its mandated plan naming the
  trap rule and resolving it wrongly. One run per cell decides nothing; cross-harness
  cells need the same n>=5 discipline as the rerun.

## Delivery plan (post-acceptance sketch)

1. ~~Spike results appended to this RFC~~ - done above; D5's premise is validated.
2. New repo seeded from `tools/bench` with history-preserving copy; schema v1 +
   generation stamping; claude-code and cursor-agent adapters.
3. Pricing module against the Artificial Analysis API; HTML report; Pages + domain.
4. This repo: `tools/bench` replaced by a pointer; historical reports annotated;
   CHANGELOG entry.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-11 | audit | Filed |
| 2026-07-11 | Claude (Fable 5) | Full design: schema, generations, adapters, pricing, site, community policy |
| 2026-07-11 | Claude (Fable 5) | Spike results: cursor-agent/Composer clean both arms; copilot/qwen3-coder escaped both arms incl. wrong-plan-propagates + spec tampering; adapter findings; task-family breadth (operator); D8 added |
