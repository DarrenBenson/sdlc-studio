# CR-0120: project upgrade enriches existing review seats in place instead of installing a parallel amigo set

> **Status:** Proposed
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Improvement

## Summary

`project upgrade --apply` (CR0119) installs the three generic v3.1 amigo cards (Dani/Sam/Lena) into
`personas/amigos/` whenever they are absent - **regardless of whether the project already has review
seats filling those roles**. A project with the established RFC0016 five-seat model
(Sarah/Marcus/Priya/Maya/Claude-Code) ends up with two parallel role-based persona-review systems and
no signal that they overlap: the install was silent, with no flag, no note, no "heads-up, this
overlaps your `seats/`". A field operator hit exactly this and had to notice the collision unaided.

The default should be to **enrich the existing seats in place**, not manufacture a parallel set. When
the project already has seats (or design personas) covering engineering/qa/product, the upgrade should
bring those up to the richer amigo-template depth (Craft/Experience Goals, Shadow, dual-render,
Tensions) rather than dropping generic cards beside them. Generic amigos should only be scaffolded
greenfield, when no seat fills the role. This is the upgrade half of the seats-vs-amigos duality; the
resolver half is [[BG0042]].

**[[RFC0021]] Accepted (Option B, sliced) settles the model.** One role-based actor model: `seats/`
stays the runtime home and name; `personas/amigos/` is retired as a runtime home and survives only as
the `templates/personas/amigos/` greenfield defaults source. Delivery is **two slices** (Product
refinement): AC1-AC4 below are **slice 1** (the operator's actual pain - resolver reads seats, no
silent parallel install) and ship with [[BG0042]]; AC5 (merge `amigo-template.md` +
`review-seat-charter.md` into one enriched seat schema and enrich seats to it) is **slice 2**, a
follow-up that must NOT gate slice 1. A seat present but missing its review render is a hard error
(RFC0021 D4).

## Acceptance Criteria

- [ ] `missing-amigos` is **seat-aware**: a role already covered by an existing review seat (matched by
      the seat charter's declared role, not filename) is NOT reported as a missing amigo
- [ ] when seats cover the roles, the default action enriches the existing seat cards in place with the
      amigo-template depth (idempotent; never clobbers operator customisation), instead of installing a
      parallel `personas/amigos/` set
- [ ] generic amigo cards are installed only greenfield - when no seat/persona fills that role
- [ ] when an install or enrichment touches personas that overlap an existing review model, the upgrade
      **emits an explicit heads-up** naming the overlap (no silent collision), even in `--dry-run`
- [ ] reference-upgrade.md documents enrich-in-place as the default and the greenfield-only install;
      unit tests cover seat-covered (enrich, no parallel install) vs greenfield (install); CHANGELOG

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
