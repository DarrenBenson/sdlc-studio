# US0385: reconcile trd.md and tsd.md and record the findings

> **Status:** Draft
> **Delivers:** CR0385
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0141
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, sdlc-studio/tsd.md, sdlc-studio/stories/US0385-reconcile-trd-md-and-tsd-md-and-record.md

## User Story

**As a** reader of this project's own spec, and of the spec-truth checks that read it
**I want** the mutation entries in trd.md and tsd.md to match what ships, and the pass to record every claim it checked
**So that** a criterion that deletes tests is not built on a superseded evidence shape, and the next reader can tell a claim that was verified from one that was never looked at

## Known divergences to reconcile

Four entries describe the single-blob model only:

- `trd.md` artefact table: `mutation-report.json` is listed with no sibling row for
  `mutation-runs.json`, so the ledger is absent from the artefact inventory.
- `tsd.md` mutation table, Output row: names the report, the git rev and a content hash per
  target, with no ledger.
- `tsd.md` mutation table, Gate row: "a rev change or an edited target reads STALE" - the
  superseded whole-blob rule.
- `tsd.md` gate-lane table: the `mutation` lane is described as reporting nothing beyond the
  report, not as judging per-file coverage.

## Acceptance Criteria

### AC1: both documents match the shipped ledger and coverage model

- **Given** the four divergences above
- **When** a reader compares each entry with `mutation.py` and the gate's coverage lane
- **Then** every entry names the ledger as the gate's source, states the per-file content-hash
  key, and states the covered / stale / uncovered verdict in place of the whole-blob rule;
  the report keeps its own row, since it is still written and still carries the survivors
- **Verify:** manual diff each of the four entries against mutation.py and gate.py, confirming no statement remains that only the report exists

### AC2: the pass records what was checked, not only what was changed

- **Given** the mutation-related claims in both documents, including those found correct
- **When** the reconcile pass finishes
- **Then** a findings table in this story lists every claim checked with its file, its verdict
  (correct, incomplete or false) and what was done, so a claim nobody examined is
  distinguishable from one examined and left alone
- **Verify:** manual confirm the findings table exists, covers every mutation claim in both files, and carries a verdict per row including the unchanged ones

## Findings

Every mutation-related claim in `trd.md` and `tsd.md`, each checked against
`scripts/mutation.py` and `scripts/gate.py` at the line cited. Rows marked **correct** were
examined and left alone, so a claim nobody looked at is distinguishable from one that was.

| # | File / entry | Claim as written | Verdict | Checked against | Action |
| --- | --- | --- | --- | --- | --- |
| 1 | `trd.md` state-file table | `mutation-report.json` carries per-mutant verdicts, the git rev and a content hash per target | correct | `mutation.py` `run_mutations` report dict; `report["git_rev"]`, `target_hashes` | kept |
| 2 | `trd.md` same row | "so a dirty tree cannot ride an old green" | incomplete | `gate.py` `_mutation`: the report's rev/hash checks run only when `_mutation_coverage` returns `known: False` | rewritten - the report is the latest run and its stamp is the fallback, not the guarantee |
| 3 | `trd.md` state-file table | no row at all for `mutation-runs.json` | false by omission | `mutation.py` `ledger_path`, `append_ledger`; `gate.py` `_mutation_coverage` reads it as the ONE source | row added: per-target ledger, content-hash key, `measured`/`registered`, 200-entry bound with cumulative `dropped` |
| 4 | `trd.md` gate section | `mutation` is one of the lanes in the gate's default sweep | correct | `gate.py` lane registry; `_mutation` runs unselected and returns `blocking: False` on every path | kept |
| 5 | `tsd.md` mutation table, Scope | four fault classes over `--files` / `--since` / `--story` | correct | `mutation.py` `FAULT_CLASSES`, `select_files` | kept |
| 6 | `tsd.md` mutation table, Method | green baseline first, apply one, re-run, restore, verdict | correct | `mutation.py` `run_mutations` baseline refusal and per-mutant loop | kept |
| 7 | `tsd.md` mutation table, Verdicts | killed / survived / error / unviable | correct | `mutation.py` `RUN_VERDICT_COUNTER` | kept (the `equivalent` registration verdict is a `register` input, not a run verdict, and is documented on the Gate row instead) |
| 8 | `tsd.md` mutation table, Output | names `mutation-report.json` only | incomplete | `mutation.py` `run_mutations` writes the report AND calls `append_ledger`; `LEDGER_LIMIT = 200` | rewritten to name both, with the ledger's key, bound and entry rule |
| 9 | `tsd.md` mutation table, Gate | "a rev change or an edited target reads STALE" | false (superseded) | `gate.py` `_mutation_coverage`: hash matches -> covered, hash differs or none recorded -> STALE, no entry -> uncovered; the whole-blob rule is the degraded fallback only | replaced with the per-file verdict, with the fallback stated as such |
| 10 | `tsd.md` mutation table, Honest degrade | an un-mutatable file/construct is listed un-checked | correct | `mutation.py` `run_mutations` `unchecked` list | kept |
| 11 | `tsd.md` advisory rationale prose | advisory because a run costs one suite execution per mutant | correct | `mutation.py` per-mutation `subprocess` re-run, `_RUN_TIMEOUT` | kept |
| 12 | `tsd.md` gate-lane table | `mutation` reports "Nothing (report only)"; rev-or-edit STALE | false | `gate.py` `_mutation` `_with_coverage` folds the coverage detail and count into the lane's output | rewritten: per-file coverage from the ledger plus the report's survivors, fallback named |
| 13 | `tsd.md` test-tier map, Verification row | "the STALE-on-edit rule" | imprecise | `gate.py` `_mutation_coverage` judges staleness per file, not per blob | qualified as per-file, and the ledger's bound and provenance added |
| 14 | `tsd.md` NFR table | `mutation` exempt from the sub-second read path (minutes per run) | correct | as row 11 | kept |
| 15 | `tsd.md` tool tables (two rows) | mutation / assertion integrity is `scripts/mutation.py` | correct | the file exists at that path; its docstring states "Pure stdlib" and it imports only stdlib plus `lib/sdlc_md` | kept (the shared Python 3.10+ floor is the repo's, not a mutation-specific claim) |
| 16 | `tsd.md` testing-levels prose (three places: overview, goals, coverage contrast) | `verify_ac` proves tests pass, `mutation.py` proves they can fail; coverage asks whether a line ran, mutation asks whether a test would notice | correct | `mutation.py` module docstring; `run_mutations` killed/survived logic | kept |
| 17 | `trd.md` performance prose | "its gate lane reads a stored report rather than executing, and reports STALE on a rev change or an edited target rather than passing" - not in the groomed list, found in this pass | false (superseded) | `gate.py` `_mutation_coverage` reads the ledger, not the report, and judges staleness per file | rewritten: reads stored evidence, and a file whose bytes changed since its mutant ran reads STALE |
| 18 | `tsd.md` pre-commit-gate blockquote | assertion integrity "is now executably enforced by the mutation gate" - not in the groomed list, found in this pass | imprecise (overclaim) | `gate.py` `_mutation` is `blocking: False` on every path, so the lane cannot refuse a commit | qualified: executably checked, with the advisory lane stated |
| 19 | `tsd.md` Generate-mode header | the document was reverse-engineered partly from `scripts/mutation.py` | correct | provenance statement about how the document was written, not a behavioural claim | kept |

## Notes

Both files feed the spec-truth checks. Their revision-history tables take a row for this pass,
naming the reconcile rather than describing it as an edit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc-studio | Reconcile pass run: 19 mutation claims across `trd.md` and `tsd.md` checked against source, 8 corrected (2 of them found in this pass, not in the groomed list), 11 verified correct and left alone; findings table recorded above |
