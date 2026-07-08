# CR-0188: Fetch and check origin drift before a sprint batch or artifact-id allocation

> **Status:** Proposed
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** P2
> **Type:** retrospective

## Summary

A local clone can run a sprint against a stale checkout with no warning. Make a
`git fetch` + origin-drift check a mandatory pre-flight for `sprint plan` (and
for standalone artifact-ID allocation), not just the already-documented
cross-repo case.

## Problem

On 2026-07-08 a local clone of this repo (last synced at v3.2.0, 2026-06-27)
ran a full RFC-decide-and-deliver sprint (RFC0018 D2/D3 -> CR0131/CR0132 ->
US0051/US0052) entirely offline from `origin/main`, which had in the meantime
moved 115 commits / 325 files ahead to v3.6.0 (2026-07-06). Two things broke:

1. **Silent ID collision.** `artifact.py new` allocates the next free number by
   scanning the *local* working tree only (`next_id.allocate_number`, no
   `--remote`). It happily handed out CR0131, CR0132, US0051, US0052 - all four
   already existed on `origin/main` as unrelated, already-shipped work. A
   `git pull`/rebase later would have hit four add/add conflicts on
   identically-numbered, differently-titled files.
2. **Duplicate delivery.** Origin had *already* shipped near-equivalent
   versions of both features the stale sprint built (a subcommand-verb-taxonomy
   doc in `best-practices/script.md`, and `telemetry.py show --summary`) as
   part of that same 115-commit history - independently designed, already
   reviewed, already released. The stale sprint's two commits were pure
   duplicate effort, recovered only by discarding them (`git reset --hard
   origin/main`, backed up to a throwaway branch first) after the drift was
   noticed by chance while investigating an unrelated skill-update notice.

The existing safeguard (`reference-cr.md`'s "Cross-repo guard") already
prescribes `git fetch` + `git ls-tree origin/main` before numbering a CR/RFC,
and `next_id.py` already implements a `--remote` mode that does exactly this
(read-only `git ls-tree`, no fetch - caller fetches first) - but today it is
scoped to "when the CR namespace is shared across two or more repos" and nothing
calls it by default. This incident shows the same failure mode inside a single
repo whose local clone is simply behind its own origin - fetch-and-check should
not be conditional on the repo being multi-repo.

---

## Proposed Changes

### Item 1: Sprint precondition - fetch and report drift before planning

**Priority:** P2
**Effort:** 2

`reference-sprint.md`'s existing "Precondition - a runnable gate" section (and
`scripts/sprint.py plan`) gains a mandatory pre-flight: `git fetch origin` (if a
remote named `origin` exists - no-op otherwise), then compare local `HEAD` to
`origin/<default-branch>`. If local is behind, **stop and report** the commit
count and touched-path overlap with the batch about to be planned, rather than
silently proceeding. This mirrors the existing "Reconcile before plan" step
(`sprint.py plan` already runs `reconcile detect` first) - add a
`remote-drift` check alongside it, same severity (warns; refuses under
`--strict`).

### Item 2: Artifact-ID allocation defaults to remote-aware when a remote exists

**Priority:** P2
**Effort:** 2

`artifact.py new`/`batch` currently call `next_id.allocate_number(type_, root)`
with no `--remote`. Change the default to probe for an `origin` remote and, if
present, use the already-built `next_id.py --remote` path (read-only
`git ls-tree -r origin/<branch>`, no fetch performed by the allocator itself -
the sprint precondition in Item 1 is what fetches). No behaviour change for a
repo with no remote, or a remote that matches local (the common case).

### Item 3: Session-start orientation mentions the fetch

**Priority:** P3
**Effort:** 1

`AGENTS.md`'s "Orientation & Current State" bullet ("re-read LATEST.md and run
`/sdlc-studio status`") gains a third clause: fetch and compare against origin
before trusting local state as current, for any repo with a remote.

---

## Impact Assessment

### Existing Functionality

None removed. A no-remote repo (or a remote already in sync) sees no behaviour
change - the new checks are additive and degrade to no-op.

### Affected Modules

| Module | Impact | Change Type |
| --- | --- | --- |
| `reference-sprint.md` | New "remote-drift" pre-flight step, alongside "Reconcile before plan" | Modified |
| `scripts/sprint.py` | `plan` runs the drift check (warn; `--strict` refuses) | Modified |
| `scripts/next_id.py` | No change to `--remote` itself - already correct | Unchanged |
| `scripts/artifact.py` | `new`/`batch` default to remote-aware allocation when `origin` exists | Modified |
| `AGENTS.md` | Orientation bullet mentions the fetch | Modified |

### Breaking Changes

None - advisory by default (`--strict` opt-in to hard-block), matching the
existing reconcile-before-plan precedent.

---

## Acceptance Criteria

- [ ] `sprint plan` performs `git fetch origin` (skipped gracefully when no `origin` remote) then compares local `HEAD` to `origin/<default-branch>`; when behind, prints commit-count + touched-path overlap with the batch and warns (refuses under `--strict`)
- [ ] A repo with no remote, or local already up to date with origin, sees identical `sprint plan` output to today (no false positives)
- [ ] `artifact.py new`/`batch` allocate via `next_id.py --remote` when an `origin` remote exists, falling back to local-only scanning otherwise
- [ ] `AGENTS.md`'s orientation bullet documents the fetch-before-trusting-local-state step
- [ ] A regression test reproduces this incident's shape: local repo N commits behind a remote that already has a same-numbered CR/story file with different content - `sprint plan` warns before the collision would occur

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| `git fetch` requires network / auth and could hang or fail in a sandboxed/offline agent run | Medium | Medium | Timeout the fetch; on failure, warn "could not check origin drift" and proceed (advisory, never a hard block by default) |
| False positive on a repo that intentionally runs many commits ahead locally before pushing (WIP branch workflow) | Low | Low | The check is advisory (warn, not block) unless `--strict`; a local-ahead-of-origin state is not flagged, only local-*behind* |

---

## Dependencies

None.

---

## Linked Epics

| Epic | Title | Status |
| --- | --- | --- |

---

## Out of Scope

- Automatically rebasing or resolving conflicts - this CR only adds detection and a warning, never an automatic merge/rebase
- Any change to `next_id.py --remote` itself, which already does the right thing

---

## Open Questions

None.

---

## Close Reason

> *Filled when CR is closed*

**Outcome:**
**Rationale:**

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | post-incident: 115-commit local/origin divergence | CR proposed - a stale local clone ran a full sprint (RFC0018 D2/D3) that silently duplicated already-shipped upstream work under colliding artifact IDs; recovered via `git reset --hard origin/main` |
