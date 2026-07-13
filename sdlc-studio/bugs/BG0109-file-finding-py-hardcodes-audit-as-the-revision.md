# BG0109: file_finding.py hardcodes 'audit' as the revision-history author, ignoring --author

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Created:** 2026-07-11
> **Created-by:** sdlc-studio file

## Summary

`file_finding.py` writes '| {today} | audit | Filed |' (three hardcoded sites, ~L117/129/139) into Revision History regardless of the --author flag, which is only used in the body context. RFC0029 was filed today with --author 'Claude (Fable 5)' and its history row says 'audit'. Cosmetic until someone audits authorship - then it is a wrong provenance record produced by the provenance tooling.

Scope widened during the fix: every creator carried the same defect - recording an authorship it never resolved - in a different disguise.

- `artifact.py` `_render` wrote `f.get('author', 'sdlc')`: an unattributed `artifact new` recorded the literal 'sdlc' rather than the resolved invoking agent, and a typed `--author 'Name; type; version'` dumped the whole triple into a cell that should carry a name. Its index Author column had the same two faults.
- `triage_noise.py` wrote `| {today} | audit | Consolidation opened |` into the consolidation CR. On schema v3 - the default era - that is the branch EVERY Low-severity finding takes, so it, not the per-type render, was where this bug's own Steps to Reproduce still reproduced after the first fix. BG0109 is itself Low severity.

## Steps to Reproduce

1. `file_finding.py file --type rfc --title X --author 'Someone'`, then open the artefact's Revision History: the author column reads 'audit'.
2. On schema v3, file a **Low**-severity finding with `--author 'Dani Okafor; agent; v2'`: it consolidates, and the consolidation CR's history row reads 'audit' while its own `Raised-by` reads the author. This is the path this bug itself took.
3. `artifact.py new --type cr --title X` with no `--author`: the history row reads 'sdlc'. With `--author 'Dani Okafor; agent; v2'` the cell, and the index Author cell, read the full triple.

## Proposed Fix

Resolve every Author cell from the same authorship the artefact stamps as `Raised-by` (`sdlc_md.authorship_value`, the resolver BG0108 introduced), rendering the name alone. Added `sdlc_md.authorship_name()` as the one formatter all three creators call, so none can drift back to a literal, and routed the history row through `sdlc_md.join_row` so a `|` in a name is escaped rather than shifting the table's columns.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-11 | audit | Filed |
| 2026-07-13 | Dani Okafor | Scope widened to `artifact.py` (same defect, different literal); fixed test-first in both creators |
| 2026-07-13 | Dani Okafor | Rejected by review: the Steps still reproduced through `triage_noise.py`'s consolidation branch (the default era's path for a Low finding, i.e. this bug's own), and `artifact.py`'s index Author column still took the raw value. Both fixed test-first; a prior note here wrongly claimed `triage_noise.py` was owned by another unit - it was clean at HEAD, and that claim is withdrawn |
