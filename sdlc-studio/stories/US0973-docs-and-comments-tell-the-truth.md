# US0973: Docs and comments tell the truth

> **Status:** Ready
> **Delivers:** CR0592
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/status.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-agentic-lessons.md, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_docs_tell_truth.py, changelog.d/US0973.md
> **Epic:** EP0270
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the help, references and code comments to describe what the tools do today
**So that** I can copy an example and have it run

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from CR0592 bullets 34, 37, 54, 62 and 70 (#39 is a duplicate of #70), 2 points. Text and dead-code changes only; no behaviour change.

- #34 help/status.md:125 says `status.py pillars` prints a weighted health score; it prints counts and per-type percentages.
- #37 reference-sprint.md:210's `decisions.py waive` example omits `--rationale`, so it is refused as written; help/sprint.md:312 says `unanswered` is the set the close would have refused on (the close no longer refuses); `docgen.py reading-guides --check` reports 3 drift items; `persona_resolve.py resolve --render build` alone prints "the concrete contract above" with nothing above it.
- #54 `run_state.ReviewLedgerError` is raised by nothing, yet sprint.py catches it at 4525, 5851 and 8924; project_upgrade.py's docstring says init writes no `.version` (it does).
- #62 help/gate.md:300, 308, 315 and 336 hard-code `.claude/skills/...`, so a skill vendored under `.agents/skills` copies a command that does not run; lines 26-103 already use `$CLAUDE_SKILL_DIR`.
- #70 `critic.py record --issues` accepts `\;` for a semicolon inside a finding, but neither its help nor its refusal says so.

## Premise at HEAD

Executed at `85042135`:

```text
$ python3 .claude/skills/sdlc-studio/scripts/docgen.py reading-guides --check
docgen reading-guides: 3 drift item(s) over 26 reference(s)
```

The drifting files are reference-agentic-lessons.md, reference-review.md and reference-sprint.md.

## Acceptance Criteria

- [ ] **AC1** Given help/status.md, when it is read, then it describes `status.py pillars` as printing counts and per-type percentages and claims no weighted health score. Fails on: HEAD help/status.md:125
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_docs_tell_truth.py::DocsTellTruthTests::test_status_help_claims_no_health_score
- [ ] **AC2** Given the skill, when `docgen.py reading-guides --check` runs, then it reports 0 drift items; reference-sprint.md's `decisions.py waive` example carries `--rationale`; help/sprint.md no longer says the close refuses on `unanswered`; and `persona_resolve.py resolve --render build` alone prints no sentence pointing at a contract above. Fails on: HEAD's 3 drift items and reference-sprint.md:210
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_docs_tell_truth.py::DocsTellTruthTests::test_examples_and_guides_match_the_tools
- [ ] **AC3** Given sprint.py and lib/run_state.py, when each is read, then `ReviewLedgerError` is neither defined nor caught, and project_upgrade.py says init writes `.version`. Fails on: HEAD's catches at sprint.py:4525, 5851 and 8924
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_docs_tell_truth.py::DocsTellTruthTests::test_no_dead_ledger_error_handler_remains
- [ ] **AC4** Given help/gate.md's CI and hook snippets, when each is read, then each names its script through `$CLAUDE_SKILL_DIR`; and `critic.py record --help` names `\;` as the way to keep a semicolon inside one finding. Fails on: HEAD help/gate.md:300, 308, 315 and 336, and a `critic.py record --help` silent on `\;`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_docs_tell_truth.py::DocsTellTruthTests::test_copied_snippets_run_and_the_escape_is_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
