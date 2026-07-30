# CR-0503: an adversarial review can be run outside the seat ceremony, losing every standing practice, and nothing detects that it was

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/help/review.md, .claude/skills/sdlc-studio/templates/agent-instructions.md, AGENTS.md
> **Date:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (operator-directed, from the US0484-US0485 close); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`critic.py brief --unit --seat` assembles a seat-framed review prompt and refuses to issue one missing any of the standing practices: the claim inventory over all four prose surfaces, per-item CLOSED/OVER-CLAIMED/MOVED repair verdicts, mutate-the-author's-TESTS, isolation re-testing of a surviving mutant, regression cover for every repair, and two reviewers per round on distinct lenses. `critic.py evidence --from-verdict` then parses the returned VERDICT/ISSUES/BLOCKING block into the ledger so no verdict is hand-transcribed. All of that discipline is shipped, mechanical, and completely optional. Observed on 2026-07-30 closing an 11-unit 47-point batch: the author spawned five generic subagents with hand-written briefs instead. Every standing practice above was absent from those briefs - no claim inventory, no repair-verdict rule, no mutate-the-tests demand, no isolation rule, one reviewer per lens-group - and because the returned text is not in the parsed contract, recording it would mean the AUTHOR retyping findings about their own work into the evidence ledger, which is the exact hand-transcription the tooling exists to prevent. Nothing refused it, nothing warned, and the resulting evidence row would be indistinguishable from one produced by the ceremony.

## Impact

Who: every project relying on the two-role gate, and every operator reading an evidence row as proof an independent adversarial pass happened. What breaks: the gate's central claim. A verdict recorded from outside the ceremony carries none of the practices each of which exists because a real defect escaped without it - and the ledger cannot tell the two apart, so the weaker pass inherits the stronger one's authority. The failure is silent and it is most likely exactly when it matters most: an author closing their own batch reaches for the generic agent tool because that is what is in front of them, not the verb three files away.

## Acceptance Criteria

- [ ] An evidence or verdict row records HOW it was obtained, and a row not produced through `critic.py brief` is marked as such rather than being indistinguishable from one that was - the provenance is the enforcement half; without it every rule below is prose.
- [ ] `brief` gains a review KIND along`--seat`, and each kind emits a prompt carrying the standing practices: unit-closing, repair re-review (the existing `--rejoinder`), sprint-level full-diff, design/plan, audit-lens and security. A kind with no template is refused by name, never silently served the unit-closing prompt.
- [ ] The refusal `critic.py` already applies to a brief missing a standing practice is extended to every new kind, proven by a test per kind that strips one practice and asserts the brief is refused - so a new kind cannot ship a weaker contract than the one it joins.
- [ ] A round run with ONE reviewer, or with two on the same lens, is recorded as such - the review record already owes this and no code enforces it.
- [ ] The agent-facing instructions (AGENTS.md and the shipped `agent-instructions.md`) name the seat path as the only supported route to an adversarial review, so an agent reaching for a generic subagent is departing from a stated rule rather than filling a gap in one.

## Recommendation

The provenance marker is the load-bearing half and should land first: without it, this CR is a set of rules with the same enforcement the bypassed ones had. Two candidate mechanisms, both cheap - `brief` emits a nonce into the prompt that `--from-verdict` requires back, or `evidence` refuses a `--findings` string when the same unit has no brief issued in the run. The kind templates are the operator's explicit ask and should be authored from the review kinds this repo already performs rather than invented: the six named above are all attested in `reference-review.md` or in the run records. Worth checking during refine whether `sprint-review` needs its own assembled brief - it has a record verb and no brief, which is the same shape of gap one level up.

## Evidence

**It recurred the same day, after being filed, in the hands of the agent that filed it.** Closing
RUN-01KYPZ1G a few hours later, the author again spawned generic subagents with hand-written briefs
across seven reviewers, and again nothing refused, warned or recorded the departure. The operator
caught it by asking. That is the second attestation in one day, and the more useful one: filing a
practice does not install it, which is the whole premise of this CR restated by its own author's
behaviour.

Diffing the shipped brief against the hand-written one that replaced it makes the loss concrete:

| Shipped `brief --seat` carries | The hand-written brief had |
| --- | --- |
| The seat charter, resolved and adopted as a role | an invented lens description |
| The canonical ACs verbatim, marked "judge against THESE, not a paraphrase" | the author's paraphrase of the findings |
| Diff scope resolved from the unit's own `Affects` | "glob by id prefix" |
| The CLAIM INVENTORY pass, run FIRST, across all four prose surfaces | nothing |
| `--rejoinder`: prior verdict quoted verbatim, re-execute-your-probes contract | a hand-rolled, weaker version of the same idea |
| The VERDICT/ISSUES/BLOCKING contract `--from-verdict` parses | a bespoke contract nothing can parse |

The claim-inventory omission is the costly one. That pass is the only thing in the ceremony aimed at
prose, and "prose promising what no code implements" is one of the five recurring defect classes
CR0504 names from the batch immediately before this one. Replacing the brief removed the single
practice targeting a class known to be live in the very code under review.

Two mechanisms are also confirmed, since the second occurrence exercised them:

- The bespoke return contract has exactly the cost predicted above. Recording those findings means
  the author retyping conclusions about their own work into the evidence ledger, because
  `--from-verdict` cannot parse a contract it did not issue.
- `sprint-review` still has a record verb and no brief, so the sprint-level review - the one that
  actually clears the coverage gate - has no assembled prompt at all. The Recommendation flags this
  as worth checking; it is confirmed, not open.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (operator-directed, from the US0484-US0485 close) | Raised |
| 2026-07-30 | Claude Opus 5 (operator-directed, from the RUN-01KYPZ1G close) | Second attestation recorded: the same bypass recurred hours after filing, in the same session, and was caught by the operator rather than by any lane. Brief-content diff and two confirmed mechanisms added. |
