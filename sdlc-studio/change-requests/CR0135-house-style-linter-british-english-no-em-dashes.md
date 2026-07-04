# CR-0135: house-style linter: British English, no em-dashes, no jargon (validate checks structure, not prose)

> **Status:** Proposed
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py (new lane or sibling), .claude/skills/sdlc-studio/reference-outputs.md, .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/help/
> **Depends on:** -

## Summary

AGENTS.md states house style as hard rules - **British English** (analyse, colour, behaviour),
**no em-dashes** (en dash with spaces or restructure), **no corporate jargon** (synergy, leverage,
robust). But nothing enforces them. `validate.py check` validates artefact *structure* (status
vocab, unfilled placeholders, links, personas) and `.markdownlint.json` covers Markdown mechanics -
neither reads prose for style. So the rules rely entirely on the author remembering, and an agent
that has never internalised them will violate them silently.

Observed in the field (this session): filing CR-0131 and the sibling CRs, I introduced em-dashes
throughout, and only caught them because I happened to grep for `—` after the fact - by hand. A
zero-em-dash convention that every existing file honours (verified: 0 em-dashes across the committed
reference set) is exactly the kind of bright-line rule a deterministic linter should hold, not an
honour system.

Proposed: a house-style lane that flags the bright-line violations, advisory by default and
promotable to a gate.

1. **Em-dash** (`—`) anywhere in artefact prose - a hard fail (the rule has no exceptions; the
   linter suggests the ` - ` / en-dash-with-spaces fix inline).
2. **Americanised spelling** from a small, high-signal list (analyze/behavior/color/-ize where the
   project is -ise, etc.) - flagged with the British form suggested.
3. **Banned jargon** from the AGENTS.md list (synergy, leverage, robust, ...) - flagged.
4. Runs over `sdlc-studio/**` artefacts + the skill's own docs; scoped to changed files in the
   pre-commit / release-gate path so it is cheap. Fixes are *suggested*, never auto-applied to
   prose (an autofix for em-dash-to-` - ` may be offered behind an explicit `--fix`).

The banned-word and spelling lists are project-configurable (a project may permit "robust" in a
security context); the em-dash rule is universal to the house style. Honest degrade: a file it
cannot parse is reported un-checked, never passed.

## Acceptance Criteria

- [ ] a style lane flags em-dashes in artefact prose with the ` - ` fix suggested; zero false
      positives on code fences / literal ` - ` / en dashes already spaced
- [ ] Americanised spellings and banned-jargon terms are flagged from project-configurable lists,
      with the British / plain alternative suggested (remediation-with-finding, per CR-0025)
- [ ] runs scoped to changed artefacts (cheap enough for a pre-commit / release-gate lane); advisory
      by default, promotable to a gate via config
- [ ] an optional `--fix` applies only the unambiguous em-dash-to-` - ` rewrite; spelling/jargon stay
      suggestions (never silently rewrite an author's prose)
- [ ] unit tests: em-dash caught, code-fence dash not caught, spelling flagged, configured-permit
      suppresses a term, unparseable file reported un-checked not passed
- [ ] `reference-outputs.md` + `help/` document the lane; `templates/agent-instructions.md` points
      consuming projects at it so the house-style rules are enforced, not just stated
- [ ] `CHANGELOG.md` `[Unreleased]` entry ([[LL0004]])

## Out of Scope

- A full grammar / prose-quality linter (this is bright-line house-style rules only).
- Auto-rewriting spelling or jargon (suggested, not applied - prose is the author's).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Created via `new` (deterministic) |
