# BG-0004: review_prep persona check reads personas.md while the epic cascade reads personas/ directory, so the persona-usage leg silently no-ops

> **Status:** Closed
> **Severity:** Medium
> **Reporter:** Adversarial Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

Persona storage location is contradictory across the skill: review_prep.py reads a single personas.md file while the epic completion cascade and epic step read a personas/ directory, so projects using the documented directory layout get a false all-clear from the deterministic persona-usage check.

## Problem

review_prep.py persona_usage() reads base/'personas.md' (review_prep.py:78), treating H2 headings as persona defs, and reference-outputs.md:30/:237 declare sdlc-studio/personas.md. But the epic completion cascade (reference-outputs.md:701) and epic step (reference-epic.md:331) consult sdlc-studio/personas/ - a directory of persona files. The two layouts are mutually exclusive for the reader. A project following the cascade/epic guidance stores personas as personas/*.md, leaving personas.md empty or absent, so review_prep reports defined=0, unused=0 (nothing to check) while the cascade believes personas exist. The deterministic persona-usage leg of the unified review silently produces an all-clear on exactly the layout the epic workflow prescribes.

## Proposed Fix

Pick one canonical layout and make every reader agree. If both are allowed, have review_prep resolve personas.md AND personas/*.md (H2 headings in the single file, or one persona per file) and have the cascade/epic text reference the same resolver. Document the single chosen convention in reference-outputs.md.

## Evidence

.claude/skills/sdlc-studio/scripts/review_prep.py:78 (personas_md = base / 'personas.md') vs reference-outputs.md:701 ('If personas exist in sdlc-studio/personas/') and reference-epic.md:331

## Impact

The persona-usage review leg gives false confidence on any project using the personas/ directory the epic workflow itself prescribes; defined-but-unused personas go undetected. Quality risk medium.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: determinism) |
