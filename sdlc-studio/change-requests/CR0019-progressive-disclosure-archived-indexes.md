# CR-0019: Progressive-disclosure indexes with release archival

> **Status:** Superseded
> **Priority:** High
> **Type:** Improvement
> **Requester:** Darren Benson
> **Date:** 2026-06-20
> **Affects:** reference-outputs.md (index conventions), scripts/reconcile.py, scripts/status.py, templates/indexes/*, a new archive helper
> **Depends on:** --
> **GitHub Issue:** --
> **Superseded by:** [RFC-0012](../rfcs/RFC0012-progressive-disclosure-indexes.md)

## Summary

The flat per-type `_index.md` files grow O(n) with the project and are loaded
whole - a real token cost on large projects, where most rows are terminal. Keep
**active** artifacts in a lean index; archive **terminal** ones by release behind a
single progressive-disclosure summary row plus an on-demand archive sub-index.

## Problem

Each artifact type has one flat `_index.md` listing every artifact. It is loaded
whole for `status`, `reconcile`, and orientation, and reconciled whole. On real
large projects this is expensive and mostly redundant:

| Index | consuming repo B | consuming repo A |
| --- | --- | --- |
| `stories/_index.md` | 196 KB (1,726 lines; 888 Done) | 72 KB |
| `change-requests/_index.md` | 376 KB | 124 KB |
| `bugs/_index.md` | 324 KB | 24 KB |

A 376 KB CR index read just to orient is the token-waste the skill warns against -
and ~888 of consuming repo B's story rows are terminal `Done`, rarely needed in full.

---

## Proposed Changes

### Item 1: Active vs archived split

**Priority:** High **Effort:** Medium

The live `_index.md` lists only **non-terminal** artifacts (Draft, Ready, In
Progress, Review, etc.). Terminal artifacts (Done, Superseded, Won't Implement,
Deferred, Rejected) are archived. The live index stays small and bounded.

### Item 2: Release archival with PD summary rows

**Priority:** High **Effort:** Medium

At a release boundary, terminal artifacts collapse into a **single summary row** in
the live index, range + headline + pointer:

```text
| EP0023-EP0064 | Release 2.5 - performance + UX | 42 epics, Done | archive/r2.5/epics.md |
```

One row stands in for many artifacts; the detail loads only when needed.

### Item 3: Archive sub-indexes (on-demand)

**Priority:** Medium **Effort:** Low

`sdlc-studio/archive/{release}/{type}.md` holds the full archived rows, loaded only
on demand. An `archive` step (command or `reconcile --archive`) moves terminal rows
at a release boundary and writes the summary row.

### Item 4: Census still correct

**Priority:** High **Effort:** Medium

`reconcile` / `status` read the active index **plus** the archive summaries so
totals and drift detection stay correct, without loading every archived row.

---

## Impact Assessment

### Affected Modules

| Module | Impact | Change Type |
| --- | --- | --- |
| reference-outputs.md | Index conventions: active vs archive, summary-row format | Modified |
| reconcile.py / status.py | Census over active + archive summaries | Modified |
| templates/indexes/* | Summary-row + archive sub-index templates | Modified |
| New archive helper | Move terminal rows at a release boundary | New |

### Breaking Changes

None for small projects (no archive until a threshold/release). Backward compatible.

---

## Acceptance Criteria

- [ ] A large project's live index lists only active artifacts and stays bounded.
- [ ] Terminal artifacts archive behind a release summary row + an on-demand sub-index.
- [ ] `reconcile`/`status` totals and drift stay correct over active + archive.
- [ ] The archive loads only on demand (progressive disclosure).

## Open Questions

- [ ] Grouping key: release vs date vs threshold-N. -- Owner: design
- [ ] Archive the artifact **files** too (into `archive/{release}/`), or only the index rows? -- Owner: design
- [ ] **Promote to an RFC?** This has >=2 viable approaches (release-cascade vs archive-junction vs threshold-collapse) and cross-cutting impact - it may warrant an RFC to weigh them before building.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Raised - flat indexes do not scale (consuming repo B 376 KB CR index); progressive disclosure + release archival |
| 2026-06-20 | Darren Benson | Superseded - promoted to RFC0012 to weigh the design options |
