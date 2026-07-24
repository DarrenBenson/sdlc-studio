# Reviews - LATEST (anchor)

<!-- close-status:begin -->
> **RUN-01KYA8CF closed stopped.** 18 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **RUN-01KYA8CF (Sprint 3a, the design rung) groomed all 18 units and proved a red-now bar of
> pass=0 fail=41.** Goal verdict PARTIAL - the batch was delivered in full, but 13 stories
> created mid-run by four operator rulings are still ungroomed.

## Where the pipeline is (2026-07-24)

Sprint 2 is closed and signed off. Sprint 3a - the design rung - is closed with a **partial**
verdict. Sprint 3b, the delivery rung that empties the backlog, is the next run.

The backlog stands at **~120 non-terminal artefacts**, which is higher than when Sprint 3a was
planned. That is correct rather than a regression: four operator decisions converted RFC0049,
RFC0050, RFC0051 and CR0418 from options into 17 units of real work.

## What Sprint 3a produced

- **18 skeleton stories groomed** - 41 acceptance criteria with Given/When/Then and a
  node-addressed Verify line, all 18 moved Draft to Ready.
- **A red-now ledger: pass=0, fail=41, manual=0.** The behaviour is absent, so every verifier
  can be run for nothing and the counterfactual bar is proved rather than asserted.
- **Four decisions recorded** - D0059 (disclosed delegated sign-off), D0060 (test strategy at
  planning), D0061 (adversarial plan review), D0062 (goal-aware breakdown gate) - each
  decomposed into EP0157-EP0160.
- **Grooming pre-work**: BG0282 split from 13 points into three units; `Affects` derived for 27
  stories.

## What the rung caught

Three of 41 verifiers **passed against unbuilt behaviour**, and all three were the same defect:
a check matching text already in the tree. `check_versions --strict` asserted consistency and
was green at 4.1.0; `grep xrepo` matched a word BG0162 had already written; `grep Primary`
matched the one-Primary-per-interface constraint while the story exists precisely because no
selection method does. A fourth passed after being repaired - a `[^.]*` regex cannot cross the
line break its target sentence contains.

None of these would have been found by reading them. Running every verifier while the behaviour
is absent is the only reliable detector, and it is free exactly once.

## Open decisions

**None outstanding.** Every RFC is Accepted with its D1 row closed. CR0355 is deliberately held
at Proposed until the v5 launch, per its own instruction.

## Next steps

- **Groom US0419-US0431** (13 stories, the decisions' output) before planning 3b, or plan 3b
  knowing 13 of its 64 units are ungroomed.
- **CR0419 first**: the capacity ceiling reads 1M tokens / 8 units against sprints running
  6.7M-8.3M over 19-44 units, so every plan reports OVER BUDGET and the only instrument that
  would catch a genuinely oversized sprint is a constant.
- **BG0290 blocks refining any accepted RFC** - the request carries no ACs to seed from, so
  validate's no-ac error fires on refine's own output.

## Lessons

A verifier that matches text already in the tree proves nothing, and reading it will not tell
you. A wrong diagnosis does not fail loudly - it produces a workaround that fails silently.
Deciding a request is not the same as reducing the backlog.
