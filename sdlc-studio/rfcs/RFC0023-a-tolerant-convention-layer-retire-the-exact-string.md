# RFC-0023: a tolerant convention layer - retire the exact-string classification gates as a class

> **Status:** Accepted
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Author:** Claude (cross-project dogfooding)
> **Consolidates:** CR0153, CR0154, CR0155 (and the earlier CR0141/CR0144 table-parser family)

## Summary

One real consuming project adopting the skill tripped **three** false gates in a single sprint,
each the same shape: a check locates or classifies a file by an **exact string**, and a legitimate
project variation is silently mis-read. The point fixes are filed (CR0153/54/55); this RFC asks
whether they should instead be retired as a *class* by a shared, tolerant convention layer, rather
than patched one call site at a time until a fourth instance appears.

## The pattern (evidence)

| Filing | Site | Exact string expected | Legitimate variation that failed | Symptom |
| --- | --- | --- | --- | --- |
| CR0153 | `reconcile.py` status-column detect | header cell `== "status"` | `Effective Status` | 302 false `status-mismatch` |
| CR0154 | `sdlc_md.artifact_files` companion skip | stem endswith `-consultations` | `-decisions` companion | false `no-status` + `duplicate-id` |
| CR0155 | `audit._bug_underspecified` | `## proposed fix` / `## steps to reproduce` | `## Fix (proposed)` / `## Symptom`+`## Root cause` | `0/6 ready`, all "underspecified" |
| (write-path) | `artifact.py new --type bug` scaffold | emits the skill's `templates/core/bug.md` | project's house template (`## Symptom`/`## Root cause`/`## Fix (proposed)`) | scaffold is mis-shaped, then CR0155's audit *rejects the scaffold it just wrote* |

The last row is the **write-path sibling of CR0155**: `artifact.py new` scaffolds the *skill's* bug
template regardless of the project's house template, so a consuming project gets a mis-shaped file
that the audit (read-path) then flags - a closed loop of the same convention gap. The tolerant layer
must therefore cover **template resolution** too: `new`/`batch` should scaffold the project's declared
template (a `conventions.templates` entry, Option A) or fall back to the skill default. It is not just
a read-time matching problem; the write side plants the mismatch.

Related, older: CR0141 (product_reconcile's `repo:featureid` token shape), CR0144 (per-parser
table-boundary detection). The through-line: **the skill encodes one house convention as a literal,
and every consuming project whose equally-valid convention differs gets a false negative** - often
across several checks at once (CR0154 hit two; CR0153 hit a whole index). The failures are also
*loud and misleading* (302 mismatches, 0/6 ready), pushing an operator to "fix" healthy artifacts to
satisfy the checker rather than the reader (the same backwards incentive as CR0147).

## Design options

- **Option A - config-declared conventions.** A `conventions:` block in `sdlc-studio/.config.yaml`:
  `status_column`, `companion_suffixes`, `bug_ready_sections: {repro: [...], fix: [...]}`, etc., each
  defaulting to today's literal for back-compat. A project declares its vocabulary once; every check
  reads from the one place. Explicit, greppable, no guessing. Cost: a growing config surface, and a
  project must know to set it (though the CR0153 diagnostic - "found header X, expected Status" - can
  point them at the knob).
- **Option B - normalised / semantic matching.** Checks match on a normalised form (case-fold, strip
  punctuation and parentheticals, word-set rather than word-order) and a small synonym set
  (`symptom`+`root cause` ~ repro; `fix (proposed)` == `proposed fix`). Zero project config. Cost: the
  fuzziness can re-introduce the very false-*positive* the exact match was chosen to avoid (reconcile's
  exact `status` guards against scavenging `Dependency Status`) - so each relaxation needs a guard.
- **Option C - a shared classifier helper.** One `is_artifact(path)` / `status_cell(header)` /
  `section_present(text, kind)` layer that all of reconcile/validate/audit/next_id call, so the
  convention lives in exactly one place (Options A and/or B implemented behind it). This is the
  structural half regardless of A vs B - it is the CR0144 "one shared iterator" lesson applied to
  classification, not just table parsing.
- **Option D - do nothing; keep patching per site.** Defensible if the instances stay rare, but three
  in one session from one project suggests the next consumer finds a fourth.

## Recommendation

**C as the structure, A as the default policy, B where a synonym is unambiguous.** Put a single
classification layer in `lib/` (C) that reads a `conventions` config (A) and falls back to normalised
matching for safe, unambiguous cases (B, e.g. word-order-insensitive `fix (proposed)`), keeping the
existing exact guards where a relaxation would scavenge (the `Dependency Status` case). Each of
CR0153/54/55 then becomes a thin adoption of the shared layer rather than a bespoke fix, and a fourth
variation is a config line, not a fourth CR.

## Open decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Config-declared (A) vs normalised (B) vs both behind a shared layer (C) as the primary mechanism | Resolved: C structure, A primary, B where unambiguous |
| D2 | Do CR0153/54/55 land as point fixes now and refactor onto the layer later, or wait and do them through the layer once? | Resolved: CR0153 point fix now; CR0154/CR0155 through the layer |
| D3 | Where a relaxation risks a false-positive (the `Dependency Status` scavenge), is the guard per-site or centralised in the layer? | Resolved: per-site (existing exact guards stay) |
| D4 | Does this warrant a diagnostic-first stance generally: when a whole-file/whole-index parse yields nothing, name the convention mismatch (CR0153) rather than emit N per-row findings? | Resolved: yes (CR0153 degenerate-parse diagnostic) |

## Decision

Accepted (decisions.md D0010; operator at sprint planning, 2026-07-05): build the tolerant
convention layer - **Option C** structure (one classification layer in `lib/`), **Option A**
config-declared conventions as the primary policy, **Option B** normalised matching only where
unambiguous. CR0154 and CR0155 land as thin adoptions through the layer; **CR0153 lands now as a
diagnostic point fix** because it diagnoses rather than matches. **D3** is resolved **per-site**:
the existing exact guards (the `Dependency Status` scavenge) stay where a relaxation would misfire,
rather than being centralised. **D4** is resolved **yes** - the diagnostic-first stance is adopted
(name the convention mismatch instead of emitting N per-row findings). The build is the sprint
2026-07-D tranche (decisions.md D0011): the layer in `lib/` read via the shared config reader, with
CR0154/CR0155 as its adopters.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | Claude (cross-project dogfooding) | Created via `new` (deterministic) |
| 2026-07-04 | Claude (cross-project dogfooding) | Drafted from three same-session dogfooding gates (CR0153/54/55, +CR0141/44 lineage): propose a shared tolerant convention layer (config + normalised match behind one classifier) to retire the exact-string-gate class. |
| 2026-07-04 | Claude (cross-project dogfooding) | Added the write-path sibling: `artifact.py new` scaffolds the skill template not the project's, so the scaffold fails CR0155's audit - the tolerant layer must cover template resolution, not just read-time matching. Found executing a sprint (filing BG0143). |
| 2026-07-16 | sdlc-studio | Wrote the accepted outcome back (per decisions.md D0010/D0011): D1-D4 marked Resolved with their dispositions and a Decision section added - the RFC now records the acceptance instead of four Open rows predating it |
