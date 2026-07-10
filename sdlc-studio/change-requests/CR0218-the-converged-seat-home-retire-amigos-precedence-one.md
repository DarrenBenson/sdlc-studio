# CR-0218: the converged seat home: retire amigos/ precedence, one layout, upgrade offers generation first

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

RFC0028/RFC0021 D2: prerequisite of team generation (Dani, blocking). `persona_resolve` prefers personas/amigos/ over seats/, and every upgraded project carries generic cards there - a generated team would be silently shadowed forever. Converge on seats/ as the runtime home; reconcile the validator layout model, reference-persona-generate Output Format, and the generator write paths in one unit (Sam objection 7); the upgrade flow offers team generation BEFORE, and suppresses, the default-amigo install.

## Acceptance Criteria

- [ ] `persona_resolve` resolves seats/ as the primary project home; a role-claiming personas/amigos/ card is detected and migrated/retired with an explicit report (never silently shadowed), including under --dry-run
- [ ] project upgrade offers team generation before the default-amigo install and suppresses the install when the offer is taken; declining installs defaults as today
- [ ] `check_personas` validates the seats/ and stakeholders/ layout without emitting the persona-layout warning for the generator's canonical output; reference-persona-generate Output Format matches the real write paths

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
