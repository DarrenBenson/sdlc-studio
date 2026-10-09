# EP0282: An artefact commit runs the cheap tests that read this repository's artefacts before it lands

> **Status:** Draft
> **Derived Point Total:** 14
> **Parent:** CR0617
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0617. Delivers the work CR0617 requested.

## Story Breakdown

- [ ] [US1021: gate.py names and runs the corpus-marked tests that a change under sdlc-studio/ reaches](../stories/US1021-gate-py-names-and-runs-the-corpus-marked.md)
- [ ] [US1022: An artefact commit runs the corpus tests in the commit hooks, names them and their time, and records them apart from the code-commit series](../stories/US1022-an-artefact-commit-runs-the-corpus-tests-in.md)
- [ ] [US1023: The tests guarded to this repository's artefacts carry the corpus marker or a reasoned exemption, the shell-hazard test that turned main red among them](../stories/US1023-the-tests-guarded-to-this-repository-s-artefacts.md)
- [ ] [US1024: The measured corpus readers outside the guarded modules carry the marker or a reasoned exemption, BG0813's test among them](../stories/US1024-the-measured-corpus-readers-outside-the-guarded-modules.md)

## Acceptance Criteria (Epic Level)

- [ ] A commit that changes any file under sdlc-studio/ runs the repository-corpus test modules, or the cheap subset of them, before it lands
- [ ] A commit touching only code still selects by import edges as today
- [ ] The selection names the corpus modules it ran and their time, within the commit budget

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
