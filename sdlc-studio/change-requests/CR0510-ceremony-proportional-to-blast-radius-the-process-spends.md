# CR-0510: Ceremony proportional to blast radius: the process spends gate-grade rigour on prose-grade changes, and the machinery that would stop it is built and switched off

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/triage_noise.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .githooks/pre-commit, tools/enable-hooks.sh, sdlc-studio/.config.yaml, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-sprint.md, AGENTS.md, .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Date:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The process applies UNIFORM maximum rigour to work whose blast radius varies enormously. A docstring correction receives the same machinery as a gate that fails open: executable criteria, mutation verification, an independent adversarial reviewer, and a rejoinder round on the repair. Roughly 60% of one session's findings were prose-grade defects processed through gate-grade machinery.

Two second-order effects cost more than the direct spend. REWORK SCALES WITH CEREMONY: scope-limitation prose was written one morning and deleted that afternoon when the defect it described was fixed; three duplicate-selector collisions happened because so many criteria were being minted; repeated test-fixture errors happened because so many tests were being written. A lighter process would have produced fewer defects to find. And THE BACKLOG IS GROOMING PASSES, NOT FIXES: every finding becomes an artefact and the filer mints skeleton criteria, so 27 of 29 open bugs carry no real criteria and each needs an unestimated grooming pass before work can start.

Two structural causes, both measured. REVIEWERS JUDGE WHOLE FILES, NOT DIFFS: `critic.brief` scopes a reviewer to the unit's declared `Affects` and `complete_affects` widens it further. RETRO0085 measured the consequence - twelve findings collapsed to one regression on a triage test, and six of the twelve were older than the batch being judged. THE CLAIM-INVENTORY PASS IS A FINDING GENERATOR BY CONSTRUCTION: the brief mandates enumerating every prose assertion across four surfaces and ruling each TRUE, FALSE or UNVERIFIABLE, and `assert_brief_claim_pass` refuses a brief that omits one, so every stale count in a docstring becomes a finding.

The reviews are NOT wrong. The most valuable defect of the session - an author able to delete the REJECT blocking their own work with one appended line - came from a full adversarial pass pointed at the review machinery. A lighter process would not have found it. The fault is that rigour is uniform while blast radius is not.

This project has already diagnosed this problem four times, and this CR supersedes three of those.

- CR0451 (In Progress, High): 30 commits at roughly 295 seconds of gate each, about 148 minutes, against about 35 minutes of delivery. Its own words: the gate cost four times the delivery, and at this cost the discipline is more expensive than the vibe-coding it replaces.
- CR0462 (Complete): a measured 9:1 overhead ratio, about 35 minutes of delivery against roughly 316 minutes of gate, review and re-running, surfaced only because the operator said it felt slow.
- CR0455 (In Progress): 4,624 tests across 121 files against 70 source modules, never reviewed for removal. Tests are added by every unit and removed by nothing. Now 6,174, a rise of 33% in three days.
- CR0453: the plan said one unit owed a unit test. It never said, and re-run 4,624 tests fifty-two times.

Filing a fifth CR on the same subject would be the exact failure being complained about, so this one absorbs them.

The second finding is the more useful one: THE FIXES ARE ALREADY BUILT AND SWITCHED OFF.

- `triage_noise.py` folds Low-severity findings into themed consolidation CRs and refuses loudly at a session cap of 20 filings. It is fully built and fully tested and has never once run in this repo, because it is gated on `is_schema_v3` and this repo pins `schema_version: 2`. It has been hand-rolled instead: BG0463 is literally twenty non-blocking findings bundled by hand, which is what `should_consolidate` does automatically.
- `sprint.claimed_proof_gaps()` compares proof owed against proof given. It is written and tested and has NO production caller. `sprint_report.py` documents the incident it was built for: six units owed mutation proof, zero runs were recorded, and all six reached terminal with both suites green because no lane compared the two sides.
- `critic brief --tier full|light` exists but is cosmetic. It substitutes one sentence into the generated prompt. The tier is never recorded, never read, never checked. The reference claims it is noted in the issues field, but that field is free text nothing parses.
- `route.estimate()` already produces a deterministic 0-100 risk score with bands and a confidence, stamped on every unit at plan time, and NO ceremony gate reads it.
- `review.max_rounds` exists with a default of 3 but is stop-and-ask rather than a refusal.
- `plan_review.py` is a hard, deterministic, risk-proportional gate that cannot be bypassed by `--force`, and is the model to copy. It is also dormant under schema v2.

A constraint any fix must respect: AGENTS.md plus the engagement floor mean fixing without filing is prohibited, so the cheapest legal path for a trivial observation is to file a bug. A filter that refuses a filing without a legal trivial-fix path relocates the friction rather than removing it.

## Impact

Everyone using the skill, and this repo first. Measured over its own artefacts:

- 277 bugs filed in 14 days, 19.8 per day, which is 59% of every bug ever filed in the project.
- 629 acceptance criteria filed in the same 14 days: median 3 per bug, maximum 9 on a Low-severity 2-point bug.
- The commit gate is 557s against a 380s budget. The ceiling has already been raised once, from 120s to 380s, because the old one fired OVER on every commit and the signal had become noise. It is now over again. The unit suites are 86% of that cost.
- One audit run cost 16.77M tokens and 343 agent invocations to file 12 bugs.
- Review rounds recorded on run state are 62% REJECT. Two batches took three rounds and never converged. RUN-01KYPZ1G ran 33.76 hours with 18 review rounds, of which 25.21 hours - 75% of the run - was review.
- Measured tokens per point spans 21,905 to 151,701, a 6.9x range, while the planner forecasts with a single constant of 25,000 at the bottom of it. Plans systematically under-price.

What breaks if nothing changes: the backlog grows faster than it clears, plans under-price by up to 6x, and the gate ceiling gets raised a third time. What breaks if this is done carelessly: the two-role gate, mutation verification on guards, and full adversarial review of anything that gates or decides must all survive, because they are what caught the critical defect.

## Acceptance Criteria

- [ ] This CR supersedes CR0451, CR0453 and CR0455, each recorded as Superseded with a pointer here, so the project carries one artefact on its own cost rather than five
- [ ] `triage_noise` consolidation and the session cap are live in this repo through a knob independent of schema version, and a Low-severity finding folds into a themed consolidation CR rather than minting its own artefact
- [ ] `claimed_proof_gaps` is called by the close, and a unit owing mutation proof with no run recorded REFUSES rather than passing green
- [ ] The review tier is derived from the diff, persisted on the verdict and read by conformance, with a test-only change deriving Tier B rather than the no-review tier
- [ ] A reviewer is scoped to the changed hunks, and a defect in untouched code is reported as pre-existing rather than blocking the unit beside it
- [ ] Every finding carries a disposition, only TRACKED mints an artefact, and a trivial correction has a legal path that does not require one
- [ ] The unit suites run once per push rather than once per commit, and the measured per-commit gate is below the 380s budget without the budget being raised again
- [ ] Re-running the author-retires-their-own-REJECT scenario still fails under the new tiering, proving the lighter process did not lose the defect that justified the heavy one

## Recommendation

All of them, in that order, and land the first and fourth before anything else so the rest is measurable against a quieter baseline.

The sequencing matters more than the content. The switch-on costs almost nothing because the code exists. The gate split is the largest immediate saving and is reversible by deleting one file. Both are independent of the tier work, which is the only part needing real design.

One verification is non-negotiable and belongs in every unit's criteria: re-run the scenario where an author retires the REJECT blocking their own work, and confirm Tier A still catches it. If the lighter process cannot find the defect that justified the heavy one, the tiering is wrong and must be reverted rather than argued for.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Raised |
