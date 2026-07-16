# RFC-0042: Make the sprint close-down un-skippable: enforce the retro/close-gate mechanically, not just by doctrine

> **Status:** Accepted
> **Decomposed-into:** EP0046
> **Size:** L
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The sprint close-down (retro + lesson extraction + close gate) is MANDATED by doctrine but only ENFORCED when an agent voluntarily runs 'gate --require-retro RETROxxxx'. The normal gate and the pre-commit hook do NOT require a retro, so an agent can transition stories to Done, commit, push and deploy WITHOUT closing the sprint. Observed live on the homelab project: the agent shipped and deployed the fixes and filed the discoveries, then skipped the retro/lesson-extraction/close-gate entirely - doing it only after the operator pushed twice. Doctrine that is not mechanically enforced gets skipped under pressure - the exact reasoning that made the QUALITY gate a pre-commit hook rather than a checklist. The CLOSE gate never got that treatment. The gap is most acute for INTERACTIVE sprints (no runner run-state to close against).

## Design Options

- **A pre-commit/pre-push hook lane that BLOCKS when a delivery unit reached a terminal state (Done/Fixed) and is committed, but no retro's Batch names it - 'sprint close owed: these Done units have no retro' - with a threshold so a single hotfix is not over-ceremonied**
- **A close-OBLIGATION in the run-state: transitioning a story to Done opens an obligation the gate refuses to pass until a covering retro clears it (works for runner runs; needs an interactive analogue)**
- **A soft hint/status nudge only ('N delivered units since the last retro - a close is owed') - discoverable but not blocking**
- **Combination: the soft nudge on hint/status for discoverability PLUS a blocking gate lane on push/release, so the un-skippable enforcement lands where shipping actually happens**

## Root cause (from the homelab agent's own post-mortem)

The homelab agent, asked why it skipped the close, was precise: it "self-certified completion from
memory instead of running the deterministic gate that exists to stop this. SDLC Studio has `gate
--require-retro` precisely because agents skip the retro. I never invoked it. So nothing failed
loudly. I had a control available and didn't run it - which is the exact silent-control failure I'd
just spent the whole sprint fixing (this project's LL0027: a gate belongs in the command people
actually run). I fixed the machines' version of the bug and committed the human version in the same
session." It treated "deployed" as the finish line. The deeper failure mode: the value of this SDLC
is that lessons COMPOUND; a skipped close silently breaks the compounding, and you cannot see it is
broken until much later.

## Recommendation

**Option D + a harness Stop hook.** The homelab agent independently reached the right shape: "wire a
Stop hook via settings.json that refuses to let a sprint-close turn end without the retro gate
passing - so it's the harness enforcing it, not my recall. Same principle as making the check exit
non-zero." So: (1) a **Stop hook** the skill can install that blocks a turn from ending while a
close is owed (a committed delivery unit reached terminal with no covering retro), the un-skippable
layer; (2) a **soft hint/status nudge** ("N delivered units since the last retro - a close is
owed") for discoverability; (3) redefine DONE - a sprint is complete only when `gate --require-retro`
is green and its output shown, never at "deployed". This is the DoD's close clause (see the DoR/DoD
RFC): the close-down is part of the Definition of Done, and a DoD is only real when a gate enforces
it.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Enforcement mechanism | Resolved: option D (soft nudge + blocking lane) plus a harness Stop hook the skill installs; interactive sprints need the same close obligation, not only runner runs |
| D2 | How to detect the "close owed" trigger (Done-transition since last retro vs run-state obligation) | Open - the mechanism detail for the blocking lane |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Filed |
| 2026-07-15 | sdlc-studio | Added the homelab agent's root-cause post-mortem; resolved D1 = option D + a harness Stop hook; noted this is the DoD's close clause |
