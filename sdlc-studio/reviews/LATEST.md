# Reviews - LATEST (anchor)

<!-- close-status:begin -->
> **RUN-01KYAHY9 closing goal-reached.** The delivery backlog reached zero open units; the v5 cut is built and the sprint is being signed off to Done. **Sign-off is the operator's, ratified** - the two-role gate is satisfied by the delegated adversarial review (evidence) plus the operator's ratification (reviewer of record).
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **The delivery backlog is empty and v5 is cut (build).** Every remaining story is delivered and
> signed off to Done; every bug is Fixed; the discovery CRs derive Complete at this close. The v5
> release is CUT (version 5.0.0 across the four authoritative homes, CHANGELOG cut from 126
> fragments, `release_cut.py` tag guard in place) but NOT yet TAGGED - the tag is the operator's
> final act, gated on `gate --release` green recorded on the exact release commit.

## Where the pipeline is (2026-07-26)

RUN-01KYAHY9 delivered the whole tail of the backlog plus the v5 cut. An independent, fresh-context
adversarial review (RFC0051 / D0059 delegated model) probed the substantive work - the
review-independence machinery, the lane partition, the over-appetite recording - APPROVEd with no
MAJOR findings and no constructible independence bypass, and named four MINOR advisories. Two of
the four were fixed in-sprint (BG0297 duplicate-detection scope, BG0298 fail-safe hazard
direction); two were declined with reason. The operator ratified the close.

## What this run produced

- **The delivery backlog emptied**: 67 units delivered and signed off to Done (48 stories + a bug
  cluster), including BG0284 (review-independence supersession), EP0118 (lane partition), EP0124
  (over-appetite recording), and the plan-surface message renderers.
- **Three dogfooding frictions filed and fixed** rather than worked around: BG0295 (compose
  dry-run gate), BG0296 (mutation gitignored-worktree scan), CR0420/US0432 (gate-budget
  re-declaration).
- **The v5 cut**: `release_cut.py` (changelog cut from fragments + a tag guard that refuses a tag
  unless the pre-tag gate was recorded green on the exact commit), version 5.0.0 everywhere,
  `check_versions --strict` green.

## What the close caught

Three delivered units carried stale or unparseable `Verify:` references (US0347 a `../..` path
pytest cannot parse, US0387 a wrong method name, US0427 a test class that never existed) - each
read as delivered while verifying nothing. Repointed to the real tests. Lesson recorded: run
`verify_ac` at delivery, not only at close.

## Next

- The operator cuts the **v5 tag** on the release commit (`release_cut.py record-green` +
  `tag-check`), after `gate --release` is green.
- **Forward-port** the skill source to the installed copy (`tools/forward-port.sh --yes`).
- **Plan the v5 documentation overhaul** (RFC): the two-backlog model (discovery vs delivery) and
  sprint planning are the headline v5 changes to document.
