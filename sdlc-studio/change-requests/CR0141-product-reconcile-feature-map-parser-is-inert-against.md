# CR-0141: product_reconcile feature-map parser is inert against CR/RFC-cited PVDs

> **Superseded 2026-07-04 by [CR-0142](CR0142-retire-product-reconcile-a-traceability-gate-that-never.md).**
> This CR proposed *fixing* `product_reconcile` to be artefact-aware. The operator's call was to
> **retire** the tool instead (it never produced a true trace and its green tests hid that), so the
> fix is moot. This record stays as the diagnosis of why it was inert - the reasoning that led to the
> retirement decision.
>
> **Status:** Superseded
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** scripts/product_reconcile.py (`parse_feature_map`, `prd_has_feature`)

## Summary

`product_reconcile.py` is meant to be a standing cross-repo gate: every product feature `PF####`
in the master PVD must trace to a real feature in its owning repo. Dogfooding it against a live
multi-repo PVD (a consuming multi-repo product, five go-forward repos) exposed that it is a **silent
no-op** on the exact PVDs it targets.

Two coupled assumptions defeat it:

1. **`parse_feature_map` needs a whole table cell matching `^[\w.-]+:[\w.-]*\d[\w.-]*$`** - a clean
   `repo:featureid` token with no spaces, brackets or punctuation. Real PVD trace cells cite the
   artifact that actually lands the feature, in prose: `studio:CR-(new, 0.4)`,
   `crew:CR-0157 (Done) · CR-0126 (Done)`, `framework:CR-0005 (schema 3.1.0) · content-hash.js`.
   None match, so **zero** features parse - and the only signal is a non-blocking `empty-feature-map`
   warn while the tool exits 0. A gate that passes green on an unparseable map is worse than no gate.
2. **`prd_has_feature` looks the feature up in `<repo>/sdlc-studio/prd.md`** as a heading or standalone
   table cell. Even if the token parsed, a **CR/RFC id is not a PRD feature id** and does not live in
   `prd.md` - so a cleaned token would flip the finding from silent-pass straight to a spurious
   `orphan-feature` (BLOCKING). The tool assumes PF -> PRD-feature; real products trace PF -> the CR/RFC
   that ships the feature, because that is where the work and its status actually are.

The parser and the resolver both encode "features are declared in prd.md", but a CR-driven SDLC
declares features in `docs/changes/` / `change-requests/` and only *summarises* them in the PRD §3
inventory once shipped. So the traceability check cannot see in-flight work at all.

## Proposed change

Make the trace resolver **artifact-aware**, not prd.md-only, and make an unparseable map fail loud:

1. **Parse richer trace cells.** In `parse_feature_map`, when the dedicated "owning repo" and
   "child feature" columns are present (header-driven), read the child-feature cell and extract the
   **first `repo:ID` token** even when followed by prose/punctuation (`crew:CR-0157 (Done)` ->
   `crew:CR-0157`), rather than requiring the whole cell to be a bare token. Keep the strict form as a
   fast path.
2. **Resolve CR/RFC ids against `docs/changes/` and `change-requests/`**, not only `prd.md`. A trace to
   `crew:CR-0157` is satisfied if that CR file exists in the child repo (any status), mirroring how
   `prd_has_feature` already anchors to a declaration site. Fall back to prd.md for `F####`/`PF####`
   PRD-feature ids. Multiple ids in one cell (`bridge:CR-0435 · CR-0436`) all resolve.
3. **Make empty-feature-map blocking when the PVD clearly has a populated §3 table** (PF rows present
   but none parsed) - that is a parser/format mismatch, not an empty product. Stay non-blocking only
   when there genuinely are no PF rows. Silent green on "rows present, zero parsed" is the trap.

## Acceptance Criteria

- [ ] A PVD whose trace cells read `crew:CR-0157 (Done) · CR-0126 (Done)` parses to >=1 feature; the
      the consuming product PVD (11 PF rows) parses all 11, not 0.
- [ ] A `PF -> repo:CR-XXXX` trace resolves against the child repo's `docs/changes/` /
      `change-requests/` (file exists), and against `prd.md` for PRD-feature ids; a dangling CR id
      raises `orphan-feature`.
- [ ] PF rows present but none parsed -> a **blocking** finding + non-zero exit (was silent warn + exit 0);
      regression test seen to fail before the fix (mutation-checked).
- [ ] `product_reconcile` on the consuming product PVD+manifest exits 0 only when every PF traces; injecting
      a dangling `crew:CR-9999` makes it exit non-zero.

## Notes / provenance

Found while wiring the consuming product Phase-3 standing coordination (five-repo PVD projection + drift).
`pvd drift` is already a working loud gate (exit 1 on a stale projection; read-only projections);
`product_reconcile` was the intended *feature-map* half of the cadence and is the piece that does not
yet bite. Until this lands, treat `product_reconcile` as advisory and rely on `pvd drift` for the
standing seam-check.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | Claude (cross-repo coordination) | Created via `new` (deterministic) |
| 2026-07-04 | Claude (cross-repo coordination) | Filled in from the consuming product Phase-3 dogfooding: parser + resolver both assume PF->prd.md, real PVDs trace PF->CR/RFC, so the check is a silent no-op; propose artifact-aware resolve + fail-loud on unparseable map. |
| 2026-07-04 | claude | Consuming-product name generalised per the neutrality guard (field-report convention) |
