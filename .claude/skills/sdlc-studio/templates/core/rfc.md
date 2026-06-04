<!--
Template: Request For Comments (design exploration)
File: sdlc-studio/rfcs/RFC{NNNN}-{slug}.md
Status values: See reference-outputs.md (Draft / In Review / Accepted / Superseded / Withdrawn)
Related: help/rfc.md, reference-rfc.md
Use an RFC (not a CR) when the design space is UNSETTLED – multiple viable options,
open decisions, or cross-cutting/cross-repo impact that must be agreed before any
change is committed. An accepted RFC SPAWNS CRs (its workstreams); it does not
itself get actioned into epics.
-->
# RFC-{{rfc_id}}: {{title}}

> **Status:** {{status}}
> **Priority:** {{priority}}
> **Author:** {{author}}
> **Date:** {{date}}
> **Spans:** {{repos_and_components}}  <!-- e.g. backend-api (providers, adapters) + web-client (UI) -->
> **Related:** {{related_rfcs_crs_epics}}
> **Supersedes / Superseded by:** {{supersession}}

## Summary

{{one_paragraph_what_and_why}}

## Context & Problem

{{what_prompted_this_what_need_or_pain_it_addresses_what_changed}}

## Goals / Non-Goals

**Goals**
- {{goal}}

**Non-Goals**
- {{explicit_non_goal}}

---

## Design Options

### Option A – {{option_a_title}}
**Approach:** {{description}}
**Pros:** {{pros}}
**Cons:** {{cons}}
**Effort / risk:** {{effort}}

<!-- Add Option B, C… one heading each. Every RFC should weigh at least two. -->

---

## Recommendation

{{leaning_with_rationale_or_"TBD – pending the Open Decisions below"}}

## Open Decisions

> The unsettled cores – the reason this is an RFC. Each must resolve before the
> dependent workstream can be built. List owner + how it gets resolved (consult,
> spike, operator call, threat model).

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | {{decision}} | {{options}} | {{owner}} | {{consult / spike / operator}} | Open |

---

## Architecture Impact

| Layer / System | Impact | Change Type |
| --- | --- | --- |
| {{layer}} | {{impact}} | New / Enhancement / Replacement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| {{risk}} | {{likelihood}} | {{impact}} | {{mitigation}} |

---

## Phased Plan / Workstreams

> How this decomposes into CRs once accepted. Each workstream becomes one (or a
> few) CRs that reference back to this RFC. Sequence + dependencies here.

| WS | Workstream | Repo | Becomes | Depends on |
| --- | --- | --- | --- | --- |
| WS1 | {{workstream}} | {{repo}} | CR (TBD) | – |

---

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** {{accepted_option | superseded | withdrawn}}
**Rationale:** {{why}}
**Spawned CRs:** {{cr_links}}

---

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| RFC/CR/EP | {{id}} | {{title}} | {{status}} | parent / sibling / workstream / supersedes |

> **Cross-repo note:** if this RFC spans repos (e.g. backend-api + web-client),
> the spawned CRs are filed in BOTH and cross-referenced. Numbers are per-repo –
> confirm the next free number against `origin/main` before filing (see
> reference-cr.md cross-repo guard).

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| {{date}} | {{author}} | RFC drafted |
