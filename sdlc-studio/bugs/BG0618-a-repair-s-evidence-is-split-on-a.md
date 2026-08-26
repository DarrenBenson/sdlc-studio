# BG0618: a repair's evidence is split on a bare semicolon and the remainder is SILENTLY DROPPED, so the review ledger records less than the author wrote

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Hit repeatedly while recording the RUN-01M0WCCG repair round on 2026-08-25, where several closures were rejected or partially recorded until every semicolon was removed from the prose. Root cause isolated by executing `parse_closures` directly on 2026-08-26 and measuring the lost text. Parser quoted from critic.py:903 and 909-910.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`parse_closures` splits the `closed` text on a bare `;` (critic.py:903) and then discards any chunk that has no ` -> ` in it (critic.py:909-910, `if not finding or not evidence: continue`). There is no escaping, no quoting, and no warning. So a closure whose EVIDENCE contains a semicolon is truncated at that semicolon and everything after it vanishes from the durable record without a word. Proven by execution on 2026-08-26: the input `the guard fires -> fixed in sprint.py; the tests now cover the epic case, and the mutant was executed and killed` parses to ONE closure whose evidence is `fixed in sprint.py`, and 72 characters - the half that names the actual proof - are gone. The docstring states the same channel shape is used by `--issues`, so a verdict's findings have the identical exposure. The `--closed-file` path exists precisely so prose can be carried verbatim off disk rather than through a shell, and it protects backticks and `$(` while leaving this wide open.

## Steps to Reproduce

1. Write a repair closure whose evidence contains a semicolon, in a file. 2. `critic.py repair --unit <id> --author <who> --closed-file <file>`. 3. Read sdlc-studio/reviews/repair-record.md: the evidence stops at the first semicolon. Nothing is printed, nothing is refused, and the exit code is 0. Reproduced in-process against `parse_closures` directly, so the loss is in the parser rather than in any shell.

## Proposed Fix

Two changes, and the second matters more than the first. Give the channel a way to carry a semicolon - the file path already reads structured input off disk, so accept a JSON list of closures there and stop re-parsing prose into records. And in every case, REFUSE a chunk that has no ` -> ` rather than dropping it: a fragment the parser cannot understand is either an author error or a split that should not have happened, and both are worth a refusal. Silence is the part that makes this dangerous, not the split.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `parse_closures` splits the `closed` text on a bare `;` (critic.py:903) and then discards any chunk that has no ` -> ` in it (critic.py:909-910, `if not...
- [ ] **AC2** The proposed fix lands, pinned by a test: Two changes, and the second matters more than the first.

## Impact

The repair record is what a reviewer reads to judge whether a REJECT was genuinely answered, and `repair_state` computes complete-versus-partial from these rows. Recording less evidence than the author supplied, with no signal, corrupts the one artefact whose job is to prove a finding was closed - and it does so most often on exactly the evidence worth having, because a substantial closure is the kind that runs to two clauses. Graded High against the rubric: the feature is broken and there is no workaround the tool ever tells you about. An author cannot avoid a semicolon they do not know is fatal. Re-triage it if the panel disagrees, as BG0604 was.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
