# CR-0413: artifact.py new mints without any duplicate check, so a defect already on the backlog is re-filed silently; file_finding.py file already computes duplicate_warnings and the two creators should share it

> **Status:** Proposed
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py,.claude/skills/sdlc-studio/scripts/file_finding.py
> **Priority:** Medium
> **Type:** Feature
> **Size:** S

## Summary

{{what changes and why}}

## Impact

{{who this affects and what breaks}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |

## Detail

Hit while composing Sprint 2. During Sprint 1 I filed BG0271 ("the site-sweep test is unrunnable
inside a git worktree") with `artifact.py new`. BG0269, filed one day earlier by the previous
run's closing review, is the SAME defect: same root cause (a `worktrees` path component matching
anywhere in `SKIP_DIRS`), same file (`tools/tests/test_skill_tests_env.py`), same severity, same
points. Nothing warned. The duplicate was only noticed because `sprint breakdown` clustered the
two ids onto one shared file, which is the coupling analysis doing a job it was not built for.

`file_finding.py file` already computes `duplicate_warnings` (shared ids, similarity percentage)
and prints them at mint. `artifact.py new` - the creator this project's own AGENTS.md tells
agents to reach for ("create artifacts with `scripts/artifact.py new`") - has no such check. So
the recommended path is the one without the guard.

## Acceptance Criteria

- [ ] AC1: `artifact.py new` warns on a probable duplicate at mint, using the same detection as the finding filer
- **Given** a bug whose title and Affects closely match an existing non-terminal artefact
- **When** it is minted with `artifact.py new`
- **Then** the mint reports the candidate id, what is shared and the similarity, exactly as `file_finding.py file` does
- **Verify:** manual

- [ ] AC2: one implementation, not two
- **Given** both creators need the check
- **Then** the detection lives in one shared function both call, so the two cannot drift
- **Verify:** manual

- [ ] AC3: a warning, never a refusal
- **Given** a legitimate near-duplicate (a genuinely distinct defect in the same file)
- **Then** the mint still succeeds and the warning is advisory - the author decides
- **Verify:** manual

- [ ] AC4: authoring criteria onto a scaffolded artefact does not leave the placeholder behind
- **Given** an artefact minted with the `- [ ] {{criterion}}` acceptance-criteria scaffold
- **When** an author supplies the real criteria
- **Then** the scaffold block is replaced rather than left beside the new one - today an appended section leaves the placeholder in place and `validate check` errors on it (hit twice while filing these very findings)
- **Verify:** manual
