# BG0144: The grooming gate accepts an Affects naming files that do not exist, and silently sizes the unit from nothing

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Effort:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Points:** 3
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

CR0260 refuses a unit that declares no `Affects`. BG0136 made the filer demand one. Neither checks that the declared paths RESOLVE. A unit can therefore be groomed against a FICTIONAL file list, and every downstream consumer treats it as sized.

Proved end to end. A bug filed with `--affects .../totally-invented-file-that-does-not-exist.py`:

1. the filer ACCEPTS it (no existence check);
2. `sprint plan` PASSES it as groomed (the breakdown gate checks the field is present and parseable as a path list, never that the paths are real);
3. the planner forecasts it at exactly 50,000 - the flat floor - because an unresolvable path yields complexity 0.

That flat floor is precisely the "unlabelled fallback" the breakdown gate own refusal message complains about: "without Affects the planner cannot size it (the complexity seed is 0, so its forecast collapses to a flat floor nobody labelled as a fallback)". The gate shuts the front door and leaves this window open. A declared-but-fictional Affects is INDISTINGUISHABLE, downstream, from a well-sized unit - it is strictly worse than an absent one, which at least gets refused.

It also defeats the shared-file cluster detection, which is the other half of what Affects is for: two units that both name a mistyped path will never be seen to collide with the real one.

This is not hypothetical and it is not rare. TWO bug reports filed in a single day carried invented paths - BG0137 named the archive sub-index `_index.md` when it is `<type>.md`, and BG0138 named `TS0001-core-artifact-lifecycle.md`, which does not exist. Both were caught by the human doing the work, never by a guard. An agent filing findings at speed will assert paths from memory, and nothing currently stops it.

## Steps to Reproduce

1. python3 scripts/`file_finding.py` file --type bug --severity Low --effort S --title x --summary y --steps z --fix w --affects "scripts/totally-invented-file.py" -> filed, no complaint. 2. Put that id in a worklist and run sprint.py plan --worklist ... -> NOT refused; planned. 3. Read the forecast: ~50,000 tokens, the flat floor, because the path does not resolve to a file and the complexity seed is 0. The unit is "groomed" and sized from nothing.

## Proposed Fix

The grooming predicate must require that at least one declared `Affects` path RESOLVES to a real file, and it must live in the one shared definition (sprint.breakdown) that BG0136 already made both the filer and the planner call - so the filer refuses a fictional path at the moment the author can still fix it, and the planner refuses one that has since been deleted or renamed. Be careful about the honest exceptions and state them: a path to a file the unit will CREATE cannot resolve yet and is legitimate, so a unit whose paths ALL fail to resolve is the error, not one where some do. Report the unresolvable paths by name either way - a typo the author can see is a typo the author will fix.

## Acceptance Criteria

### AC1: a unit whose declared Affects paths ALL fail to resolve is refused, naming them

- **Given** a unit declaring only `Affects` paths that do not exist on disk (a fictional/typo list)
- **When** the shared grooming definition (`sprint.breakdown`) scores it
- **Then** it is `ungroomed`, and the unresolvable paths are named so the author can fix the typo; a unit with at least one resolving path (plus a greenfield file it will create) still grooms
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_bug_regressions.py::AffectsResolveGroomingTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
| 2026-07-15 | sdlc-studio | Fixed: grooming requires at least one Affects path to resolve; all-unresolvable is refused and named. Fixture ripple migrated (real files created in test fixtures). |
