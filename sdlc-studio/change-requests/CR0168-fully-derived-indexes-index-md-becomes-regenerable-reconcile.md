# CR-0168: Fully derived indexes: _index.md becomes regenerable reconcile output, never an input

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0012](../epics/EP0012-distributed-artefact-identity-schema-v3.md)
> **Priority:** High
> **Type:** Enhancement
> **Raised-by:** Dani Okafor (Engineering amigo)
> **Depends on:** none (foundation tranche)

## Summary

`_index.md` files become fully regenerable output of `reconcile`, never inputs. Neither
humans nor agents may hand-edit them, and a CI guard fails on manual index edits.

## Motivation

With concurrent agent writers the norm (trunk-based development, parallel worktrees), the
index file is the second collision surface after id allocation (RFC0024 removes the first).
Two agents appending index rows in separate worktrees conflict on merge even when their
artefacts do not. The doctrine already says the index is derived and reconcile syncs it
(LL0001: reconcile from a file census, not from the existing counts; CR0164 made apply add
missing rows mechanically). This CR finishes the thought: if reconcile can regenerate every
row from the artefact census, the index is a build artefact, hand edits are drift by
definition, and merge conflicts on `_index.md` disappear because either side can be thrown
away and regenerated.

## Scope

**In scope**

- `reconcile.py` gains full index regeneration: every `_index.md` (bugs, CRs, RFCs, epics,
  stories, test-specs) is rebuilt from the file census, including summary tables and archive
  pointers.
- All writers stop hand-authoring rows anywhere outside `artifact.py`/`reconcile.py`;
  `artifact.py new` may still append its own row for immediate visibility, but regeneration
  must reproduce it byte-identically.
- A CI guard (repo `tools/` plus the portable `gate.py`) that fails when an `_index.md` diff
  is not reproducible by regeneration (regenerate, compare, fail on mismatch).
- Documentation: SKILL.md deterministic entry points and `reference-reconcile.md` state the
  rule as absolute for humans and agents alike.

**Out of scope**

- Index archival policy (exists: `archive.py`, CR0160); regeneration respects archive
  pointers, it does not change them.
- Derived views beyond `_index.md` (status dashboards already recompute).
- Merge tooling; the fix is regenerability, not a merge driver.

## Acceptance Criteria

- [ ] `reconcile.py regenerate` (or `apply`) rebuilds every index byte-identically from a
      clean census; running it twice is a no-op (idempotency test).
- [ ] A hand-edited index row is detected by the CI guard and by `reconcile detect`, with a
      message naming the offending row and the regeneration command.
- [ ] A simulated two-worktree merge conflict on `_index.md` resolves by regeneration with no
      information loss (test fixture).
- [ ] `artifact.py new` rows and regenerated rows are byte-identical (round-trip test).
- [ ] Doctrine text updated; `agent-instructions.md` template tells consuming-project agents
      the index is read-only output.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| RFC0024 / CR0167 | Sibling foundation work; regeneration must handle both id eras during migration, so land in the same release |
| CR0174 | The consolidated lint consumes this CR's "index untouched by hand" check |

## Effort

**M.** Reconcile already owns census logic and row insertion; the new work is full-file
regeneration, idempotency proof, and the CI guard.

## Risk

Regeneration that is almost-but-not-quite byte-stable would make every reconcile run a noisy
diff and train agents to ignore index changes. The idempotency AC is the defence (LL0010:
validate the defence with the bug it defends against - the fixture includes a real historical
hand-edit).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Full scope drafted; formalises what reconcile half-implies today |
