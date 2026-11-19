# EP0327: Authors and reviewers run one shipped mutation runner and the self-check records its report

> **Status:** Draft
> **Derived Point Total:** 15
> **Parent:** CR0673
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0673. Delivers the work CR0673 requested.

## Story Breakdown

- [ ] [US1199: The mutation probe drops each conjunct of a guard and flips polarity words in a document a test reads](../stories/US1199-the-mutation-probe-drops-each-conjunct-of-a.md)
- [x] [US1200: A mutation runner applies a list of file edits in a scratch copy and prints one verdict line for each](../stories/US1200-a-mutation-runner-applies-a-list-of-file.md)
- [x] [US1201: Self-check record takes the runner's report and mutant list, and the author brief names the runner command](../stories/US1201-self-check-record-takes-the-runner-s-report.md)
- [x] [US1202: The critic brief prints the author's recorded mutants and their replay, labelled as the author's](../stories/US1202-the-critic-brief-prints-the-author-s-recorded.md)

## Acceptance Criteria (Epic Level)

- [ ] `mutation.py` gains drop-conjunct (each operand of an and/or guard removed in turn) and, for a .md file in Affects that a declared test reads, flip-polarity (below and above, only and also, never and always, must and may, not removed); a fixture reports US1117's M11 and US1120's inverted rule as survivors.
- [ ] A runner entry point takes a JSON list of file, old, new and test entries, applies each in a scratch copy of the Affects, runs the named test, restores and checks byte identity, and prints one line per mutant (killed or survived, and the test's last line).
- [ ] `critic.py self-check record --mutants-from <report>` records the runner's verdicts and the full mutant list beside the counts and refuses a survivor with no answer, and the author brief prints the runner command for the unit's Verify selectors instead of asking for hand-chosen mutants.
- [ ] `critic.py brief` prints the author's recorded mutant list and the runner's replay of it, labelled as the author's, and a replayed author mutant is never counted as the reviewer's own pass.
- [ ] Before and after: on the next sprint builders make at most 3 mutation calls per unit against run six's 6.8 (88 over 13), and no round 2 has as its only blocker a vacuous pin the operators cover.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
