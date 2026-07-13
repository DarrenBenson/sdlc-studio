<!--
Template: Handoff Index
File: sdlc-studio/handoffs/_index.md
Status values: N/A (generated records, outside the status machinery)
Related: help/handoff.md, reference-sprint.md
-->
# Handoff Index

**Last Updated:** {{last_updated}}

Run-close handoff guides, one per run that stopped short of its goal (budget spent, a unit
blocked, an operator stop). Each names what was delivered with its evidence and every
remaining item with a pointer to start from - the failing AC, the check it stalled at, the
blocker, or the file - plus a `copilot-tail` / `judgement` suitability tag and the open
decisions. Generated, never hand-authored: `handoff generate` joins the run's own evidence,
allocates the id and appends the row here. It is linked from the batch retro and emits the
worklist the next `sprint plan --worklist` reads back.

| ID | Title | Date |
| --- | --- | --- |
| [HO{{handoff_id}}](HO{{handoff_id}}-{{handoff_slug}}.md) | {{title}} | {{date}} |
