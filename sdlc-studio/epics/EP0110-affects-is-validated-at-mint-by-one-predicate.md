# EP0110: Affects is validated at mint, by one predicate every writer shares

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0400
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0400. Delivers the work CR0400 requested.

## Story Breakdown

- [ ] [US0323: One shared resolvable-Affects predicate serves file_finding, artifact new and refine apply, so a future writer cannot be added without it](../stories/US0323-one-shared-resolvable-affects-predicate-serves-file-finding.md)
- [ ] [US0324: artifact new and refine apply refuse an unresolvable Affects before an id is allocated, minting nothing](../stories/US0324-artifact-new-and-refine-apply-refuse-an-unresolvable.md)
- [ ] [US0325: The refusal names the closest unique basename match where one exists, rather than sending the caller to look](../stories/US0325-the-refusal-names-the-closest-unique-basename-match.md)

## Acceptance Criteria (Epic Level)

- [ ] `artifact new` and `refine apply` validate a declared Affects with the SAME predicate `file_finding` uses, refusing before any id is allocated so a bad path mints nothing.
- [ ] The refusal names the closest unique basename match where one exists (CR0399), so the caller is told the answer the tool can already see rather than being sent to look for it.
- [ ] A path to a file the unit will CREATE is still legitimate: the check refuses only when NO declared path resolves, matching the rule the grooming gate already applies, so the ordinary case of naming a not-yet-existing file is unaffected.
- [ ] One shared helper serves all three writers, so a future writer cannot be added without the check and the three cannot drift on what 'resolvable' means.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
