# CR-0112: Strip internal provenance tags (CR/BG/RFC) from consuming-facing docs + shipped code

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

The skill embeds its own change-request ids as provenance tags pervasively: ~199 in reference-*.md + help/*.md and ~224 in scripts/*.py comments. A consuming agent reads these workflow docs while running its OWN project, whose CR/BG namespace collides with the skill's - so (CR0110) in a skill doc can be misread as the project's CR0110. Operator decision: STRIP the CR/BG/RFC tags from consuming-facing docs AND the shipped Python comments. Traceability stays where it belongs - the skill's change-requests/, CHANGELOG, and git blame. Keep US/EP examples and the skill's own artifacts (change-requests/CHANGELOG/rfcs/reviews) untouched.

## Acceptance Criteria

- [ ] CR/BG/RFC#### tags removed from reference-*.md, help/*.md, templates/**, and scripts/*.py (comments) - grammar kept clean; US/EP examples and code blocks preserved
- [ ] the skill's own artifacts (change-requests/, CHANGELOG.md, rfcs/, reviews/) keep their ids - that is the provenance home
- [ ] a guard (lint-style.sh or a checker) flags a bare (CR|BG|RFC)#### in reference/help/scripts so the convention does not creep back; documented in best-practices/claude-skill.md
- [ ] lint + gate green; CHANGELOG entry under [3.1.0]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
