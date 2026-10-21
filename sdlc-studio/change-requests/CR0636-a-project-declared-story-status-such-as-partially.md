# CR-0636: A project-declared story status such as `Partially Done` is always read by the release gate as a completion claim, and no config can declare it non-terminal, so a project must misdescribe a partly-built story as `In Progress` to get its unbuilt criteria out of the red count

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Date:** 2026-10-12
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-12T11:22:32Z

## Summary

A consuming project declares `Partially Done` in .config.yaml (and its register gate accepts it). `gate._claims_completion` deliberately asks the BASE vocabulary, so a declared status falls to the fail-closed branch and claims completion (gate.py ~1197-1215; the docstring explains why: a project's `Shipped` must not silently drop red criteria). That protects one direction but leaves no route for the other: US0413 had AC1-AC3 built and AC4/AC5 never built (filed as a bug and scheduled). Set to `Partially Done`, its two unbuilt criteria stay in the corpus red count and fail the release gate; the only base status that does not claim completion and fits is `In Progress`, which says work is under way when it is not. Found in a consuming project's run, RUN-01M4QTY2 (2026-10-12).

## Impact

Partly-delivered stories are either counted as red regressions or recorded with a status that misstates their state.

## Acceptance Criteria

- [ ] A project can declare an extended status as not claiming completion in .config.yaml; the release gate then lists that story's failing criteria as unbuilt, and an undeclared extended status still fails. The stories refine writes carry the executable checks.

## Triage

- Confirmed by the code path the filer cites: `gate._claims_completion` asks the base vocabulary, so a project-declared status falls to the fail-closed branch and claims completion; nothing in config can declare it otherwise. Deliberate in one direction (a project's `Shipped` must not drop red criteria), missing in the other.
- Private project name generalised. A request, not yet a unit: `refine` sizes it. Not in the first 6.2 run.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Refine needs: one story, Points 3
- Criteria split in two on the story: declared non-completing lists as unbuilt (pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_declared_status.py::DeclaredStatusTests::test_declared_non_completing_status_is_unbuilt); undeclared still red (…::test_undeclared_extended_status_fails_closed)
- Affects adds changelog.d/<story>.md and help/gate.md or reference-config for the new key
- Persona: Maya Okafor

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Raised |
| 2026-10-12 | Claude Opus 5.5 (triage) | Triaged: confirmed from the code path; project name generalised |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
