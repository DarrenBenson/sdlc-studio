# BG0040: validate personas reports well-formed when personas are nested

> **Status:** Closed
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new
> **Severity:** medium

## Summary

`validate personas` (`validate.check_personas`, `validate.py:341`) globs `personas/*.md` flat and
skips the `seats/` subdir. When a project keeps its personas nested (e.g. `personas/team/`,
`personas/stakeholders/`), the flat glob matches **zero** files, so the check prints "personas look
well-formed." A vacuous pass reads as a real one. During an upgrade the operator spent a whole pass
trusting a well-formed verdict while the personas were nested and unmigrated.

## Steps to Reproduce

1. In a project, put personas under a nested dir (`sdlc-studio/personas/team/*.md`) with no flat
   `personas/*.md` design personas.
2. Run `validate.py personas --root .`. It reports "personas look well-formed" - a pass derived from
   an empty match set, not from inspecting the nested personas.

## Proposed Fix

Make the empty case explicit: when `personas/` exists but the flat glob finds zero design personas
AND nested persona-shaped files are present (or any non-index `*.md` under `personas/**`), do not
return a clean pass - emit an advisory "personas present but not in the flat Cooper layout
(N nested files found); not validated" finding, or scan recursively and validate what it finds.
A pass must mean "inspected and well-formed," never "found nothing to inspect." Unit test: a project
with only nested personas does not get a bare clean pass. Relates to [[BG0041]] (same upgrade, the
detector side of the persona-layout confusion). CHANGELOG.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
