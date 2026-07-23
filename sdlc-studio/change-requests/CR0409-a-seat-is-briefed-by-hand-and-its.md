# CR-0409: A seat is briefed by hand and its verdict typed back through a shell argument, so the plan review's quality depends on the author it is meant to check

> **Status:** Complete
> **Decomposed-into:** EP0153
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Two friction points from the first live Sprint Goal review, both about how a verdict gets into and out of the system.

BRIEFING. There is no command that emits what a seat needs to review a goal. The author assembles it by hand: the batch and where the worklist lives, that the stories carry placeholder acceptance criteria because refine seeds scaffolds, which shared-file clusters the planner derived, the project's own relevant failure modes, and which files are worth reading. Every one of those is derivable from the run state, the batch and the lessons registry. Because it is hand-assembled, the review's quality depends on how well the AUTHOR briefs it - and the author is the party the review exists to check. A seat briefed thinly returns a thin verdict and the gate is discharged just the same. Concretely, the three seats in this review found a false scope claim, an information-free clause and a satisfiable-by-trivia bar, all of which turned on context that happened to be included; a shorter brief would have surfaced none of them.

VERDICT ENTRY. `--seat` takes a pipe-delimited string of free prose on the command line, with no --fields-file path. This is exactly the class CR0392 names for four other prose-writing scripts: backticks and dollar-parenthesis are command substitution inside a shell argument, so a seat's note containing a command is EXECUTED rather than stored. A real verdict quotes commands and file paths constantly - the three recorded here all did - so this surface is more exposed than most, not less. It should be added to CR0392's scope rather than fixed separately.

**MEASURED, in the command this CR names, while recording the review this CR is about.** A seat
note quoting `equivalent` in backticks was passed to `goal-review record` as a shell argument.
The shell performed command substitution, `equivalent: command not found` went to stderr, and
the WORD WAS SILENTLY DELETED from the stored verdict: the recorded QA note read "a
self-registered  verdict with free text discharges any survivor", missing the term the sentence
was about. Nothing in the tool noticed; the record simply held a different sentence from the one
the reviewer wrote. It was caught by reading the stored JSON afterwards, and re-recorded intact.
This is the second surface where this class has now been observed rather than argued, and it is
the one holding an independent reviewer's words - the artefact whose whole value is being an
unaltered account of what somebody else said.

## Impact

Every project running the goal review, and worst where it matters most: the seats are supposed to be an independent check on the author's plan, and today both the input to that check and the transcription of its output pass through the author's hands unaided. The consult is also not reproducible - two operators briefing the same seats on the same goal get different reviews, and nothing records which brief was given.

## Acceptance Criteria

- [ ] A command emits the seat brief for the current batch and goal, derived from the run state, the worklist and the planner's own output, so the same batch briefs the same way every time.
- [ ] The brief names the batch's grooming state - placeholder acceptance criteria, shared-file clusters, the reachable end state - because those are what the first live review turned on.
- [ ] The brief that was given is recorded with the verdicts, so a thin review is visible as a thin brief rather than as a seat that found nothing.
- [ ] goal-review record accepts a --fields-file document, so no seat's prose crosses a shell. Fold this into CR0392 rather than building a second path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
