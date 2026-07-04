# CR-0135: extend the style guard with British-spelling detection (em-dash + jargon already enforced)

> **Status:** Complete
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** Low
> **Type:** Improvement
> **Affects:** tools/lint-style.sh, tools/style-allowlist.txt, .claude/skills/sdlc-studio/reference-outputs.md
> **Depends on:** -

## Summary

> **Root-cause correction (2026-07-04).** First filed as "add a house-style linter" claiming nothing
> enforces the AGENTS.md style rules. That is **wrong**: `tools/lint-style.sh` (run by `npm run lint`
> in CI) already hard-fails on em-dash (U+2014, no exceptions), corporate jargon (with an allowlist),
> and internal provenance tags in consuming-facing files. The em-dash + jargon rules are enforced.
> Rescoped to the one rule that is stated but **not** checked.

The AGENTS.md style requirements list three prose rules: British English, no em-dash, no jargon.
`lint-style.sh` enforces two of them. The gap is **British English** - the guard does not flag
Americanised spellings (analyze/analyse, behavior/behaviour, color/colour, -ize/-ise), so a document
can use American spelling and pass every check.

This CR is a small addition to the existing guard, not a new tool: add a bounded, high-signal
American-spelling detector alongside the em-dash and jargon passes, sharing the same allowlist
mechanism for the rare legitimate exception (a cited product name, an external quotation).

**Self-evidence for the discoverability problem (see CR-0133).** This CR was first written claiming
the linter did not exist, and its own draft shipped two literal em-dashes and several jargon words -
which `bash tools/lint-style.sh` flags in seconds. The author reached for the rule (avoid em-dash)
but not the tool that enforces it, exactly the failure CR-0133 addresses. The strongest argument for
surfacing the toolbox is that the tool went unfound by the very session filing style CRs.

## Acceptance Criteria

- [ ] `lint-style.sh` gains an American-spelling pass over `*.md` (bounded, high-signal list:
      analyze, behavior, color, and the -ize/-ization family where the house form is -ise/-isation),
      printing each offender with the British form suggested and exiting non-zero
- [ ] the pass shares the existing `style-allowlist.txt` mechanism so a legitimate exception (a
      product name, a quotation) can be permitted by line context
- [ ] zero false positives on the current tree (run it over the repo; it must pass clean today, or
      each hit is a genuine spelling to fix)
- [ ] a unit test / fixture: an Americanised spelling is flagged, an allowlisted line is not, a
      British spelling passes
- [ ] `reference-outputs.md` (or the style section it points to) notes British-spelling is now
      checked, not only stated; `CHANGELOG.md` `[Unreleased]` ([[LL0004]])

## Out of Scope

- Em-dash and jargon enforcement (already shipped in `lint-style.sh`).
- A full grammar / prose-quality linter (bright-line spelling only).
- Auto-rewriting spellings (suggest, do not silently change an author's prose).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Created via `new` (deterministic) |
| 2026-07-04 | claude | Root-cause corrected: em-dash + jargon already enforced by tools/lint-style.sh; rescoped to the British-spelling gap. Rewritten to pass the linter (no literal em-dash / jargon). |
