# CR-0416: the engagement floor cannot see work for a unit the commit message never names: a git add -A that sweeps in a concurrently-edited unit attributes its files to whichever id the subject happens to carry

> **Status:** In Progress
> **Decomposed-into:** EP0156
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py,.githooks/commit-msg
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

Happened to me in Sprint 2, in commit `6ae0c80e`. I finished BG0276, started its background
commit, then began BG0268 while that ran. The BG0276 commit's `git add -A` staged BG0268's
in-flight edits too, so BG0268's source change, its test class and its changelog fragment all
landed under a subject naming only BG0276, with no `Refs: BG0268` trailer.

Nothing caught it, and nothing could:

- The **commit-msg hook** requires a `Refs:` trailer per id only when the SUBJECT names two or
  more ids. This subject named one, so no trailer was demanded.
- The **engagement floor** attributes a commit's files to the ids the message declares. BG0268's
  files are therefore attributed to BG0276, and BG0268 reads as a unit with no commits behind it.

The signal that would have caught it was available and unused: every file in that commit has an
owning unit, because each unit declares `Affects`. A commit touching files that belong to a unit
the message never names is exactly the shape of a mis-attribution, and the floor already knows
both halves.

This is not only an operator-discipline problem. Any concurrent-edit workflow - a background
commit while the next unit is being written, which this project does constantly - produces it.

## Impact of the mis-attribution

The per-id attribution the floor exists to provide becomes quietly wrong: one unit is credited
with another's work, and the under-credited unit looks undelivered. Every later reader of
`git log` inherits the error, and the retro's per-unit accounting rests on it.

## Acceptance Criteria

- [ ] AC1: a commit touching a unit's Affects while naming a different unit is reported
- **Given** a commit whose changed files fall under the `Affects` of a unit that the subject and the `Refs:` trailers never name
- **When** the commit-msg gate runs
- **Then** it names that unit and asks for a `Refs:` trailer, so the attribution is stated rather than guessed
- **Verify:** pytest tools/tests/test_commit_msg_hook.py::UnnamedUnitAttributionTests::test_a_file_owned_by_an_unnamed_unit_is_reported

- [ ] AC2: a warning, not a refusal, where ownership is ambiguous
- **Given** a file claimed by several units' `Affects`, or by none
- **Then** the gate does not refuse on it - shared and unowned files are normal, and a gate that blocked on them would be disabled within a week
- **Verify:** pytest tools/tests/test_commit_msg_hook.py::UnnamedUnitAttributionTests::test_a_shared_or_unowned_file_does_not_refuse

- [ ] AC3: the historical mis-attribution in this repo is recorded, not silently corrected
- **Given** commit 6ae0c80e carries BG0268's delivery under BG0276's name
- **Then** the record says so where a reader of either unit will meet it, rather than pushed history being rewritten
- **Verify:** manual
