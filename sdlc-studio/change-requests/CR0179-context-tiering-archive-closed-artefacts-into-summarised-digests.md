# CR-0179: Context tiering: archive closed artefacts into summarised digests to bound token cost

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0018](../epics/EP0018-tooling-hardening-and-review-debt.md)
> **Priority:** Low
> **Type:** Enhancement
> **Raised-by:** Dani Okafor (Engineering amigo)
> **Depends on:** CR0167, CR0168 (land after the schema work ships)

## Summary

Archive closed artefacts into summarised digests so status and planning commands stop
re-reading the full corpus as repos age. Backlog priority: low urgency, raised now so it is
on the ledger.

## Motivation

Token cost creep is the silent failure mode: no single command gets slow enough to notice,
but a two-year-old repo with a thousand closed artefacts pays a growing tax on every
status, hint, and planning pass. Large long-lived repos will hit it first, and by then the
fix is retrofitting. The groundwork exists - RFC0012 established progressive-disclosure
indexes with release archival, CR0160 added the index-bloat advisory, and the first live
archive run cut live indexes from 332 to 83 lines. This CR extends that pattern from index
rows to artefact content: a closed artefact's full text is tier-two context, and commands
should read a digest unless the artefact is specifically opened.

## Scope

**In scope**

- Digest generation at archive time: per archive batch (e.g. per release), a summarised
  digest capturing id, title, outcome, key decisions, and cross-references for each closed
  artefact - enough for planning and dedup checks without opening originals.
- Status, hint, planning, and dedup-oriented reads consume digests for closed artefacts;
  originals remain on disk, untouched and linkable (the audit trail is never summarised
  away, only the default read path changes).
- Digest freshness guard: a digest that no longer matches its census (artefact added to a
  closed archive, alias change from CR0167) is drift that reconcile detects and regenerates,
  same discipline as CR0168 indexes.
- Measurement before and after: tokens read by `status` on this repo's workspace, recorded
  in the CR on delivery.

**Out of scope**

- Summarising open artefacts (active work is always read in full).
- Deleting or rewriting originals; digests are an access tier, not a replacement.
- LLM-quality summarisation debates: v1 digests are mechanical field extraction; prose
  summaries can follow if field extraction proves insufficient.

## Acceptance Criteria

- [ ] Archiving a release batch produces a digest; `status`/`hint` on a fixture repo with
      500+ closed artefacts read digests, not originals (instrumented read-path test).
- [ ] Token cost of `status` on the fixture drops measurably versus full-corpus reads
      (numbers recorded in this CR on delivery).
- [ ] Digests are regenerable and drift-checked by reconcile, byte-stable like CR0168
      indexes.
- [ ] Opening a specific closed artefact by id still resolves to the full original
      (aliases from CR0167 included).
- [ ] No behaviour change for repos below the size threshold (config-gated, default
      threshold documented).

## Dependencies

| Artefact | Relationship |
| --- | --- |
| CR0167 | Blocking: digests key on canonical ids and must resolve aliases |
| CR0168 | Blocking: digests reuse the derived-output-with-drift-check machinery |
| RFC0012 / CR0160 | Prior art extended, not replaced |

## Effort

**M.** Mechanical digest extraction plus read-path changes in a handful of commands, with
the CR0168 regeneration pattern already proven by then.

## Risk

A stale or lossy digest silently misleads planning - the LL0009 failure class (silent
misleading beats loud failure in severity). The reconcile drift check and mechanical (not
interpretive) v1 extraction are the mitigations; anything the digest cannot represent
faithfully stays a full read.

## Delivery measurement (US0104)

Instrumented read-path measurement on a 501-closed-artefact fixture, `status` tallying one
type:

| Read path | Closed originals read | Bytes read |
| --- | --- | --- |
| Full corpus (no digest) | 501 | 59,010 |
| Digest-backed | 0 | 0 |

`status`/`hint` read a closed artefact's status from the filename-keyed digest instead of
opening the original, so the read cost of the closed corpus drops to zero and is bounded by
the digest size rather than growing with history. Below `digests.min_closed` (default 500)
the feature is dormant and behaviour is unchanged. Delivered as US0104 (EP0023).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Full scope drafted; backlog priority, raised for the ledger |
| 2026-07-09 | claude | Delivery measurement recorded (US0104) |
