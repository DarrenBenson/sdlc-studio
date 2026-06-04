<!--
Load: On /sdlc-studio rfc or /sdlc-studio rfc help
Dependencies: SKILL.md (always loaded first)
Related: reference-rfc.md (deep workflow), templates/core/rfc.md
-->

# /sdlc-studio rfc — Design Exploration (Request For Comments)

> **Source of truth:** `reference-rfc.md` — detailed workflow steps.

An **RFC** captures an *unsettled* design space — multiple viable options and open
decisions — and drives it to a decision. It sits **before** a CR:

| Artifact | When | Shape |
| --- | --- | --- |
| **RFC** | Design is unsettled — options + open decisions, often cross-repo | Explore → decide |
| **CR** | The change is already clear | Propose → action into epics |
| **ADR** (TRD §) | A decision already made | Record context + consequences |

> Rule of thumb: if you'd write "Option A vs Option B" or "open question", it's an RFC. An **accepted RFC spawns CRs** (its workstreams); it is never actioned into epics directly.

## Quick Reference

```text
/sdlc-studio rfc                        # Ask what to do (interactive)
/sdlc-studio rfc create                 # Draft a new RFC
/sdlc-studio rfc list                   # List RFCs
/sdlc-studio rfc list --status draft    # Filter by status
/sdlc-studio rfc review                 # Review RFC ages + open decisions
/sdlc-studio rfc accept --rfc RFC-0001  # Record the decision + spawn/link CRs
/sdlc-studio rfc close  --rfc RFC-0001  # Supersede or withdraw
```

## Actions

### create
Draft a new RFC from `templates/core/rfc.md` into `sdlc-studio/rfcs/RFC{NNNN}-{slug}.md`, add a row to `sdlc-studio/rfcs/_index.md`. Captures: problem/context, goals/non-goals, **≥2 design options** (with pros/cons/effort), **Open Decisions** (the unsettled cores, each with an owner + how-it-resolves), architecture impact, risks, and a phased workstream plan. Status starts **Draft**.

### list
List RFCs; filter `--status {draft|in-review|accepted|superseded|withdrawn}`, `--priority P1`, `--author`.

### review
Flag RFCs needing attention: Draft/In Review older than ~14 days with no movement; Open Decisions unresolved > 7 days; Accepted RFCs whose spawned CRs don't exist / aren't linked back.

### accept
Promote an RFC whose Open Decisions are resolved: fill the **Decision** section (chosen option + rationale), set status **Accepted**, and **spawn the workstream CRs** (one per WS row) cross-linked back to the RFC. Cross-repo RFCs spawn CRs in each repo — confirm next free numbers against `origin/main` first (see `reference-cr.md`).

### close
Set **Superseded** (point to the replacing RFC) or **Withdrawn** (record why). Update the index.

## Lifecycle

```text
Draft → In Review → Accepted ──(spawns)──▶ CRs → Epics → Stories → … → ADR (decision recorded)
            │
            ├──▶ Superseded   (replaced by a later RFC)
            └──▶ Withdrawn    (not pursued)
```

## Output

- **RFC file:** `sdlc-studio/rfcs/RFC{NNNN}-{slug}.md`
- **Index:** `sdlc-studio/rfcs/_index.md`

## See Also

- `reference-rfc.md` — workflow detail (REQUIRED for this workflow)
- `/sdlc-studio cr help` — the promotion target
- `/sdlc-studio trd help` — architecture context; record the final decision as an ADR in the TRD
- `/sdlc-studio consult team` — Three Amigos (+ live-fleet) review of design options before `accept`
