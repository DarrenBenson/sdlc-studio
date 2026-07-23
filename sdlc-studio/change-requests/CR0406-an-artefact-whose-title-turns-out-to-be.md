# CR-0406: An artefact whose TITLE turns out to be false has no deterministic correction path, so the one field a reader sees first is the one field only a hand-edit can fix

> **Status:** Complete
> **Decomposed-into:** EP0150
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py,.claude/skills/sdlc-studio/scripts/transition.py,.claude/skills/sdlc-studio/scripts/reconcile.py
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Hit while correcting CR0405 before this sprint's refinement. CR0405 was filed asserting CHANGELOG.md has no helper; scripts/changelog.py is that helper, so the claim is false and it is IN THE TITLE, which is what the index row shows and what a reader sees first.

Every other field has a deterministic writer. `transition.py set` moves a status and syncs the index. `transition.py annotate` stamps any metadata field. `artifact.py new` mints the id, the filename and the index row together. The title alone lives in three places at once - the filename slug, the H1, and the index row's link text - and no command reconciles them. Correcting it means editing the H1 by hand, renaming the file by hand, and repairing the index row by hand, then hoping reconcile agrees. That is precisely the hand-editing of a structured surface the rest of this tooling exists to abolish, so the correct move today is to leave a known-false title standing and explain it in a Revision History row nobody reads first.

The corrective is worth stating because it is the general shape: a field with no deterministic writer is a field that stays wrong. This project already learned it for ids, index rows, statuses and findings. The title is the last one left, and it is the highest-visibility field on the artefact.

Note the interaction with links. A rename breaks every inbound reference - epic breakdown lines, Decomposed-into fields, Delivers fields, LATEST.md, retros - which is exactly why nobody does it by hand, and exactly why a tool should. `check_links.py` already knows how to find them.

**Measured during RUN-01KY5EJX's repair round.** BG0265's title carried a count that the
run's own grooming falsified. Correcting it required three separate edits: the H1, the index
row, and a filename check. `reconcile.py apply` was run first and reported `changed 0 row(s)`, since
it syncs status and counts but not titles, so the index row had to be hand-edited, which is
the failure this CR describes, performed while filing evidence for it. The filename happened
to be slug-stable because the changed words were past the slug's truncation point; had they
not been, a rename would also have been needed with no tool to keep the three in step.

## Impact

Every project using this skill, and worst in the projects that use it best: the more an artefact is cited, the more expensive its title is to correct, so a wrong title on a well-linked artefact is effectively permanent. The concrete cost today is one shipped CR whose title asserts something false about this repository, kept that way deliberately because the alternative was worse.

## Acceptance Criteria

- [ ] A deterministic retitle exists that changes the H1, the filename slug and the index row link text as one operation, refusing before any write if any of the three cannot be updated.
- [ ] Inbound references are found and rewritten, or the retitle refuses and NAMES them - never rewrites the artefact and leaves the references dangling.
- [ ] A retitle is recorded on the artefact, so a reader can see the title changed and what it was, rather than finding a filename that disagrees with git history for no stated reason.
- [ ] Where a retitle is refused, the message states the reason and what to do, in the manner the grooming refusal already sets.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
