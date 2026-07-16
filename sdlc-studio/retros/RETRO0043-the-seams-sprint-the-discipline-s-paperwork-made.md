# RETRO-0043: The seams sprint: the discipline's paperwork made tool-carried

> **Date:** 2026-07-16
> **Batch:** US0186, US0187, US0188, US0189, US0190, US0191, US0192, BG0177 (EP0056-EP0062, from CR0307/0308/0309/0315/0316/0317/0327 + BG0177)
> **Goal:** done (run RUN-01KXPA4N; Sprint Goal: "Make the ceremony seams tool-carried: the discipline's paperwork costs zero improvisation" - judged ACHIEVED via goal-verdict)
> **Delivered:** 8 / 8   **Blocked:** 0
> **Reviewer of record:** Darren Benson (operator) - signed off 2026-07-16 against the embedded decision brief (deliveries, critic REJECTs + repairs, gate/mutation/cost evidence - the CR0318 rule, honoured manually pending CR0323); adversarial passes by the Dani Okafor and Sam Eriksson seats (11 reviews)

## Delivered

- **US0186 (5pt) - the review close.** `review_prep.py close --rv [--latest-body]` stamps
  review-state.json and derives LATEST.md from the dated record - refusing without one.
- **US0187 (3pt) - refine seeds ACs.** Request criteria become story AC scaffolds verbatim
  (callable replacement after the critic's template-expansion catch); `--no-seed-acs` opts out.
- **US0188 (5pt) - changelog fragments.** Per-unit `changelog.d/` entries, compose-and-consume,
  release gate refuses strays. Dogfooded mid-sprint: every later unit's entry was a fragment.
- **US0189 (3pt) - critic brief + from-verdict.** The review ceremony's scaffolding emitted and
  parsed deterministically; its own review used the brief it generates.
- **US0190 (1pt) - shared test loader.** One authority for the script-import incantation, with a
  foreign-cache identity refusal.
- **US0191 (3pt) - parent-aware minting + rfc resolve.** `--parent` wires both link directions
  inside the mint's lock; `resolve` does section-scoped decision-row surgery.
- **US0192 (1pt) - verify_ac --story takes an id.** The natural first invocation works.
- **BG0177 (2pt) - rfc decide fixed.** ws from real children; decided-awaiting-delivery reads
  DECIDED, never READY.

## Blocked / deferred

- Nothing blocked. CR0307/0308/0309/0315/0316/0317/0327 Complete; EP0056-EP0062 Done.

## What went well

- **The tools reviewed themselves into shape.** US0189's critic ran from the brief US0189
  generates; its verdict was recorded through the parser it ships. Five later units' changelog
  entries were fragments (US0188's convention) - zero hold-back dances this sprint after three
  the sprint before.
- **Seven of eight units drew REJECT or blocking-grade findings, all real:** the git-history
  replacement-template expansion (a criterion containing a backslash corrupted the minted
  story), the CLI `--parent` silently dropped while API tests stayed green, `resolve` editing a
  body table, four verdict-parser holes, two VACUOUS "killing tests" the reviewer executed the
  mutants against, the MC-style provenance-tag style breaks, and a repair note that overclaimed
  an import cleanup. Every repair carries a test the reviewer verified kills its mutant.
- **First Sprint Goal judged at close** (US0183's machinery, one sprint after it shipped):
  goal-verdict ACHIEVED, recorded on the run state and displayed by the report.

## What was hard / what stalled

- **API overload (529s) stalled the critic cadence twice**; implementation continued while
  units held short of Done, and resume-by-message recovered every review. The
  implement-ahead/review-behind reordering worked but cost sequencing care.
- **Blind bulk edits misfired twice** (a replace landing in `meta_new` instead of `new`,
  breaking 15 test modules until repaired; a `_section` list/str contract misread). Both were
  caught by the suite within minutes - but both were self-inflicted by editing without reading
  the surrounding code first.

## Lessons

- A reviewer must execute the mutant, not admire the test: two "killing tests" in one unit were
  proven vacuous by running the actual mutants (wrong section targeted, wrong sort order) - a
  test that cannot fail its mutant is the false-assurance class with a green badge.
- Text that flows into `re.sub` is data, never a template: the same replacement-expansion class
  surfaced twice in one sprint (AC seeding, and historically the -G fix) - callable replacement
  is the house rule now.
- A CLI flag is only shipped when a test exercises the CLI path: API-level tests stayed green
  while `--parent` was silently dropped at the argparse mapping - every new flag needs one
  main()-path test.

## Estimate vs actual

**Were the estimates any good?** The plan forecast 575,000 tokens (23pts x 25k seed, plausible
287k-1,305k). Interactive sprint: per-unit actuals unrecorded; the harness-tracked total is
awaited from the operator (`retro.py accuracy --id RETRO0043 --tokens N --write`) - reported as
**not-yet-captured**, never unknowable. Subagent spend alone (11 seat reviews across 8 units,
including 5 REJECT-repair cycles) measured 820,944 tokens - summed exactly from the harness's
per-subagent usage reports, and already 1.43x the point forecast before the unmeasured main-loop
share. The review-heavy shape repeats RETRO0042's pattern and blew the +/-50% honesty band.

## Actions raised

| Finding | Disposition |
| --- | --- |
| Mutation sampler mis-scoped AGAIN (multi -p patterns do not union; whole-diff targets vs narrow suite) - second occurrence after RETRO0042 declined it as one-off | declined: still operator error, but now documented twice - file a CR on the third occurrence per the retro's own rule |
| Refusal exit codes differ across module conventions (file_finding=1, rfc/resolve=2) | declined: each matches its module's established contract; a repo-wide exit-code convention is CR0234's (uniform CLI grammar) existing territory |

## Close loop (gated)

`gate --require-retro RETRO0043` (this retro's id, file form) fails until all four are true:

- [x] this retro exists AND passes its content check (`retro.py validate --id RETRO0043`)
- [x] its lessons are in the project store (`retro.py extract --id RETRO0043`)
- [x] open lessons re-validated (`lessons revalidate`)
- [x] `retros/LESSONS-SUMMARY.md` regenerated (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: not-yet-captured in full (subagent share 820,944 measured exactly from per-task usage reports; the main-loop share is invisible from inside the session - CR0278's case - so the harness total awaits the operator) · Duration: single interactive session 2026-07-16 night · Critic rejects: 4 REJECT->APPROVE cycles (one twice-rejected) + 3 APPROVE-with-blocking-grade-findings-fixed; 7 of 8 units repaired under review · Mutation: changelog 23/25, critic 21/25, rfc 21/25 killed (scoped per module)

## Handoff

- [HO-0002](../handoffs/HO0002-the-seams-sprint-delivered-8-8-next-cr0314.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | Sprint close: 8/8 delivered, Sprint Goal achieved, lessons + dispositions recorded |
| 2026-07-16 | Darren Benson (operator) | Reviewer-of-record sign-off against the decision brief; operator's ~160k figure identified as the context meter, not spend - harness cumulative total still awaited (CR0278) |
