# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXT0YV** (the gate-and-close-honesty
> sprint, 2026-07-18, RV-0013 / RETRO-0049). Supersedes the RETRO0048 picture.

## Where the pipeline is (2026-07-18)

The **gate-and-close-honesty sprint** (RUN-01KXT0YV) is delivered: **9/9 units, Sprint Goal
ACHIEVED**. The batch was EP0072 (the close-and-gate ergonomics family from the 2026-07-16 audit
triage) plus BG0190, the follow-up left by the previous close.

- **US0216:** the gate's mutation lane names a refused red-baseline run rather than rendering its
  all-zero summary as `0/0 mutations killed`, and carries the report's own remedy.
- **US0213:** `verify_ac` records an `ac_fingerprint` (each AC's id, title and Verify command) and
  the Done gate compares that instead of file mtime, so a status transition, a revision-history row,
  or the verifier's own `Verified:` stamps no longer invalidate a correct green. Legacy reports
  without the field still fall back to mtime.
- **US0218:** `mutation.py --since` spends its ceiling on the changed lines first and reports
  `diff_mutations` / `diff_applied` / `diff_covered`, so a bounded run is evidence about the diff
  rather than about whichever lines sorted first.
- **US0219 / US0220:** the pre-commit gate records each suite's wall-time to a bounded history,
  announces the expected duration before paying it, and names the docs-only skip instead of taking
  it silently.
- **US0217:** a repo-wide conformance failure is attributed once under `globals` rather than charged
  to every judged unit - one doc gap no longer reads as 118 broken units - with the gate still
  counting it so reporting better never enforces less.
- **US0215:** the review-current lane tells an uncommitted-but-current anchor from a stale one and
  names committing the close paperwork as the remedy.
- **US0214:** `review_prep close` writes its own RV index row through the shared meta-index helper.
- **BG0190:** the apply-signoff tail derives a parent epic terminal, scoped to the run's own units
  and refusing on any child it cannot read.

## CODE leg

One independent adversarial full-diff review over `3376648..HEAD`, recorded as a sprint-level
verdict. **Two rounds of REJECT**, both blocking, both on `_derive_parent_epics` and both in the
same direction - claiming completion on incomplete evidence. Round 1: unresolvable and status-less
children were treated as absent rather than incomplete, so an incrementally-written epic would be
marked Done off its one delivered story, across every epic in the repo. Round 2: the repair's
truthiness guard meant an empty units list disabled scoping and restored the full-repo sweep,
reachable via a bug/CR-only batch. Round 3 APPROVE, after the reviewer re-ran its own reproductions
and mutation-checked the new guards. Full suite 2,899 green, drift 0, every commit gated.

The review earned its cost twice: both defects sat in code the author's own tests passed over.

## Document legs

`reference-verify.md` (the fingerprint's freshness model and what it deliberately excludes),
`help/mutation.md` (the diff-biased ceiling), `AGENTS.md` (gate timing expectations), `CHANGELOG.md`,
and the nine groomed units. Each is consistent with the shipped code and enforced by the gate.

## Next steps

- Follow-ups filed this sprint: **BG0191** (the handoff is snapshotted before the apply-signoff
  cascade, so units the close just finished report as remaining), **BG0192** (`cross-epic-ac` is a
  bare keyword match that false-positives on a common English word), **BG0193** (a Verify line whose
  test filter matches nothing passes vacuously - exit 0, zero tests run), **BG0194**
  (`ID_SEARCH_RE` lacks a trailing-digit boundary, so a 5-digit id truncates to its 4-digit prefix).
- **Grooming is not free and was not estimated.** Eight of the nine units arrived as
  `{{placeholder}}` skeletons, so the 26 points described the code and not the work. Run
  `--goal design` over a Draft backlog before committing to a `--goal done` batch.
- Standing: **CR0278** (interactive-sprint token capture) - per-unit actuals were not captured this
  run, so est/actual is not-yet-captured; the sprint total can be supplied with `accuracy --tokens`.
- Residual audit CRs (CR0280-CR0306) and BG0187 remain, plus the eight unstarted refined epics
  (EP0073-EP0076, EP0078, EP0079, EP0081, EP0082) for a future scheduled batch.
- Release freeze holds until ~2026-07-21; everything lands unreleased on `main`.
