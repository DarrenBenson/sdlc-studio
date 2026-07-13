# RFC-0031: The scaffold contract: may a creator emit an artefact that cannot pass validation?

> **Status:** Accepted
> **Date:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren; human; v1

## Summary

Split out of BG0108 on 2026-07-13, on the critic's judgement that the residual is a product call rather than a bug fix. BG0108 made every creator emit validator-clean artefacts WHEN GIVEN CONTENT. A content-LESS scaffold (artifact.py new --type story --title x --epic y, no --ac) still emits placeholder / no-ac / evidence-present errors, because there is nothing to put in the acceptance-criteria section. The question is what a creator should do about that, and it cannot be answered inside a bug fix because both cheap answers are dishonest. Answer A - write a TODO into the AC section - was tested and REJECTED on evidence: `validate._unfilled(`'TODO') is False and `conformance._real` uses the identical regex, so a TODO would satisfy the placeholder rule AND silently promote an unspecified story to the 'specified' conformance stage. That is the exact silent-corruption class BG0108 exists to stop. Answer B - refuse to create without content - is coherent and matches `file_finding`'s existing 'refuses to write a hollow artifact' precedent, but it contradicts artifact.py's documented scaffold contract (the agent fills the scaffold's content) and --template full's deliberately-unresolved placeholders, with a wide doc and flow blast radius. The tension is real: a scaffold is BY DESIGN incomplete, and the validator's job is to say so.

## Design Options

- **Refuse at creation: new/batch require the content their type needs (a story needs at least one AC), exactly as they already refuse a story without --epic. Coherent, matches `file_finding`'s precedent, and means 'created' always implies 'valid'. Cost: contradicts the scaffold contract, breaks the two-step create-then-fill flow, and --template full's placeholders lose their point.**
- **Keep the scaffold, and make the validator era-aware about it: a freshly created, never-edited scaffold is a known incomplete state, so validate reports it as a WARNING (not-yet-filled) rather than an error, and escalates to an error once the artefact is transitioned out of its initial status. Preserves the flow, keeps the honesty (it still says the artefact is not filled in), and puts the hard failure at the gate that matters. Cost: the validator needs to know 'freshly created', which is state it does not have today.**
- **Accept the status quo and document it: a content-less scaffold is EXPECTED to fail validation until filled, and that is the validator doing its job. Change nothing in code; amend BG0108's AC and say so plainly in the docs. Cheapest and arguably already true - the objection is only that 'create then immediately validate' reports errors, which is a workflow surprise rather than a defect.**

## Recommendation

Option 3, then reconsider. The critic's own finding is that the validator is RIGHT to complain - an unspecified story IS unspecified, and the value of BG0108's work is precisely that the errors are now honest and limited to genuinely missing content rather than scattered across metadata the creator owned. Option 2 is the attractive one if the surprise proves to bite in practice, but it adds state to the validator for a problem that may be purely one of documentation. Decide after v4.1 is in the field and we can see whether anyone actually trips on it.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Act on this finding or keep status quo | Resolved (D0028): status quo accepted, documented |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | audit | Filed |
| 2026-07-14 | Darren | Resolved status quo (operator decision D0028): a content-less scaffold is EXPECTED to fail validation until filled - the validator doing its job. Making it green would require writing filler into the acceptance-criteria section, which passes validate's no-ac rule AND silently promotes an unspecified story to 'specified' in conformance (the BG0108 corruption class). Documented as expected in reference-scripts-create.md; era-aware validation (warn-until-edited) reconsidered only if it trips someone in the field. No code change. |
