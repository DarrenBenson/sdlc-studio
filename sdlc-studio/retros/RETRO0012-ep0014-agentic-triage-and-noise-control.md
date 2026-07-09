# RETRO-0012: EP0014 - agentic triage and noise control (the four-critic sprint)

> **Date:** 2026-07-09
> **Batch:** EP0014 / US0065-US0068 (closes CR0173 + CR0172)
> **Goal:** `done` - move the human from triage gate to sampling auditor, schema-v3 dormant
> **Delivered:** 4 / 4   **Blocked:** 0

## Delivered

- **US0065** - the `inbox` triage lane: findings (bug/cr/rfc) file into `inbox` under
  `schema_version: 3` (both `artifact.new` and `file_finding`), and a gated `inbox`->triaged
  transition records a structured `triaged_by` and enforces separation of duties (solo-human
  warns, never deadlocks). Triaged target is type-specific (bug->Open, cr->Approved, rfc->In
  Review); `--triage-severity` records the triager's severity alongside the raiser's.
- **US0067** - triage noise controls (`triage_noise.py`): a session cap (default 20) refuses the
  N+1th finding loudly; a Low-severity finding folds into a themed consolidation CR. Routed from
  both filing paths so neither is a bypass.
- **US0068** - a record-only `Tranche` reference: `validate` shape check, `artifact.new`
  pass-through writer, `status tranche` query, all on the shared newline-safe `sdlc_md.tranche_ref`.
- **US0066** - triage-as-sampled-audit (`triage_sampling.py`): a seeded sampling policy (every
  Critical + every raiser/triager disagreement + `sample_rate` of the rest) and triage-quality
  metrics from the records (false-positive rate, severity inflation, sampled-pending), surfaced
  by `status triage-metrics`.

All era-gated behind `schema_version: 3`, dormant on v2 (the repo is v2; the release freeze holds).

## Critic loop, observed

The story - four independent adversarial critics (each a separate instance from the author,
each framed to refute), and the closing full-diff pass. **Every one earned its keep.** The
per-unit reviews saw one story's diff; the closing pass saw the whole sprint.

| Unit | Verdict path | The escape the author's own tests missed |
| --- | --- | --- |
| US0065 | REJECT -> fix -> APPROVE | `file_finding` (the primary agent finding-filer) bypassed the inbox lane; the gate guarded only the canonical target, so `inbox`->In Progress/terminal sidestepped triage |
| US0067 | REJECT -> fix -> APPROVE | a consolidation theme containing `·` (the codebase's own field separator) was truncated by `extract_field` on read-back -> a new CR per finding instead of one |
| US0068 | REJECT -> fix -> APPROVE | the query read the value with the general `extract_field`, whose leading `\s*` crosses newlines -> an empty `Tranche` line phantom-matched the next line as its value |
| US0066 | APPROVE (LOW fixed) | an `id()`-based pool re-filter could over-count a duplicated dict object (unreachable, latent) |
| Closing full-diff | APPROVE (LOW fixed) | a record-only tranche was silently dropped when a Low finding consolidates (cross-unit: US0067 x US0068) - no per-unit review could see it |

Survivors of the adversarial pass: none uncontested. Three REJECTs were genuine correctness
bugs (not style), each reproduced by the critic, fixed test-first, and re-reproduced clean by the
same critic before APPROVE. Two LOW findings were latent/edge but fixed anyway (the sprint's own
"fail loud, not silent drop" principle demanded the tranche-drop be made visible).

## What went well

- **The independence gate is not ceremony.** Four for four, an instance that did not write the
  code found a real defect the author's tests passed over. Two were the *same class* of bug
  (`extract_field` over-capturing across newlines) surfacing in two different units - the second
  critic caught it in the query path after the first fixed it in the validation path.
- **Era-gating held end to end.** The closing pass exercised a full v2 repo and confirmed nothing
  from any of the four stories changes v2 behaviour - the release-freeze contract intact.
- **Deterministic tooling did the bookkeeping.** Ids, index rows, status cascades, conformance
  verdicts, and the decisions ledger were all script-allocated; reconcile stayed at drift 0
  through 4 commits.

## What was hard

- **Shared-file composition.** All four stories touched `artifact.py` / `status.py` / `sdlc_md.py`,
  so true parallel worktrees would have collided. Running them sequentially as orchestrator (wave
  order US0065 -> {US0067, US0068} -> US0066) with a per-unit critic was the right call, and the
  closing full-diff pass existed precisely to catch what sequential per-unit review cannot (the
  tranche-drop was a US0067 x US0068 interaction).
- **A catalogue at its ceiling.** `reference-scripts.md` was exactly at its 600-line budget; two
  new scripts needed entries. Trimmed hard, then allowlisted deliberately at 619 - the catalogue
  wants splitting when it next grows.

## Lessons

- **Re-run-your-own-repro is where escapes die.** Each fix was verified by the *same* critic
  re-running its original reproduction, not by the author asserting green. That step turned three
  plausible fixes into proven ones.
- **A design note names the tidy path, not the whole surface.** US0065's note said "`artifact.py`
  files into inbox"; the real primary filer was `file_finding.py`. Read the code for every path,
  not just the one the note names.
- **When two units share a creation path, add a closing pass that composes them.** The tranche
  drop was invisible to both per-unit reviews by construction.
- **Deferred, on purpose:** stamping a structured `Raised-by` on tool-filed findings, so the
  triage separation-of-duties check is never vacuous, is EP0013 authorship territory - recorded in
  the ledger, not smuggled into this sprint.

## Metrics

- Delivered 4/4; 0 blocked. 5 adversarial reviews, 5 real findings (3 correctness REJECTs, 2 LOW),
  0 shipped unaddressed.
- 1312 script tests pass (was 1274 at sprint start; +38 new triage tests across 5 test modules).
- Gate PASS; reconcile drift 0 throughout; per-unit conformance 7/7 stages on all four stories.
- Story index now 35 terminal rows (> 30 advisory) - archive deferred to the v4.0 cut (no release
  label to archive under mid-freeze).
