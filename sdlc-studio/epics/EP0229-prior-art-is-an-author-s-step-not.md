# EP0229: Prior art is an author's step, not something a reviewer discovers for them

> **Status:** Draft
> **Derived Point Total:** 11
> **Parent:** CR0529
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0529. Delivers the work CR0529 requested.

## Story Breakdown

- [ ] [US0740: The toolchain runbook's DELIVER section names the prior-art check with its command](../stories/US0740-the-toolchain-runbook-s-deliver-section-names-the.md)
- [ ] [US0741: The check names BOTH halves: the history search and the one reference document](../stories/US0741-the-check-names-both-halves-the-history-search.md)
- [ ] [US0742: The guidance states that an artefact records BELIEF and history records what happened](../stories/US0742-the-guidance-states-that-an-artefact-records-belief.md)
- [ ] [US0743: Reading the artefact corpus in bulk is explicitly NOT the instruction, and the row says so](../stories/US0743-reading-the-artefact-corpus-in-bulk-is-explicitly.md)
- [ ] [US0744: Whether `critic.py brief` gains an author-facing form is decided and recorded either way](../stories/US0744-whether-critic-py-brief-gains-an-author-facing.md)

## Acceptance Criteria (Epic Level)

- [ ] The toolchain runbook's DELIVER section names the prior-art check as a step, with the command beside the hand-rolled shape it replaces, so an author reading the row for the step they are on meets it before starting rather than after being rejected.
- [ ] The check names BOTH halves, because the three recorded failures split across them: `git log -S <symbol>` for a symbol the author did not write, and the one reference doc governing the surface being changed - US0487's was `reference-schema.md`, a versioned contract, and reading it was worth four gate refusals.
- [ ] The guidance states plainly that an artefact records BELIEF and history records what happened, and that where they disagree the history wins - BG0485's parent asserted a defect that had been fixed four days before the bug was filed, so a rule that sent an author to the corpus first would have confirmed the wrong thing.
- [ ] Reading the artefact corpus in bulk is explicitly NOT the instruction, and the row says so, because 1,678 records cannot be read per unit and the attempt would push authors back to whichever few they happened to pick.
- [ ] Whether `critic.py brief` gains an author-facing form is decided and recorded either way - the claim-inventory machinery already exists and only its audience is fixed, so declining it is a choice that should be visible rather than an omission.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
