# CR-0142: Retire product_reconcile - a traceability gate that never told the truth

> **Status:** Complete
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** scripts/product_reconcile.py (deleted), scripts/tests/test_product_reconcile.py (deleted), reference-pvd.md, reference-scripts.md, help/pvd.md, help/references.md, help/help.md, templates/core/pvd.md, EP0008, RFC0015 (WS3 note), CR0049 + US0034 (superseded), CR0141 (superseded)
> **Supersedes:** CR0141, CR0049, US0034

## Summary

`product_reconcile.py` (shipped by CR0049 / US0034 as RFC0015 WS3) is removed. Its job was
cross-repo feature-map traceability: every product feature `PF####` in the master PVD should
trace to real work in its owning repo. Dogfooding it against the first real multi-repo PVD
showed it had **never once produced a true trace** - and its test suite hid that.

Two findings, together, made retirement the honest call rather than a fix (CR0141):

1. **It never worked on a real PVD.** The parser needs a whole table cell matching a bare
   `repo:featureid` token; real trace cells cite the landing artefact in prose
   (`crew:CR-0157 (Done) · CR-0126 (Done)`). So it parsed **0 of 11** features and exited 0 with
   only a non-blocking `empty-feature-map` warn - green on an unparseable map. And the resolver
   only looks in `prd.md`, but a CR-driven SDLC declares features in `docs/changes/` /
   `change-requests/` and only summarises them in the PRD once shipped, so it could not see
   in-flight work at all.
2. **Its green tests gave false confidence.** All 12 unit tests fed it synthetic clean tokens
   (`repo-a:F0007`) - a format the real artefact never uses - so they passed while the tool was
   inert in practice. That is the exact assertion-integrity / mutation-check anti-pattern this
   repo's own CR0131-0134 exist to kill: a test that pins a shape reality does not have.

**Why retire, not fix (CR0141):** the value left after removing the wrong assumptions is thin.
For a single-author, few-repo product the ~11-row feature map is read every `review` cadence
anyway, and judging whether a feature is real / in the right repo is a judgement call, not a
regex. The coordination win from the exercise that surfaced this was **projection + drift**
(`pvd sync` / `pvd drift`), which works and is independent of `product_reconcile`. A tool that
has never told the truth is not worth 135 lines plus eight doc touchpoints of maintenance.

## What changed

- **Deleted:** `scripts/product_reconcile.py` + `scripts/tests/test_product_reconcile.py`.
- **De-referenced:** `reference-pvd.md` (workflow step 5), `reference-scripts.md` (its section),
  `help/pvd.md`, `help/references.md`, `help/help.md`, `templates/core/pvd.md` - all now point at
  `pvd sync` / `pvd drift` + the `review` cadence for feature-map integrity.
- **RFC0015:** WS3 marked retired (WS1/WS2 - the PVD + `pvd sync`/`drift` - stand).
- **CR0049 + US0034:** Superseded (they shipped a tool now withdrawn; the ship fact is preserved).
- **CR0141** (the proposed fix): Superseded - the tool is retired instead of fixed.

## Acceptance Criteria

- [x] `product_reconcile.py` + its test removed; `grep -rn product_reconcile .claude/skills` returns
      nothing (no dangling reference in the shipped payload).
- [x] Every user-facing surface (help, reference, template) describes the PVD toolset as
      `pvd create` / `pvd sync` / `pvd drift` only; feature-map integrity is a `review`-cadence job.
- [x] `pvd.py` (sync/drift) untouched and green - retirement breaks nothing that worked.
- [x] CR0049, US0034, CR0141 carry a Superseded banner pointing here; RFC0015 WS3 noted retired.
- [x] The script test runner + `gate.py` green after removal.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | Claude (cross-repo coordination) | Created via `new` (deterministic) |
| 2026-07-04 | Claude (cross-repo coordination) | Retired product_reconcile: deleted tool + test, de-referenced across help/reference/template, superseded CR0049/US0034/CR0141, noted RFC0015 WS3 retired. Rationale: never produced a true trace, green tests hid it, superseded by pvd drift + the review cadence. |
