# RFC-0039: The discovery track: Issue, refine and triage - a discovery backlog feeding delivery, worked in parallel

> **Status:** Draft
> **Decomposed-into:** EP0035
> **Size:** XL
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

This sprint split the backlog into DISCOVERY (RFC/CR requests) and DELIVERY (epic/story/bug work), dual-track, with gates that keep them apart (plan refuses a request, status shows both, reconcile flags an accepted-but-unrefined request, terminal status derived from children). This RFC extends that into a full discovery track. (1) Add an ISSUE as the defect-side discovery item (operator-confirmed Option A): an Issue is a raw report/symptom, triaged into bugs (or a story/CR if it is really a change); a bug stays the concrete, reproducible DELIVERY unit it is today. (2) Add two ceremonies as first-class commands - refine (a CR/RFC -> epics/stories) and triage (an Issue -> bugs/stories) - both writing the Parent/Decomposed-into links the US0120 primitive verifies, both the place where questions get answered. (3) The pay-off is PARALLELISM: one person refines/triages the discovery backlog ahead while another delivers the current sprint(s); the gates shipped this sprint are what make that safe to run concurrently. (4) Bake the Three Amigos personas (engineering/product/qa seats) fully into refine, triage and review, so clarification and independent review are done BY the seats. (5) Update all documentation, help and README around these concepts. Likely ABSORBS RFC0037 (triage ceremony) and builds on RFC0021 (seats/amigos converge).

## Design Options

- **Issue as a new discovery type (RFC/CR/Issue discovery; epic/story/bug delivery); refine + triage as first-class commands; `is_request` generalises to `is_discovery`**
- **Alternative rejected: bug becomes the discovery item and a new 'fix' is the delivery unit - rejected because bug is already a good, deeply-wired delivery unit and Issue is the real-world intake term**

## Recommendation

Option A (Issue as discovery item; bug stays delivery). Decompose this RFC into CRs per area: (a) Issue type + vocab + `is_discovery`; (b) refine command; (c) triage command; (d) persona/Three-Amigos integration into refine/triage/review; (e) documentation/help/README rewrite (coordinate with CR0272, the command-surface cleanup).

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Act on this finding or keep status quo | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Filed |
