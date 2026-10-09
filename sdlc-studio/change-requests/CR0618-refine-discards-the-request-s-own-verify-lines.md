# CR-0618: refine discards the request's own Verify lines when it seeds the story, so grooming done on the CR is lost and redone

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-09)
> **Decomposed-into:** EP0283
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Date:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T10:59:21Z

## Summary

`_seed_acs` (refine.py ~203) transcribes each request criterion as the AC TITLE and leaves Given/When/Then and `Verify:` as `{{placeholders}}`, by design ('seeding never fabricates executability'). But copying a Verify line the request ALREADY carries is transcription, not fabrication. In a consuming project, its CR0554 was groomed with a new-test-file Verify per criterion (they fail at base); `refine apply` seeded US0608 with placeholders and the orchestrator re-typed all three Verify lines by hand. Because the skill executes verifiers only on stories and bugs (`EXECUTES_VERIFIERS`), refining is the route a CR's checks must take to run at all, so losing them on that route is the worst place.

## Impact

Every refined CR's executable checks are re-typed by hand, with room for transcription drift.

## Acceptance Criteria

- [ ] Refining a single-story request whose criteria carry Verify lines seeds each story AC with that criterion's Verify line, and a criterion without one still gets the placeholder

## Triage

- Confirmed by reading `_seed_acs` (refine.py): each request criterion becomes an AC title with `{{placeholder}}` Given/When/Then and Verify lines. Copying a Verify line the request already carries is transcription, not fabrication, so the change keeps the 'seeding never fabricates executability' rule.
- Priority Low and size S stand. A CR is not work until `refine` decomposes it; this one will refine to one story. Related: BG0995 (the same seeding path).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | Claude Opus 5.5 | Raised |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: confirmed; private project names generalised; relations recorded |

## Amigo Consult

_Consulted 2026-10-09: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Priority, if only one request fits 6.2: the panel recommends CR0628, since every D0355 draft carries per-story criteria and no open request carries a Verify line.
- File the validator contradiction (the `file_as_bugs` entry) as a bug and build it in the same run as the first CR0618 story. The panel recommends yes; the filing is the operator's.
- Re-grade BG0995 from Medium to Low. The panel recommends yes: no open request carries the label, both CR writers emit plain text, and the defect is loud.
