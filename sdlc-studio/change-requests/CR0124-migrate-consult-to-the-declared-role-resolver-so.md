# CR-0124: migrate consult to the declared-role resolver so authored seats are honoured there too

> **Status:** Proposed
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement

## Summary

Surfaced by the WS4a (RFC0021 slice 1) QA review. [[BG0042]] made the delegation resolver
(`persona_resolve`) read a project's authored review seats by their declared `role:` field, so an
authored seat is now honoured when the sprint loop delegates build/review work. But the **consult**
workflow is a SECOND persona-loading path: `reference-consult.md` still loads its seat charter from
the `review-seat-charter.md` template keyed on `{{seat_name}}`/prose and reads `personas/index.md` +
`personas/stakeholders/`. It does NOT call `persona_resolve` and does NOT honour the declared `role:`
field. So a project's authored seat is used for delegation but still shadowed in consult - the
duality is only half-resolved until consult shares the same resolver.

This is the next call site to migrate (the same "find every reader of the key" discipline that
[[BG0039]] taught - see [[LL0008]] sibling lesson on call-site sweeps). [[RFC0021]] D2 names consult
as part of Option B's end state.

## Acceptance Criteria

- [ ] consult resolves its seat through the same declared-`role:` chain as `persona_resolve`
      (project `personas/seats/` role-matched > skill default), so an authored seat is honoured in
      consult, not only in delegation
- [ ] consult no longer keys the seat on template `{{seat_name}}`/H1 prose for projects that have
      authored seats; the generic charter remains the fallback when no seat fills the role
- [ ] a render-less seat is handled consistently with the delegation resolver (review-render
      required for a consult, per RFC0021 D4)
- [ ] unit test: a project with an authored role-matched seat drives the consult from that seat, not
      the generic template; reference-consult.md updated; CHANGELOG

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
