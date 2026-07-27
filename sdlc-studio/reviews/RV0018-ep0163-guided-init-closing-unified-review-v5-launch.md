# RV-0018: EP0163 guided init - closing unified review (v5-launch)

> **Date:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Scope

The EP0163 guided-init epic (US0437-444): the `init guided` onboarding orchestrator in
`scripts/init.py`, the `status`/`hint` precedence surface in `scripts/status.py`, and their tests.
Diff base c5c33d31..acd2726f. Reviewed by an independent adversarial reviewer (fresh context, the QA
seat), independent of the guided-init author, plus the operator as reviewer of record.

## Findings

Adversarial pass probed the project's recurring failure modes: tests asserting a label not a value,
vacuous verifiers, gate-bypass/idempotence holes, greenfield/brownfield classification, the status
precedence branch, non-clobber seeding, malformed-state handling, and per-AC coverage via mutation.

- No MAJOR.
- MINOR (repaired + re-verified, `acd2726f`): the TSD "detected stack" clause was not pinned to
  brownfield (a mutation making it unconditional passed every test) - now asserted; a corrupt or
  shape-invalid `onboarding.json` crashed `status`/`hint` (the mandated orientation path, now a
  reader of that file) - `read_onboarding` now degrades to absent and `init guided` self-heals.
- MINOR (accepted as designed): onboarding can reach "complete" with zero artefacts (`--confirm` is
  the operator's word that the step was done); an abandoned-but-incomplete onboarding nags until
  `--reset` (a resumable checkpoint, with `--reset` the documented escape).
- NIT (fixed): duplicate `Verified` line pair in US0443.

Could not break: idempotent resume, skip-then-resume ordering, `set_stage` name/status validation,
the PRD greenfield/brownfield fork, `_onboarding_hint` fall-through (complete and absent both fall
through), non-clobber seeding, and the US0444 grep verifiers (non-vacuous).

## Verdict

**APPROVE.** No MAJOR survived; the two fixable MINOR findings were repaired and mutation-proven
before sign-off; both suites pass (38 init, 43 status). Operator ratified as reviewer of record on
2026-07-27. Recorded sprint-level review: `reviews/sprint-review-record.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
