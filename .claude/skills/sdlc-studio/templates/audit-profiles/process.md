# Audit Profile: process

The packaged lens pack for the way a delivery was **produced**, not what it claims. Its
sibling `test` pack attacks the claims a codebase makes about itself; this pack attacks the
process behind them. The class is uniform: **work done before the contract it depends on was
established** - a repair written before its approach was weighed, a path written from memory
before the tree was read, a count kept by hand beside the mechanism that already derives it.
None of these come from not knowing the rule. Several happened minutes after the same author
wrote the rule down. So the pack looks for the SHAPE rather than trusting the discipline.

> **Refute panel:** shared - 3 skeptics per candidate, survive on >= 2 of 3
> (`reference-audit.md#audit-refute`). This pack does not opt out.

**Default scope: the delivery, not a directory.** The evidence for these lenses is spread
across commits, artefact fields, index tables and run reports, not one tree of source. Point
a finder at the change under audit and the artefacts it touched, and give it the recorded
incident the lens was drawn from.

Use each row as the `{{lens}}` / `{{lens_question}}` of `audit-finder.md`, one finder per
lens, looped until-dry; then the shared refute panel and filer.

## Signatures {#process-signatures}

Each lens names the **signature** that finds it - the mechanical detector a finder runs
before reasoning, or a plain statement that none exists. A mechanical signature begins with a
runnable detector token the pack documents and names only paths that are on disk; where no
search can single the class out, the signature begins with `manual - ` and states why, so a
reader can tell a detector from a hope. The documented detector token is `python3` (a skill
script run over the workspace). Reasoning still runs behind every lens - a signature narrows
where a finder looks, it does not replace the finder.

| Lens | Adversarial question | Hunts for | Drawn from | Signature |
| --- | --- | --- | --- | --- |
| path-from-memory | Was this path, id or field value resolved against the tree, or written from memory? | an Affects or Depends-on field naming a file that is not on disk; a path carrying a remembered prefix the tree does not use; a reference to an id nothing defines; a value copied from a sibling artefact and never re-checked here | LL0046, LL0013 | python3 .claude/skills/sdlc-studio/scripts/integrity.py check |
| count-by-hand | Is this count or list kept by hand beside a mechanism that already derives it? | an index total typed into prose next to the census that computes it; a per-epic tally maintained by editing; a figure published without checking the parser's contract it is fed into; a guard message that restates the rule rather than deriving it from the guard | LL0001, LL0042 | python3 .claude/skills/sdlc-studio/scripts/reconcile.py detect |
| accepted-without-running | Did this check execute, or was a green read off something that never ran? | a selector that matched nothing read as a pass; an always-passing prose verifier; an exit code trusted where the real failure mode is that it did not run; a summary line reporting work that was skipped | LL0008, LL0023 | python3 .claude/skills/sdlc-studio/scripts/verify_ac.py stamps |
| repair-without-plan | Was this repair attacked as an approach before it was written, or driven straight from the finding? | a review finding answered by an immediate diff with no approach weighed first; a round of repairs manufacturing the next round's defects; a fix that closes the sentence and leaves the class; a change defended by re-reading it rather than by attacking it | LL0046, LL0045, LL0028 | manual - a plan is not kept in the tree a search can reach, and whether a repair was attacked before it was written is a reading of process rather than a state on disk |
| skipped-preflight | Was a cheaper, scoped or already-existing form of this work checked for before it was done? | a whole-workspace run started when a scoped form existed; a helper built that had already shipped; a broad change where a narrow one was one command away; a contract acted on before it was read | LL0046, LL0027 | manual - whether a cheaper or existing form was looked for first is a choice the actor made or skipped, and it leaves no artefact in the tree to search for |

## Filing (binding)

Every candidate that survives the refute panel is either filed through `file_finding.py`
or declined with a stated reason. Silence on a candidate is not an outcome of this run.
A declined candidate keeps its reason in the run report, so a later reader can tell a
judged candidate from an unexamined one.

## Notes

- This pack is declarative: a lens is a name + an adversarial question + what it hunts +
  the recorded failure it was drawn from + its signature. A project extends a profile by
  appending rows (see `reference-audit.md#audit-extend`); a new row states its own evidence
  and its own signature in the same way, or declares plainly that it has no mechanical one.
- `Drawn from` cites the shipped lessons registry (`lessons/_index.md`). Read the cited
  entries into the finder's context: each carries the concrete failure that produced the
  lens, which is worth more to a finder than the lens name.
- A signature narrows the search; it does not settle the finding. A mechanical detector
  reports candidates a finder then judges, and no detector that ships with this pack can
  prove it fires on the very incident its lens was drawn from - that is a manual run over a
  commit range, recorded in the run report, not a test the pack can hold.
- A finding here is usually a **Bug** or a **CR**: a process defect that already shipped
  is wrong now, and one that recurs is a change to how the work is done. File through
  `file_finding.py` so ids and index rows are tool-allocated rather than hand-authored.
- Pair with the `test` pack rather than replacing it: `test` attacks what the code claims,
  `process` attacks how the claim was produced. A delivery that passes both has neither a
  lying docstring nor a repair written before its plan.
