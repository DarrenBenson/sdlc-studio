# US1015: A verdict written by the context that edited the unit is a self-review, whatever seat it names

> **Status:** Draft
> **Delivers:** CR0619
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/verdict_provenance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py, .claude/skills/sdlc-studio/reference-review.md, changelog.d/US1015.md
> **Epic:** EP0280
> **Points:** 5
> **Depends on:** US1014
> **Persona:** Maya Okafor

## User Story

**As** a team lead holding humans and agents to the same discipline
**I want** a verdict whose writing or recording context edited the unit's files before it was briefed to be recorded and shown as a self-review, whatever reviewer name it carries and whichever command wrote it
**So that** a session that wrote the code and then recorded its own verdicts under a QA seat's name cannot pass as independent review

## Acceptance Criteria

- **AC1:** Given fixture transcripts in which the main thread edited `src/unit.py` (the unit's Affects) and then wrote the issued verdict file, when `critic.py record --reviewer "Tomas Reinholt (qa)" --author engineering` runs, then the row is written with `self-review:src/unit.py` in its `Source` cell, `show` says so, and `transition.py` refuses the unit Done as not independently reviewed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewByContextTests::test_the_editing_context_is_a_self_review_whatever_the_seat_name
- **AC2:** Given the same editing main thread, when it runs `transition.py set US0001 --status Done --verdict APPROVE --reviewer "Tomas Reinholt (qa)" --author engineering`, then the transition is refused naming the self-review and the edited file, the provisional verdict is withdrawn, and the unit keeps its status.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewByContextTests::test_the_one_call_close_from_the_editing_thread_is_refused
- **AC3:** Given reviewer subagent `r1`, which received the brief and afterwards applied a mutant with its Edit tool to `src/unit.py` in its own worktree, reverted it, and wrote the issued verdict file, when `record` runs, then the row is independent and carries no self-review token.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewByContextTests::test_a_reviewer_mutating_its_own_worktree_after_the_brief_stays_independent
- **AC4:** Given author subagent `a1`, which edited `src/unit.py` inside its worktree at `.claude/worktrees/agent-a1` and was never briefed, when `a1` writes a verdict file for the unit, then the row is a self-review naming `src/unit.py`; and in the same test, subagent `r1`, which edited nothing, writing the next round's file records as independent.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewByContextTests::test_a_worktree_author_is_matched_to_the_units_files

## Notes

- Release: later (D0355 breakdown G6, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: comparing only the `--author` and `--reviewer` strings, as every writer does today (critic.py:3317 warns; `independence`, critic.py:2066, gates)
- AC2 must fail on: the context check placed in `cmd_record` rather than `_write_verdict` (critic.py:349), so the one-call close (`provisional_verdict`) and `artifact.py close --verdict` (`record_verdict`) walk round it
- AC3 must fail on: counting every edit to an Affects path whatever its time, which brands each reviewer that follows the shipped practice ('Mutate in an ISOLATED CHECKOUT of your own', critic.py:2219-2220; those worktrees live inside the repository)
- AC4 must fail on: comparing absolute paths, so an edit made in a worktree is never matched to the unit's repository-relative Affects and the author's own verdict passes as independent
- Checked at HEAD: `record --reviewer 'Tomas Reinholt (qa)' --author 'engineering seat'` from the session that wrote the code is recorded, and `is_independent` returns True (fixture probe; panel re-probed). `transition.py set --verdict` (transition.py:1495-1517) and `artifact.py close --verdict` (artifact.py:1640-1665) apply only the same string check before writing.
- One home for the rule: the context check runs in `_write_verdict`, which all three writers share. It writes the `self-review:<path>` token into the `Source` cell. `independence(reviewer, author, source='')` gains an optional third argument naming the Source cell, which `is_independent` fills from the row. The pre-write string checks at transition.py:1514 and artifact.py:1653 stay as they are. The module keeps the one authority its own docstring (critic.py:2067-2075) records two copies failing. Caller inputs are never rewritten (LL0024).
- The recording context is the transcript holding the current process's own command: a running Bash call is already in its transcript, in the main thread or a subagent. A flagged verdict is judged by that context; a file verdict by its writer (story 5). CR0619 AC3's 'session' becomes a context here, because a session id covers the orchestrator and every agent it spawned.
- Authoring evidence (panel, Q5): a Write, Edit or NotebookEdit call on an Affects path, matched repository-relative through the agent's `worktreePath`, made before the context first received the brief (the issued path is unique, so its first appearance is the timestamp). It is bounded to the unit's delivery: from the open run's review base for the unit, or its In Progress transition, so an edit to a shared file for an earlier unit in a long session does not count. Known limit: an author editing through Bash (`sed -i`, a heredoc) is not counted.
- Re-sized from 3 to 5: three writers instead of one, and the before-the-brief bound.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G6 after the refine panel's review |
