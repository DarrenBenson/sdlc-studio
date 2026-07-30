# CR-0505: a sprint has no compulsory checklist and no report document, so what was dropped, what crept in and what is carried are known only to whoever ran it

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Date:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator-directed at the 2026-07-30 close); human; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

A sprint run today leaves its record scattered across artefact statuses, a retro if one is written, commit messages, and prose in reviews/LATEST.md. Nothing forces the compulsory items to be completed, and nothing collects the answers in one place - so the facts an operator needs to judge a sprint are reconstructed by asking. Measured on the 2026-07-30 batch (11 units, 47 pts): the reviews were run with hand-written briefs instead of the shipped seat ceremony and nothing noticed; scope crept by 15 filed bugs and 2 CRs that were never planned; two units were held mid-sprint on an operator decision and the fact that they were held was carried in conversation, not in any artefact; the four repaired MAJORs and the eleven carried known issues were only written down because the operator asked twice; and the units' points, the review outcome and the carried defects never appeared side by side, which is exactly the view needed to answer 'is this sprint closeable'. The same items recur every run and are re-derived every run.

## Impact

Who: the operator judging a sprint, and the next agent picking up the residue. What breaks: the close becomes an interview. Nothing refuses a sprint that skipped the review ceremony, dropped a planned unit, or carried a stop-ship as a known issue - because nothing states the compulsory set, so no lane can hold it. The cost compounds: a decision taken in conversation (which units are held, what is accepted as a known issue) is lost the moment the session ends, and the next run starts by re-deriving it. This sprint spent two operator prompts asking for facts a report would have carried.

## Acceptance Criteria

- [ ] There is ONE compulsory checklist per sprint, and it is a template that renders into a sprint report - the same document, not two artefacts to keep in step. Its sections are the questions this repo re-derives every run: planned vs delivered points, units DROPPED with the reason, SCOPE CREEP (artefacts filed that were not planned, counted and listed), the review that ran and by which seat, KNOWN ISSUES carried with their stop-ship ruling, and the sign-off record.
- [ ] Each compulsory item is DERIVED where it can be derived, and only asked where it cannot. Delivered points, filed-but-unplanned artefacts, the review records and the sign-off record are all already in the tree - a checklist that asks an agent to retype them will be filled in with what the agent remembers rather than what happened, which is the failure mode the derived index already exists to prevent.
- [ ] The close REFUSES on an unanswered compulsory item, naming it. A checklist nothing enforces is the state this CR is filed from: the seat ceremony was already compulsory in prose and was skipped without a warning.
- [ ] A known issue carried past the close records its STOP-SHIP RULING and who made it, so 'carried' and 'nobody looked' are distinguishable in the record - this batch carried eleven, one of them a shipped command that tracebacks on a default install, and that ruling existed only in conversation until it was written down by hand.
- [ ] Scope creep is reported as a NUMBER against the plan, not as a list to read: a sprint that filed 17 unplanned artefacts against 11 planned units should say so in one line, because that ratio is the signal and it is currently invisible.

## Recommendation

Sequence this INTO THE NEXT SPRINT at the operator's direction. Build the derived half first: the report is worth more than the checklist, and a report assembled from the tree cannot be filled in with a wishful answer. `retro.py` already reads the batch, the accuracy figures and the lessons, so the report belongs there rather than in a new script - check during refine whether this absorbs the retro rather than sitting beside it, since two close-time documents that both claim to record the run is the drift this repo keeps filing bugs about. The enforcement AC should land in the same slice as the template: the previous three attempts to make a practice compulsory by writing it down (the seat ceremony, the waiver shrink rule, the review standing practices) were all skipped or unenforced, and this CR exists because of the first one.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Darren Benson (operator-directed at the 2026-07-30 close) | Raised |
