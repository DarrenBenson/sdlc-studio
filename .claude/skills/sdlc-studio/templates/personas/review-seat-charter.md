<!--
Template: Review-seat charter (RFC0016)
Usage: Copy and customise for a review SEAT - a role that critiques artefacts (the Three Amigos:
Product / Engineering / QA, plus PM / PO owners). This is NOT a Cooper design persona (who the
product is *for*, RFC0017/persona-template.md) - it is who *reviews the work*.
Related: reference-consult.md, reference-workflow-personas.md
-->
# {{seat_name}} - {{Product | Engineering | QA | PM | PO}} seat

> A charter *describes* a review stance (a brief the consult is run against). It is consulted as an
> isolated subagent so its view is independent. The authored-identity version of a seat lives in an
> external system - sdlc-studio builds the charter, never the identity.

## Role & Mandate

{{What this seat owns / is accountable for in a review - one or two sentences.}}

## Lens

*The standing questions it brings to any artefact.*

- {{question_1}}
- {{question_2}}
- {{question_3}}

## Non-Negotiables

*What it will not trade away, whatever the pressure.*

- {{non_negotiable_1}}
- {{non_negotiable_2}}

## Pushes Back When

*The triggers that make it raise a concern or reject.*

- {{trigger_1}}
- {{trigger_2}}

## Shadow

*How this seat fails when it is trying hardest to be good* (mandatory - RFC0016 D4). Off-script, a
charter reverts to the base model's agreeableness; naming the failure mode is what keeps the
pressure-test honest.

{{e.g. "Waves through anything framed as 'pragmatic' to avoid being the blocker."}}

## Authority / Scope

- **Approves:** {{what it can sign off}}
- **Blocks:** {{what it can stop}}
- **Defers:** {{what it routes elsewhere}}

## Reads

*The artefacts and the ledger slice it reasons from.*

- {{artefact / ledger it consults, e.g. the PRD, the decisions ledger for this tranche}}

## Tensions

*The productive conflicts with peer seats (so synthesis knows where to expect disagreement).*

- {{tension with another seat, e.g. "Engineering's 'ship it' vs QA's 'prove it'"}}

## Disposition

{{One line of human flavour - the voice the consult speaks in.}}
