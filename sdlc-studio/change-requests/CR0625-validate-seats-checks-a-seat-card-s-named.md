# CR-0625: validate seats checks a seat card's named personas against the project's declared cast, so a seat cannot review for a primary persona the project no longer has

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-09)
> **Decomposed-into:** EP0285
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/reference-persona.md
> **Evidence:** Operator-relayed assessment of a consuming project's Sprint 0 (sdlc-studio-lens), 2026-10-08: the product seat's opening says the project manager is the primary reader while its proficiency line still says it is cold on 'the primary persona (Darren)', and its craft goals are the old dashboard sentence. 'A review that cannot cite Maya's frustrations is reviewing a different product.' `validate.check_seats` checks role comments, headings, the demographic denylist, one card per role and provenance stamps; nothing compares a card's persona references with the cast.
> **Date:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T11:37:35Z

## Summary

A seat card names the personas it reviews for, and the project declares its cast (primary and secondary personas). When the cast changes, the seat cards are not re-read, so a seat argues for a persona the project has demoted. `validate seats` is the natural place: warn when a card names a persona as primary that the cast does not declare primary, or names one that does not exist.

## Impact

A product seat reviewing against the wrong primary persona gives confident verdicts about a different product.

## Acceptance Criteria

- [ ] `validate seats` warns, naming the card and line, when a seat card calls a persona primary that the project's personas do not declare primary, or names a persona with no persona file
- [ ] A card consistent with the cast produces no warning

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | Claude Opus 5.5 | Raised |

## Amigo Consult

_Consulted 2026-10-09: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Release cut: the panel recommends 6.2 for 19 points (End goal reader 3, goal review 3, plan advisory 3, Serves goal reference 3, --serves 2, goals-served 2, seat-card check 3), with the standing seed (5) later unless BG0995, G9's request-seed story and CR0628's breakdown story land first. Confirm.
- G7 interplay: should a standing criterion be exempt from revert-check naming? The panel recommends yes, as a seeded, reasoned `Revert-check-exempt` entry. The draft recommends instead that G7 exempt a criterion carrying the `standing:` marker. The field is one line whose single reason covers every id it lists (`revert_exemptions`, verify_ac.py:3926-3943), so a seeded id would either share an author's unrelated reason or overwrite it, and a hand-written standing AC counted by its verbatim Verify would still be named. Rule with G7.
