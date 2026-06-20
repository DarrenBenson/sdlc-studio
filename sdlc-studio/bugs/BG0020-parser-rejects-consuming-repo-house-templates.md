# BG-0020: shared parser rejects consuming repos' house templates

> **Status:** Fixed
> **Severity:** High
> **Reporter:** agent-crew (live-board feedback)
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

Run against the real agent-crew and agent-bridge boards, `reconcile` and
`conformance` were effectively inoperable: `reconcile detect` reported 447 drift
items (446 false) and `conformance` flagged every story non-conformant - all for
template-shape reasons, not real drift. Five gaps in the shared parser
(`lib/sdlc_md.py` + `reconcile.py` + `conformance.py`), four of them flagged by the
consuming project.

## Steps to Reproduce

1. `reconcile.py detect --scope stories --root ~/code/Engram-Labs-UK/agent-crew` -> 447 drift.
2. `conformance.py check --root ~/code/Engram-Labs-UK/agent-crew` -> every story non-conformant.

## Gaps

1. **`parse_index` latched the Status column from the first table header and never
   re-pinned** - the story index has two layouts (master Status@col3 + ~40 per-CR
   breakdown tables Status@col4), so every breakdown row read Points as its status
   -> Unknown -> 446 false status-mismatches. (Relocated from BG0018's fix, which
   pinned once.)
2. **`extract_field` couldn't read inline metadata** - this repo packs
   `> **Status:** Done · **Epic:** … · **Points:** 5` on one line; the line-anchored
   regex returned None for every non-first field -> "missing decomposed".
3. **`AC_BULLET_RE` rejected checkbox ACs** - house ACs are `- [ ] **AC1** …`.
4. **`VERIFY_RE` required a leading dash** - house uses a standalone `**Verify:**` line.
5. **`conformance` "specified" needed a numbered AC** - house AC sections are often
   prose bullets with no `ACn` id; a populated AC section should count.

## Fix

- `parse_index`: re-pin Status/ID columns at every header row (drop the first-header
  latch); a data row never has a literal "status" cell, so this fires only on headers.
- `extract_field`: match a field at a line start (optional `>`) **or** after a `·`
  separator, capturing up to the next `·` / `**Field:**` / end of line.
- `AC_BULLET_RE`: allow an optional `[ ]` checkbox; `VERIFY_RE`/`VERIFIED_RE`: make the
  leading dash optional.
- `conformance`: a populated `## Acceptance Criteria` section counts as specified.

## Evidence (after fix)

| Board | reconcile drift | decomposed miss | specified miss |
| --- | --- | --- | --- |
| agent-crew | 447 -> **6** (genuine) | ~all -> 12 | ~all -> 75 |
| agent-bridge | -> **3** (genuine) | -> 29 | -> 0 |

The residual `verifiable`/`verified`/`critiqued` non-conformance is a genuine
discipline gap (only 60/577 agent-crew stories use Verify lines; no critic-verdict
records there), not a parser defect. Regression fixtures added for the two-layout
index, inline metadata, checkbox AC, dashless Verify, and prose-bullet AC.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | agent-crew | Reported - parser inoperable on the house template (4 gaps) |
| 2026-06-20 | Autosprint (parser-fix) | Fixed - 5 parser fixes; validated live (447->6 drift); our repo unaffected (21/21) |
