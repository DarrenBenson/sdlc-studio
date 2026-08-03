# CR-0498: The close ceremony costs more than the work it certifies: measured at ~32 minutes of gate and 57 process spawns to sign off 19 units

> **Status:** Complete
> **Decomposed-into:** EP0189
> **Priority:** High
> **Type:** enhancement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/templates/reviews/retro.md, .claude/skills/sdlc-studio/scripts/tests/test_root_census.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** RUN-01KYMJEM close: 5 commits, gate-timings.json total [368, 371, 398, 427], 57 critic.py spawns (38 wasted), 3 close attempts, 3 retro validate round-trips
> **Date:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

Measured over the close of RUN-01KYMJEM, a 34-unit run. The ceremony that records what a sprint did cost about 32 minutes of gate across 5 commits, 57 subprocess invocations to record three facts about 19 units, and 3 `sprint close` attempts of which 2 stopped on a refusal. None of it changed a line of shipped code.

FOUR SEPARABLE CAUSES, each with its own remedy.

**1. Late-binding refusals.** `close` runs seven steps and stops at the first unmet prerequisite. It was run three times: stopped on retro content, then on a missing `--principal`, then completed. Each restart re-ran the preceding steps. `preflight` exists to report every prerequisite at once and does - but it cannot validate retro CONTENT before the retro exists, which is exactly the class that refused.

**2. Arguments discovered by failing.** `critic signoff` requires `--author`; `close --apply-signoff` requires `--principal`. Both were learned from a refusal, and the first cost 19 wasted spawns before the message was read.

**3. Per-unit process spawns.** Recording the adversarial evidence, the verdict and the sign-off for 19 units took 57 invocations of `critic.py`, each paying interpreter start, imports and a read-modify-write. 38 of them were wasted on the argument error above.

**4. The gate runs the full suites over a close that touches no code.** Measured relevance of what a close actually writes: a CR body, a bug body, a story body and `reviews/LATEST.md` are all `test-relevant: no`; `retros/VELOCITY.md` and every NEWLY FILED artefact are `yes`. A close is filings plus VELOCITY.md, so BG0383's fast path buys it nothing - the saving lands on mid-sprint body edits, which is not where the cost is. The close had already run `gate --require-retro --require-review: PASS` before the commits that each re-ran 5,006 tests over an untouched script tree.

## Steps to Reproduce

Close a run of ~30 units and count: `sprint close` invocations, `critic.py` spawns, and the
gate seconds recorded in `.local/gate-timings.json`. For RUN-01KYMJEM: 3, 57 and [398, 427] on
the last two commits.

## Proposed Fix

Five changes. D first - it is the largest single saving.

**D. A close-scoped gate profile.** The close changes no code and has already run the full gate
once as step 4 of 7; the commits that follow re-run the suites over an untouched script tree.
Reuse that verdict rather than re-earning it per commit. Worth about 25 of the 32 minutes on
its own.

**E. Let a listing-only declaration name the IDS its structural read depends on**, not just the
directory. `GATE_LISTING_ONLY = ("sdlc-studio",)` becomes structural for the ids the census
actually names and irrelevant for every other new file, which makes filing an artefact free -
and filing is most of what a close does. Keep the fail-safe direction: a declaration naming no
ids stays structural for the whole tree exactly as now, so the narrowing is opt-in and a module
that gets it wrong is slower rather than wrong.

**A. `close --dry-run`** runs all seven steps against a scratch copy and reports EVERY refusal
in one pass, retro content included. Converts three serial round-trips into one.

**B. Batch forms on `critic evidence|record|signoff`:** `--from-run` reads the open batch,
`--units` takes a list. 57 spawns become 3, and an argument error costs one refusal rather than
nineteen.

**C. The retro scaffold emits a template that PASSES `retro validate` once filled:** the
carried-set shape and the `fixed-in:` / `declined:` disposition vocabulary demonstrated, not
merely named in a refusal.

## Impact

A ceremony more expensive than the work it certifies is one people learn to skip, and this project's whole argument rests on it not being skipped. The gate budget lane went OVER during this close - 427s against a 380s ceiling, +35% on the 2026-07-26 baseline - so the cost is now visible in the tool's own reading rather than only in wall-clock. The close is also the moment an operator is most tired and least willing to absorb three serial four-hundred-second round-trips, which is when a `--no-verify` starts to look reasonable.

## Acceptance Criteria

- [ ] `sprint close --dry-run` reports every unmet prerequisite of all seven steps in one read-only pass, retro content included, and writes nothing.
- [ ] The adversarial evidence, the verdict and the sign-off can each be recorded for a whole batch in one invocation, with the open run as the default scope.
- [ ] A required argument missing from a batch invocation is refused once, before any unit is written, naming every argument the command needs.
- [ ] A retro created by the scaffold and filled in as the template demonstrates passes `retro validate` without a rejection round-trip.
- [ ] A close-phase commit that touches no script, template or tool reuses the gate verdict the close itself earned, rather than re-running the suites.
- [ ] The close reports its own cost - gate seconds and elapsed - so the next reduction is measured against a number rather than an impression.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | Claude Opus 5 | Raised |
| 2026-07-29 | Claude Opus 5 | Steps and Proposed Fix RESTORED. Both were supplied at filing and silently discarded: `file_finding`'s CR renderer has only Summary, Impact and Acceptance Criteria, so a `fix` or `steps` field for a CR reaches nothing. That is BG0384's class still live in the other filer - `artifact.py` now lands an unhomed field, `file_finding.py` does not. Filed separately. |
