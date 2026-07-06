# RV-0006: Repository review 2026-07-06: architecture, code quality, defensive security

> **Date:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Reviewer:** Sam Eriksson (QA amigo)
> **Method:** hand-written "Repository Review Prompt" (the CR0175 starting spec), run read-only
> on source. Three parallel review legs (architecture, code-level, defensive security), each
> finding evidence-cited; every reported finding re-verified at its cited file:line before
> filing. Remediation-only for security (no exploit steps, no payloads, no secret values).

## System overview

SDLC Studio is a Claude Code agent skill (Agent Skills open format), not an application: a
progressive-disclosure markdown knowledge base (`SKILL.md` router plus ~46 reference files,
help, and templates) over a read-mostly stdlib-Python layer (43 top-level scripts under
`.claude/skills/sdlc-studio/scripts/`, shared `lib/sdlc_md.py`). Files are the source of truth;
`_index.md` tables and statuses are derived and reconciled from a disk census. GitHub
integration is via the `gh` CLI only (no token handling). Repo CI guards live in `tools/`; the
repo dogfoods the skill against its own `sdlc-studio/` workspace. Project version 3.5.0.

The codebase is disciplined and above category norm: uniform exit-code convention, every broad
`except` annotated and confined to advisory lanes, findings that carry their own fix strings,
`yaml.safe_load` throughout, argv-list subprocess calls (no string-built shells outside the one
declared `eval`/`shell` verifier verb), slugs sanitised to `[a-z0-9-]` before becoming
filenames, and a fast, isolated 1160-test unit suite. The defects below sit mostly at the
cross-script seams and in one prose-only trust boundary, not in the core.

## Architecture assessment (per Phase 1 dimension)

1. **Module boundaries/coupling** - Sound but with a god module: `reconcile.py` (1277 lines,
   11 sibling importers, private-underscore cross-module use) is the de-facto shared index
   library while `lib/` officially owns conventions. `github_sync` forks its own discovery
   layer. Import graph is acyclic. (CR0181, CR0187)
2. **Data flow / mutable state** - Files-are-truth is consistently implemented and honestly
   reported. Defects: double telemetry per close (BG0053), stale-report Done gate (BG0065),
   two master-table policies (BG0066).
3. **Error handling** - Consistent and above average; weak spots are github_sync's
   failure-as-empty-list and a state stamp after failure (BG0064).
4. **Config / secrets** - Secrets handling is genuinely clean (gh-only, no tokens, no committed
   secrets found). Config handling has three inconsistent regimes - silent default, fail-loud,
   hard PyYAML crash - and the README's "no pip installs" claim is false at the config/gate
   edge (CR0180, BG0062).
5. **Concurrency / resources** - Weakest dimension: zero locking, non-atomic
   truncate-and-write, allocation TOCTOU, one untimed network subprocess (BG0063), unbounded
   append logs. Tolerable only under an undocumented-as-mandatory single-writer convention
   (CR0183).
6. **API surface / contract** - Argparse contract largely uniform (`--root`, `--format json`)
   with drift points: `--repo-root` vs `--root`, github_sync's missing `--root`, and a
   CLI-vs-library allocation divergence (BG0060). (CR0181)
7. **Test architecture** - Excellent unit tier, effectively no integration tier over
   cross-script cascades - which is where this review's real bugs live (CR0185).
8. **Observability** - Adequate for blocking paths (self-diagnosing findings, `.local`
   reports, honest STALE/NOT-RUN states); advisory paths are black holes with no opt-in debug
   channel (CR0187 item 7).
9. **Documentation drift** - README and SKILL.md accurate; the TRD is two majors stale and
   misstates the script count, write contract, state files, and test figures (CR0184); the
   reconcile docstring misstates its own write surface (CR0187 item 1).
10. **Scalability / performance** - Fit for purpose at realistic scale (measured ~0.35s full
    reconcile over ~330 artefacts). O(corpus) re-reads are latent, not urgent.

## Findings table

All severities were re-verified at the cited file:line. "Dedup" notes overlap with the
last-session ledger (CR0166-CR0179).

| ID | Title | Type | Severity | Effort |
| --- | --- | --- | --- | --- |
| BG0053 | artifact.py close records telemetry twice per close | Bug | High | S |
| BG0054 | install.sh exits 1 after a successful install (set -e sweep) | Bug | High | S |
| BG0055 | ts-check verify-report cross-check keys on bare AC id | Bug | High | S |
| BG0056 | verify_ac shell trust boundary is prose-only (CWE-78) | Bug | High | M |
| BG0057 | verify_ac unrecognised expressions fall through to shell (CWE-78) | Bug | Medium | S |
| BG0058 | CI workflow has no permissions block (CWE-250) | Bug | Medium | S |
| BG0059 | gate.py --only unknown check yields vacuous PASS | Bug | Medium | S |
| BG0060 | next_id allocate CLI diverges from allocate_number | Bug | Medium | S |
| BG0061 | archive.py hardcodes terminal sets: Deferred archived as closed | Bug | Medium | S |
| BG0062 | Done/parity gates crash with PyYAML error on stdlib machines | Bug | Medium | S |
| BG0063 | github_sync gh() runs network subprocess with no timeout | Bug | Medium | S |
| BG0064 | github_sync pull stamps last_pull even when gh failed | Bug | Medium | S |
| BG0065 | Done verify gate passes on a stale merged report entry | Bug | Medium | S |
| BG0066 | append_index_row scans unbounded, disagrees with reconcile | Bug | Medium | M |
| CR0180 | Harmonise the three config failure regimes | CR | Medium | M |
| CR0181 | Route github_sync/verify_ac through shared discovery; unify --root | CR | Medium | M |
| CR0182 | Consolidate the two archive implementations on iter_tables | CR | Medium | M |
| CR0183 | Passive concurrency safety: atomic writes + advisory lock | CR | Medium | M |
| CR0184 | Refresh the stale v2.0.0 TRD | CR | Medium | M |
| CR0185 | Cross-script invariant test tier over the cascade seams | CR | Medium | M |
| CR0186 | Security hardening debt (6 Low findings, themed) | CR | Low | M |
| CR0187 | Code-quality debt (Low findings, themed) | CR | Low | M |

14 bugs (4 High, 10 Medium) + 8 CRs (6 Medium, 2 themed Low). Low findings consolidated into
CR0186 (security: action pinning, installer integrity, sync redaction, `.local` hygiene, http
verb limits, mutation `--test` boundary doc) and CR0187 (quality: stale docstrings, primitive
duplication, uneven `--format json`, complexity hotspots, latent test-suite issues, unbounded
logs, debug channel).

## Deduplication against the open ledger

- BG0060/BG0066 (id allocation, index placement) touch the same identity/index surface that
  RFC0024/CR0167 (distributed identity) and CR0168 (derived indexes) redesign. Filed as bugs
  because they are defects in the *current* scheme, cross-referenced to the redesign; fixing
  them is worthwhile even though the redesign will later supersede the mechanism.
- CR0183 (passive concurrency) is explicitly positioned as the floor that complements
  RFC0024 - ULIDs remove the id race, but index and cascade writes still need atomicity.
- CR0184 (TRD refresh) is doc work adjacent to CR0177 (README/positioning); different
  document, coordinate wording.
- No finding duplicated an open artefact outright; CR0166 (batch scaffold polish) does not
  overlap.

## Positive observations (no action)

No committed secrets in the working tree. `yaml.safe_load` only; no `eval`/`exec`/pickle on
data outside the declared verifier verb. gh/git calls are argv lists throughout. Slugs/ids
sanitised before becoming filenames (path-traversal closed). `version_check.py` fetches only a
hard-coded HTTPS GitHub endpoint and degrades silently. `install.sh` sweep only deletes
directories verified as skill copies. CI already runs bandit at `-ll`. Telemetry is local
JSONL, no network. `pvd.py` writes copies read-only (0444). Test suite asserts on behaviour,
not fixtures (1201 test functions sampled; the 8 assert-free ones delegate to asserting
helpers).

## Verification (Phase 4, read-only)

- `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests` -> **Ran 1160
  tests, OK**.
- `python3 -m unittest discover -s tools/tests` -> **Ran 41 tests, OK**.
- `npm run lint` (markdown, style, links, skill, versions, budgets, neutrality) -> **all
  pass**.
- `npm audit` -> **found 0 vulnerabilities**.
- `reconcile.py detect` -> **0 drift**; `validate.py check` -> **345 checked, 0 errors** (after
  filing the 22 new artefacts).

## Limitations

- `pip-audit`/`cargo audit` not applicable - runtime Python is stdlib-only; the only pinned
  dependency is the `markdownlint-cli` devDependency (npm audit covers it).
- Secret scan covered the working tree only, not full git history or the npm dependency tree.
- bandit was not executed in this review (read-only; CI already runs it at `-ll`).
- The reconcile multi-view double-archive path (BG0066-adjacent, noted under CR0182) is
  inferred from code paths, not yet reproduced against a live multi-view fixture - CR0182's
  acceptance test will confirm or clear it.
- Whether the org already restricts the default `GITHUB_TOKEN` to read-only was not knowable
  from the repo (open question on BG0058); the fix is cheap regardless.

## Top five priorities (recommended order)

1. **BG0056** - verify_ac shell trust boundary (High, security). The only finding with a path
   from external content (GitHub issue bodies) to shell execution. Add the technical
   provenance control the docs already assume.
2. **BG0053** - double telemetry per close (High). Silently corrupts the estimation-calibration
   data the learning loop exists to provide; a one-line fix plus a count assertion.
3. **BG0055** - ts-check bare-AC cross-check (High). Produces false cross-story failures that
   erode trust in the one gate meant to stop a matrix claiming green over a red runner.
4. **BG0054** - install.sh false-failure on sweep (High). First-run experience: a successful
   multi-tool install reports failure to every user the sweep is for.
5. **BG0059 + BG0062** - vacuous gate PASS and the PyYAML gate crash (Medium, paired). Both are
   fail-loud violations of the project's own LL0008; cheap, and they protect every downstream
   gate.

## Verdict

Healthy, well-disciplined codebase with no Critical findings and a clean security core. The
risk concentrates in one prose-only execution boundary (BG0056) and a cluster of cross-script
seam defects the strong unit suite does not reach (CR0185 closes that gap). Recommend a first
tranche of the four High bugs plus the paired fail-loud Mediums, then the enforcement/quality
CRs. This review also validates the CR0175 on-ramp workflow end to end: read-only on source,
every finding evidenced and tool-filed, zero drift introduced.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full report: 14 bugs + 8 CRs filed, verification recorded, priorities set |
