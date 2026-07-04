# BG0042: persona_resolve ignores existing review seats so authored seats are shadowed by generic defaults

> **Status:** Closed
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new
> **Severity:** high

## Summary

`persona_resolve.project_card` (RFC0020) looks for a project practitioner override at exactly one
path: `sdlc-studio/personas/amigos/<seat>.md`. It never looks at `personas/seats/`, where a project's
hand-authored RFC0016 review seats live (the "Three Amigos" - Sarah/Marcus/Priya etc.). So a project
that has invested in rich, role-matched seats has them **shadowed**: the resolver skips straight to
the generic shipped defaults (Dani/Sam/Lena). The "most-specific-first" guarantee the RFC promises is
broken precisely where the project is most specific. The amigo template even says "a richer
project-authored practitioner persona overrides this default" - but the resolver cannot see the place
those personas actually live.

## Steps to Reproduce

1. A project with review seats at `sdlc-studio/personas/seats/` (engineering/qa/product roles) and no
   `personas/amigos/` overrides.
2. `persona_resolve.py resolve --seat engineering --render build --root . --path-only`.
3. It returns the skill default amigo card (Dani), not the project's engineering seat - the authored
   seat is invisible to delegation framing.

## Proposed Fix

Extend the resolution chain so an existing review seat counts as the practitioner override. Map
`seat (engineering|qa|product) -> the project's seat card` by reading each seat charter's declared
role (not by filename, since seats are named Sarah/Marcus/Priya), and resolve order:
`personas/amigos/<seat>.md` (explicit amigo) > the role-matched `personas/seats/*.md` > skill default >
generic. This is the resolver half of the seats-vs-amigos duality; the upgrade half is [[CR0120]]
(enrich seats in place rather than installing a parallel set).

**[[RFC0021]] Accepted (Option B) settles the model and binds this fix - it is RFC0021 slice 1:**

- The resolver keys on a **declared `role:` field** on the seat card, never parsed H1 prose or
  filename (Engineering refinement - prose scraping is non-deterministic at the boundary). Resolve
  order: explicit `personas/amigos/<seat>.md` (legacy override) > the `role:`-matched
  `personas/seats/*.md` > skill default > generic.
- A **deterministic tiebreak is required** for two seats claiming one role and for zero seats
  claiming it (the latter falls through to default, never crashes) - both need negative tests (QA).
- A seat card present but missing its review render is a **hard error**, not a silent fallback (QA).
- Failing-first unit tests: a role-matched seat with no amigo override resolves to the seat, not the
  default (must fail on today's code first); two-claim and zero-claim roles covered; and
  build-instance-id != review-instance-id resolved from one seat card (the independence floor, RFC0021
  D5). CHANGELOG.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
