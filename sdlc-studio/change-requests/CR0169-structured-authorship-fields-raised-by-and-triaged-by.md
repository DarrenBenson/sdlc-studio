# CR-0169: Structured authorship fields: raised_by and triaged_by as typed references

> **Status:** Complete
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0013](../epics/EP0013-structured-authorship-and-policy-enforcement.md)
> **Priority:** High
> **Type:** Enhancement
> **Raised-by:** Dani Okafor (Engineering amigo)
> **Depends on:** none (foundation tranche)

## Summary

`raised_by` and `triaged_by` become structured frontmatter references, not bare strings:
`name`, `type` (one of `human`, `persona`, `agent`), and `version`. Persona documents are
the resolver today; agentic entities later, with no schema change.

## Motivation

Personas raise and write artefacts today (this CR is itself persona-raised), but authorship
is recorded as free text (`Created-by: sdlc-studio new`, revision-history author strings,
`Requester:`). The persona model will later be swappable for full agentic entities;
if authorship is structured now, that swap is a resolver change, not a schema migration and
not a rewrite of history. The audit trail cannot credibly be rewritten later, which is why
backfill of existing artefacts is an acceptance criterion, not a nice-to-have. Authority
modelling beyond separation of duties (CR0170) is explicitly deferred past this version.

Prior art this builds on: RFC0016/RFC0017/RFC0020/RFC0021 established the persona and seat
model; CR0151 added seat-score provenance; CR0165 flags a critic reviewer that is no declared
seat. This CR gives all of that a single typed representation to point at.

## Scope

**In scope**

- Frontmatter schema: `raised_by: {name, type, version}` and `triaged_by: {name, type,
  version}` on bugs, CRs, RFCs, and stories; `type` enum is `human | persona | agent`.
- Resolver: `name` resolves against the persona library (`personas/`, amigos included) for
  `type: persona`; against git identity for `type: human`; `agent` is reserved and
  validates but does not resolve yet.
- `artifact.py new/batch` and `file_finding.py` take `--raised-by` (structured) and write the
  block; `transition.py` records `triaged_by` on the triage transition (vocabulary lands in
  CR0173).
- Backfill script: every existing artefact (including archives) gains a `raised_by` block
  inferred from existing Requester/Created-by/revision-history fields, marked
  `inferred: true` where the source was ambiguous. Existing prose fields are left in place;
  the structured block is additive.
- `validate.py` checks presence and shape on new artefacts.

**Out of scope**

- Any permission or authority semantics (CR0170 carries the single separation-of-duties
  rule; broader authority matrices are deferred past this version).
- agentic-entity resolution, identity lifecycle, or credentials.
- Renaming or removing the human-readable Requester/Created-by lines.

## Acceptance Criteria

- [ ] New artefacts carry structured `raised_by`; `validate.py` fails a bare-string author on
      a schema-v3 artefact.
- [ ] `type: persona` names must resolve to a persona document; an unresolvable name is a
      validation error naming the persona library path.
- [ ] Backfill has run over every existing artefact in this repo, including archived ones;
      ambiguous attributions are marked `inferred: true`; zero artefacts left without a
      `raised_by` block.
- [ ] Swapping the resolver (persona to a stub agent resolver) requires no frontmatter
      change on any artefact (test proves the seam).
- [ ] `reconcile detect` and index regeneration are unaffected (fields are frontmatter-only).

## Dependencies

| Artefact | Relationship |
| --- | --- |
| RFC0024 / CR0167 | Sibling foundation work; backfill and migration should run in one schema-v3 pass so consuming projects touch history once |
| CR0170, CR0171, CR0174 | The enforcement layer consumes these fields; they block on this CR |

## Effort

**M.** Schema plus resolver are small; the backfill over full history with credible
inference is the bulk.

## Risk

A sloppy backfill would poison the audit trail at birth: an artefact confidently attributed
to the wrong author is worse than one honestly marked inferred. The `inferred: true` marker
and a backfill report (counts per inference rule) are the mitigation.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Full scope drafted; agent-entity swap must be a resolver change only |
| 2026-07-08 | sweep-close (backlog reconciliation) | Delivered via US0060, already Done; CR status was never cascaded to Complete -> closed |
