# RFC-0012: Progressive-disclosure indexes with release archival

> **Status:** Accepted
> **Priority:** High
> **Author:** Darren Benson
> **Date:** 2026-06-20
> **Spans:** sdlc-studio skill (index conventions, reconcile/status census, an archive helper, templates/indexes)
> **Related:** CR0019 (origin - promoted to this RFC), RFC0002 (the audit flagged token waste)
> **Supersedes / Superseded by:** supersedes CR0019

## Summary

The flat per-type `_index.md` files grow O(n) with the project and are loaded
whole - a real token cost on large projects, where most rows are terminal. Explore
how to keep indexes bounded via progressive disclosure: a lean **active** index
plus **archived** terminal artifacts behind summary rows, loaded on demand.

## Context & Problem

Each artifact type has one flat `_index.md` listing every artifact, loaded whole
for `status`, `reconcile`, and orientation. On real large projects this is
expensive and mostly redundant (measured 2026-06-20):

| Index | consuming repo B | consuming repo A |
| --- | --- | --- |
| `stories/_index.md` | 196 KB (1,726 lines; 888 Done) | 72 KB |
| `change-requests/_index.md` | 376 KB | 124 KB |
| `bugs/_index.md` | 324 KB | 24 KB |

A 376 KB CR index read just to orient is the token waste the skill warns against,
and ~888 of consuming repo B's story rows are terminal `Done` - rarely needed in full.
This was raised as CR0019; it has multiple viable approaches and cross-cutting
impact (reconcile, status, the index template, every project), so it is promoted
to this RFC to weigh them before building.

## Goals / Non-Goals

**Goals**

- Keep the live index **bounded** regardless of project size.
- Keep the `reconcile`/`status` census **correct** without loading every archived row.
- Archive loads **on demand** (progressive disclosure).
- **Backward compatible** - small projects are unaffected until a threshold.
- No loss of traceability or artifact IDs.

**Non-Goals**

- Changing artifact IDs or deleting artifacts.
- Forcing archival on small projects.

---

## Design Options

### Option A - Release-cascade indexes

**Approach:** a top-level `_index.md` of release rows, each pointing to a per-release
sub-index (`index-r2.5.md`). Artifacts grouped by release, hierarchical.
**Pros:** clean by-release navigation.
**Cons:** every release is a sub-index even when small; active work is split across
the current release's sub-index; more files to keep consistent.
**Effort / risk:** Medium / medium.

### Option B - Active/archive split with PD summary rows

**Approach:** the live `_index.md` lists only **active** (non-terminal) artifacts;
terminal artifacts move to `archive/{release}/{type}.md`, represented in the live
index by a **single summary row** (range, headline, status counts, pointer), e.g.
`| EP0023-EP0064 | Release 2.5 - perf + UX | 42 Done | archive/r2.5/epics.md |`.
**Pros:** the live index stays small and is exactly "what is in flight"; the bulk
(terminal rows) collapses to one line each; biggest token win.
**Cons:** needs an archive step at a boundary; the census must sum active + archive
summaries.
**Effort / risk:** Medium / low.

### Option C - Threshold / windowed index

**Approach:** keep the most recent N (or all active) in the index; older terminal
rows auto-collapse by count/age, no release boundary needed.
**Pros:** automatic; no release ceremony.
**Cons:** "recent N" is a weaker grouping than release; summary rows are arbitrary
ranges.
**Effort / risk:** Low / low.

### Option D - Read-time progressive disclosure only

**Approach:** no archival; the agent slices the index (grep/section-read) instead of
loading it whole.
**Pros:** trivial; immediate read-cost win.
**Cons:** does not bound the file, the maintenance cost, or the reconcile cost.
**Effort / risk:** Low / low.

---

## Recommendation

**Option B (structure), auto-triggered by Option C (threshold), grouped by release.**
The live index holds active artifacts plus one summary row per archived release;
archival triggers when the index crosses a size/count threshold, grouped to the
release that closed. `reconcile`/`status` compute the census from active rows plus
the archive summary counts. Adopt **Option D's slice-read now** as a cheap,
independent first win while B is built.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Archival trigger | release boundary / threshold-N / age / on `archive` command **[chosen]** | Operator | explicit operator-run command | Resolved |
| D2 | Archive scope | index rows only **[chosen]** / move artifact files too | Design | rows-only (files stay, links intact); files later | Resolved |
| D3 | Census of archived | parse_index unions archive sub-index rows **[chosen]** / trust summary counts / deep re-validate | Design | union the full archived rows - census exact, not summary-trust | Resolved |
| D4 | Pointer schema | bullet: range + count + archive pointer (not a table row) | Design | bullet so the parser ignores it; counts come from the unioned rows | Resolved |
| D5 | Migration | `archive --type <t> --release <r>` run per type | Design | the archive subcommand is the migration | Resolved |

---

## Architecture Impact

| Layer / System | Impact | Change Type |
| --- | --- | --- |
| reference-outputs.md | Index conventions: active vs archive, summary-row format | Enhancement |
| reconcile.py / status.py | Census over active rows + archive summaries | Enhancement |
| New archive helper | Move terminal rows at a boundary; write the summary row | New |
| templates/indexes/* | Summary-row + archive sub-index templates | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Census drifts if summary counts are stale | Medium | High | archive helper writes counts atomically; `reconcile --deep` audit |
| Archived rows become hard to find | Low | Medium | summary row points at the archive sub-index; IDs unchanged |
| Over-engineering for small projects | Medium | Low | threshold-gated; no archival until it is large |

---

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | Index conventions + summary-row schema in reference-outputs.md | CR (TBD) | D4 |
| WS2 | reconcile/status census over active + archive summaries | CR (TBD) | D3, D4 |
| WS3 | `archive` helper (move terminal rows by release, write summary) | CR (TBD) | D1, D2 |
| WS4 | Slice-read guidance (Option D) - immediate read-cost win | CR (TBD) | - |

---

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** Accepted (full build: WS1-WS4)

**Rationale:** A consuming project needs it at scale (consuming repo B 196KB/376KB indexes; deferral lifted). D1 explicit `archive` command (predictable over auto-trigger), D2 rows-only (files/links intact), D3 census by UNIONing the full archived rows into parse_index (exact, not summary-trust - removes the 'stale counts' risk), D4 bullet pointer (parser-ignored), D5 the command is the migration. Proven read-only at scale on consuming repo B (371 stories / 407 CRs archivable).

**Spawned CRs:** CR0041 (archive.py + parse_index union + conventions), **delivered**.

---

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| CR | CR-0019 | Progressive-disclosure indexes with release archival | Superseded | origin (promoted to this RFC) |
| RFC | RFC-0002 | Adversarial Audit | Draft | the audit flagged index token waste |

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (rfc0012) | Accepted + delivered as CR0041 (full WS1-4; operator: needed at scale, deferral lifted); census by parse_index union (D3) removes the stale-counts risk |
| 2026-06-20 | Autosprint (rfc-decide session) | Decision session 2026-06-20: deferred the archival machinery (WS1-3) - high value only at scale, this repo is small; WS4 slice-read can be picked up anytime. Revisit at an index size threshold. |
| 2026-06-20 | Darren Benson | Promoted from CR0019; weighs cascade vs archive-junction vs threshold vs read-time PD |
