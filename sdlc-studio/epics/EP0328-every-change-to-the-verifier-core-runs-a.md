# EP0328: Every change to the verifier core runs a kit of the hostile runtimes consuming projects have

> **Status:** Draft
> **Derived Point Total:** 7
> **Parent:** CR0675
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0675. Delivers the work CR0675 requested.

## Story Breakdown

- [ ] [US1203: The hostile kit proves the verifier dies with its caller, exits on an interrupt and leaves no orphan](../stories/US1203-the-hostile-kit-proves-the-verifier-dies-with.md)
- [ ] [US1204: The hostile kit proves a batch obeys a consumer's pytest addopts and collects under warnings as errors](../stories/US1204-the-hostile-kit-proves-a-batch-obeys-a.md)
- [ ] [US1205: The hostile kit proves a shallow clone, a non-Claude harness and an over-long token change no result](../stories/US1205-the-hostile-kit-proves-a-shallow-clone-a.md)

## Acceptance Criteria (Epic Level)

- [ ] `scripts/tests/test_verifier_hostile_env.py` imports `verify_ac`, gate and `run_state`, so the existing selection runs it whenever they change, and drives each case through the shipped entry point in a scratch consumer tree.
- [ ] The kit asserts that the verifier dies with its caller's process group, SIGINT exits 130 within seconds, nested callers leave no orphan, a batch obeys the project's addopts -m, collection under filterwarnings = error with a pytest11 plugin equals a fresh pytest --collect-only, the light-tier scope check holds in a --depth 1 clone, results do not change with CLAUDECODE unset and `CURSOR_AGENT` set, and a 300-character token does not crash.
- [ ] Each case fails against a recorded mutant of the defect it models (BG1190's `start_new_session` change, US1112's addopts replacement, US1113's unbounded token).
- [ ] The kit runs in under 30 s with no network access.
- [ ] Before and after: no verifier-core unit in the next two sprints reaches round 2 on an environment the kit models.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
