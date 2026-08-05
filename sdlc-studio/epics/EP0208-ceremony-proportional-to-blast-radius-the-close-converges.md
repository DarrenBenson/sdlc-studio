# EP0208: Ceremony proportional to blast radius: the close converges and the risk band drives the review

> **Status:** Draft
> **Derived Point Total:** 20
> **Parent:** CR0510
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0510. Delivers the work CR0510 requested.

## Story Breakdown

- [ ] [US0638: The close pre-flight runs the retro checklist it is about to be judged on](../stories/US0638-the-close-pre-flight-runs-the-retro-checklist.md)
- [ ] [US0639: Every gate execution the close runs is recorded, so the close cost report is not a fraction of the truth](../stories/US0639-every-gate-execution-the-close-runs-is-recorded.md)
- [ ] [US0640: plan_review honours its own enabled key rather than the schema-version gate](../stories/US0640-plan-review-honours-its-own-enabled-key-rather.md)
- [ ] [US0641: The critic brief tier is derived from the risk band, recorded on the verdict, and read by the coverage predicate](../stories/US0641-the-critic-brief-tier-is-derived-from-the.md)
- [ ] [US0642: A low-band unit gets a bounded brief and the claim-inventory pass runs only at high band](../stories/US0642-a-low-band-unit-gets-a-bounded-brief.md)

## Acceptance Criteria (Epic Level)

- [ ] This CR supersedes CR0451, CR0453 and CR0455, each recorded as Superseded with a pointer here, so the project carries one artefact on its own cost rather than five
- [ ] `triage_noise` consolidation and the session cap are live in this repo through a knob independent of schema version, and a Low-severity finding folds into a themed consolidation CR rather than minting its own artefact
- [ ] `claimed_proof_gaps` is called by the close, and a unit owing mutation proof with no run recorded REFUSES rather than passing green
- [ ] The review tier is derived from the diff, persisted on the verdict and read by conformance, with a test-only change deriving Tier B rather than the no-review tier
- [ ] A reviewer is scoped to the changed hunks, and a defect in untouched code is reported as pre-existing rather than blocking the unit beside it
- [ ] Every finding carries a disposition, only TRACKED mints an artefact, and a trivial correction has a legal path that does not require one
- [ ] The test selection pre-commit computes REACHES the suite runners, so `total.tests` stops reading the full count on every run
- [ ] Re-running the author-retires-their-own-REJECT scenario still fails under the new tiering, proving the lighter process did not lose the defect that justified the heavy one

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
