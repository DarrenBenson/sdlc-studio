# RFC Workflow Reference

Deep workflow for `/sdlc-studio rfc`. Load with `help/rfc.md`. RFCs capture an
**unsettled** design space and drive it to a decision; an accepted RFC **spawns
CRs** (its workstreams) rather than being actioned into epics itself.

File: `sdlc-studio/rfcs/RFC{NNNN}-{slug}.md` · Index: `sdlc-studio/rfcs/_index.md`
· Template: `templates/core/rfc.md` · Statuses: `Draft / In Review / Accepted /
Superseded / Withdrawn` (see `reference-outputs.md`).

## When to use an RFC vs a CR vs an ADR

- **RFC** — the design is unsettled: ≥2 viable options, ≥1 open decision, or
  cross-cutting/cross-repo impact that must be agreed before committing. The RFC
  is the place options are weighed and decisions are recorded.
- **CR** — the change is already clear; propose it and action it into epics.
- **ADR** (in the TRD) — a decision already made; records context + consequences.
  When an RFC is accepted, record the resulting decision as an ADR in the TRD.

If you find yourself writing "Option A vs Option B" or "open question / TBD" in a
CR, it should have been an RFC.

## `/sdlc-studio rfc` (default)
Ask: create, list, review, accept, close, or help.

## create
1. **Number:** glob `sdlc-studio/rfcs/RFC*.md`, take the next free `RFC{NNNN}`.
   **Cross-repo:** if this design spans repos, confirm the number is free on
   `origin/main` too (see the cross-repo guard in `reference-cr.md`).
2. Copy `templates/core/rfc.md`; fill: Summary, Context & Problem, Goals/Non-Goals,
   **Design Options (≥2, each with pros/cons/effort)**, Recommendation (may be TBD),
   **Open Decisions** (each row: decision · options · owner · how-it-resolves ·
   Open), Architecture Impact, Risks, **Phased Plan / Workstreams** (the CRs it will
   spawn), Related Artifacts.
3. Status **Draft**. Add the index row. Slug ≤50 chars from the title.
4. **Consult is encouraged before In Review:** `/sdlc-studio consult team` (Three
   Amigos) on the options; add a live-fleet consult when the design touches the
   agents themselves (memory `live-agent-consult-mandatory`).

## list
Glob the RFCs, read each `> **Status:**`; print id · title · priority · status ·
author · date. Filters: `--status`, `--priority`, `--author`.

## review
For each RFC:
- **Draft / In Review** older than ~14 days with no Revision-History movement →
  flag "stalled".
- **Open Decisions** with an Open row > 7 days → flag "needs a decision (owner: X)".
- **Accepted** → verify each Workstream row has a spawned CR that exists and links
  back; flag any missing/unlinked.

## accept
Use when the Open Decisions are resolved.
1. Validate status is Draft or In Review and **no Open Decision row is still Open**
   (resolve or explicitly defer-with-reason first).
2. Fill the **Decision** section: chosen option(s) + rationale.
3. **Spawn the workstream CRs** — for each WS row, create a CR (`reference-cr.md`)
   that references this RFC in its header (`> **RFC:** RFC-{{id}}`) and carries the
   workstream's scope. Cross-repo RFCs spawn CRs in each affected repo; confirm next
   free numbers on `origin/main` per repo.
4. Set RFC status **Accepted**; fill "Spawned CRs"; cross-link RFC ↔ CRs.
5. Record the architectural decision as an **ADR** in the TRD (the RFC explored;
   the ADR records the settled decision + consequences).
6. Update the index (counts + Spawned CRs column).

> **Accepted is not terminal.** The RFC remains the living design home its CRs
> reference. Don't delete or archive it.

## close
- **Superseded** — a later RFC replaces it. Set status, point to the replacement in
  "Supersedes / Superseded by", note in Revision History.
- **Withdrawn** — not pursued. Set status, record why in the Decision section.
Update the index either way.

## Reconcile
`reconcile --scope rfcs` (or a full reconcile) audits the RFC index against the
files: per-row status match, missing rows (a file on disk with no index row),
recomputed Summary counts, and Accepted→spawned-CR linkage. See
`reference-reconcile.md`.
