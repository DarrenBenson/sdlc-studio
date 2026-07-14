# CR-0260: A breakdown step that makes a backlog plannable: Affects, size (bugs too), dependencies, shared-file clusters

> **Status:** Complete
> **Priority:** P2
> **Type:** Feature
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/templates/core/bug.md

## Summary

Planning keeps hitting units that cannot be sized or sequenced, and the gap is closed by hand every time. The `--goal design` rung exists and establishes `Depends on` (and, from a PRD, decomposes to epics+stories), but it does NOT groom an existing CR/bug backlog into a PLANNABLE state. Four things are missing, each hit three times in one session:

1. Units declare no `Affects`, so `complexity.py` cannot size them and they fall back to a flat 50k base - hand-groomed three times.
2. **Bugs have no size field at all**, only Severity (which is priority, not size), so a bug can never be sized even in principle.
3. Nothing detects **shared-file clusters**. The planner knows only declared `Depends on`, so it reported CR0257 and BG0132 as safely parallel when both touch `file_finding.py` - it has produced a wrong parallel wave three times.
4. A CR is never decomposed into stories, so its Done is never gated on executable ACs (only stories carry real verifiers - see BG0132).

Operator's framing: during planning, if something is missing we should add it - either in the plan, or as a distinct breakdown step that turns CRs into epics/stories and adds size, complexity and points to everything, bugs included.

## Impact

Every sprint plan. Today the planner's output is only as good as metadata nobody is required to supply, so it silently under-informs: a flat forecast, a fake-parallel wave, an unsizeable bug. The operator gets a plan that looks authoritative and is not. Closing it also removes the hand-grooming that has preceded every plan this session.

**Effort:** L

## Acceptance Criteria

**The breakdown must be UNAVOIDABLE.** A separate step nobody runs is doctrine, and this session
proved three times what happens to doctrine: the retro gate was satisfiable by `touch`, the review
was advisory so a stale one reached a close, and `--goal design` (which already exists and is
specified to produce "a reviewable, estimated backlog") has never once been run. Enforcement must
live in the command people actually invoke. Nobody runs `design`. Everybody runs `plan`.

- [ ] **`sprint plan` REFUSES an ungroomed batch.** Blocking, non-zero, and it prints NO plan - a
      plan over unsized units is the false-authority this exists to abolish. It names each offending
      unit and what it lacks (`Affects`, size), and names the command that fixes it. A warning is not
      enough: an advisory lane is the one that gets scrolled past.
- [ ] **Validated against the bug it defends (LL0010):** a batch containing one unit with no
      `Affects` must FAIL `plan`, and the same batch must pass once groomed. If it cannot fail, it is
      not a gate.
- [ ] **The escape is explicit and auditable, never accidental.** Following the engagement-floor and
      `lessons.loop` pattern, an operator who knowingly accepts an unsized batch may opt out in
      config; the lane then REPORTS and does not block. Omission is not an escape - only a recorded
      decision is.
- [ ] The planner surfaces **shared-file clusters** as a coordination hint, derived from the
      `Affects` it already parses: units touching the same file are one cluster, not independent
      parallel work. (It reported CR0257 and BG0132 as parallel while both touch `file_finding.py`;
      the wave shape has been hand-corrected three times this session.)
- [ ] A CR is decomposed into stories where the work warrants executable ACs, so Done is gated on
      real verifiers rather than prose (BG0132).
- [ ] (Bugs carrying a size field is **CR0257's AC2** - owned there, not duplicated here. CR0260
      depends on it: the gate cannot refuse an unsized bug until a bug can carry a size.)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
