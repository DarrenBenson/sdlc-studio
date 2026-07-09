# RETRO-0015: EP0022/EP0023 supply-chain, sync hardening, shared-layer, context tiering

> **Date:** 2026-07-09
> **Batch:** EP0022 (RV0006 debt clearance) + EP0023 (context tiering)
> **Goal:** clear the RV0006 code-quality/security debt (CR0186/CR0187) and land the context-tiering groundwork (CR0179), all behaviour-preserving or dormant on a v2 repo
> **Delivered:** 5 / 5   **Blocked:** 0

## Delivered

- US0102 - `find_by_id`/`story_epic` consolidated onto `lib/sdlc_md.py`; `audit`/`transition`/`lite_profile` delegate; `reconcile` `--format json` parity locked by a test (CR0187 items 1-3).
- US0100 - every GitHub Action pinned to a commit SHA + a `check_action_pins.sh` gate guard; both installers verify a per-release sha256 before extraction (CR0186 items 1-2). Also untracked two accidentally-committed `.local/` fixture files and added a `**/.local/` safety net.
- US0101 - `github_sync push` secret scan (redacted, public/unknown-target refusal, `--allow-secrets` for a confirmed-private target); `http` verb scheme floor + opt-in host allow-list; `.gitignore` hardening (CR0186 items 3-5).
- US0104 - context-tiering digests: `status`/`hint` read a filename-keyed digest instead of opening closed originals (501/59,010 bytes -> 0 on the fixture); `artifact_files` refactored onto `iter_artifact_files(trust_names=...)`; dormant below `digests.min_closed` (default 500) (CR0179).
- US0103 - three complexity hotspots decomposed (`detect_type` 115->40, `transition` 128->45, `detect_conformance` 118->84) behaviour-preservingly; test fixes (raw-string escape, quiet `main()`); `SDLC_DEBUG`/`roll_jsonl` diagnostics (CR0187 items 4-6).

## Blocked / deferred

- None. CR0201 was filed mid-sprint (a follow-up, not a blocker): the `lint-style.sh` provenance-tag guard misses `US`-form and non-leading ids.

## What went well

- The independent-critic gate earned its keep: it caught a real macOS-portability defect (`${var,,}` needs bash 4) in US0100, a shipped-comment provenance tag in US0101, and verified the three US0103 decompositions were behaviour-identical via mutation testing. Two REJECTs, both fixed to APPROVE.
- The US0102 shared-layer `find_by_id` landed first, so US0104's id-resolution AC and US0103's decompositions built on one lookup, not three drifted copies.
- Every unit stayed green per-commit; the closing full-diff critic found no cross-unit interaction, import-cycle, or era-gating defect across five units touching the same `sdlc_md.py`/`reconcile.py`.

## What was hard / what stalled

- US0104's read-path optimisation initially failed its own instrumented test because `artifact_files` reads every file for the is-artifact filter; the real fix was refactoring the enumeration (`iter_artifact_files` with a `trust_names` bypass) and keying the digest by filename (collision-safe), not just short-circuiting the status read.
- The CR ACs had drifted from the codebase (as in the prior sprint): CR0187's `revision`/`rebuild` subcommands did not exist and `--format json` parity was already present, so US0102's ACs were adapted to reality rather than fabricating work.
- The AC Verify DSL bit twice again: `grep -iE` flags reach ripgrep raw (US0100 AC2), so Verify lines were retargeted to clean `shell`/`grep` verbs.

## Lessons

- A "no re-read" optimisation must account for enumeration cost, not just the obvious read - the hot path (`artifact_files`) already read every file, so the win required refactoring the walker, not the caller. <!-- durable: promote if it recurs -->
- The style guard's provenance regex only catches `(CR|BG|RFC)dddd` immediately after `(`, so `US`-form and slash-joined tags pass; a critic caught one in a shipped comment. Filed as CR0201. <!-- lessons add --global candidate -->
- Diffuse-debt CRs age: their ACs drift from the code between filing and delivery. Verify each item against the current tree at grooming time and adapt the story honestly.

## Metrics

- Units: 5/5 delivered, 0 blocked · Critic rejects: 2 (US0100 bash-4 portability, US0101 provenance tag), both fixed -> APPROVE · Suites at close: 1442 skill + 103 tools green · Follow-ups filed: 1 (CR0201) · Nothing pushed (release freeze until v4.0).
