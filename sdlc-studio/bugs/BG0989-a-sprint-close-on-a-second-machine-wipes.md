# BG0989: A sprint close on a second machine wipes the committed LESSONS-SUMMARY.md: the project lessons log it regenerates from is gitignored, so it exists only on the machine that wrote it

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_committed.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/help/lessons.md, .claude/skills/sdlc-studio/reference-agentic-lessons.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-domain.md, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/reference-epic.md, .claude/skills/sdlc-studio/reference-operator-heuristics.md, .claude/skills/sdlc-studio/help/help.md, .claude/skills/sdlc-studio/lessons/_index.md, .claude/skills/sdlc-studio/scripts/README.md, .claude/skills/sdlc-studio/templates/workflows/release-gate.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, changelog.d/BG0989.md
> **Evidence:** homelab RUN-01M4B5HP close pre-flight, 2026-10-07: lessons-summary STOP; `lessons.py summary --dry-run` -> 'would write 0 open lesson(s)'; sdlc-studio/.local/lessons.md absent on studypc2; LESSONS-SUMMARY.md last regenerated 15a2c17 (2026-08-21) with 71 lessons
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T15:37:47Z

## Summary

The project-tier lessons log lives at `sdlc-studio/.local/lessons.md`, and `.local/` is gitignored, so the log exists only on the workstation that ran earlier closes. `LESSONS-SUMMARY.md` - the digest every sprint reads at start - IS committed, and the close regenerates it from that log. On any other checkout the log is absent: `lessons.py summary --dry-run` reports 'would write 0 open lesson(s)' over a committed summary listing 71, and a real close would run retro-extract (creating a fresh log holding only the current retro's lessons) and then regenerate the summary - silently replacing 71 lessons with 3. Nothing warns: the lessons-summary gate reads 'stale', and its remedy (regenerate) is exactly the destructive step. Observed in the homelab consuming project on 2026-10-07 (RUN-01M4B5HP, RETRO0017): the previous close (2026-08-21) ran on another workstation; this one, on studypc2, was stopped by the agent noticing the 71 -> 0 before running it. A project worked from more than one machine - the normal case for a solo operator with a laptop and a desktop - loses its lessons digest on the first close away from home.

## Steps to Reproduce

1. Run a sprint close on machine A (writes sdlc-studio/.local/lessons.md, commits LESSONS-SUMMARY.md)
2. Clone or pull the project on machine B
3. `lessons.py summary --dry-run` -> 'would write 0 open lesson(s)' while the committed summary lists N
4. `sprint.py close --retro RETROxxxx` on B regenerates the summary from a log holding only this retro's lessons

## Proposed Fix

Either (a) commit the project log (move it out of `.local/`, e.g. `sdlc-studio/retros/lessons.md`) - lessons are project knowledge, not machine-local state; or (b) refuse to regenerate when the log is absent or holds fewer open lessons than the committed summary lists, naming both counts and the likely cause ('the log is per-machine - copy it from the machine that ran the last close'). (a) fixes the class; (b) is the guard either way. A test: a committed summary with N lessons and no log -> the close refuses the regeneration and writes nothing.

## Acceptance Criteria

- [ ] **AC1** The project lessons log is read from and written to a committed path, `sdlc-studio/retros/LESSONS.md`, beside the summary built from it, so a fresh clone on another machine reads the lessons its committed summary lists
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_committed.py -k a_fresh_clone_reads_the_committed_log
  - **Verified:** yes (2026-10-07)
- [ ] **AC2** A project holding only the legacy `.local/lessons.md` has it moved to the committed path by the first `lessons` command (any but a `--global` one, `carry` and `violated` included) or by `retro extract`, with nothing left behind and a line saying to commit it; a project holding both refuses and names both files to merge by hand
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_committed.py -k legacy_log_is_moved
  - **Verified:** yes (2026-10-07)
- [ ] **AC3** `lessons summary` and the close's regeneration refuse to write a digest when the log does not hold a lesson the committed summary lists (open or closed, compared through the summary's own render-and-parse round trip), naming the missing ids; the log that built the summary is never refused, whatever its titles hold; closing a lesson still shrinks the digest, and `prune` removes what it deletes from the digest too
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_committed.py -k summary_guard
  - **Verified:** yes (2026-10-07)
- [ ] **AC4** The stale-summary gate's remedy no longer tells the operator to clear the digest when the log is missing, and every shipped doc names the committed path, with `.local/lessons.md` only as the legacy path migration reads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_committed.py -k remedy_and_docs_name_the_committed_path
  - **Verified:** yes (2026-10-07)

## Triage

- Reproduced at e2090297 in this repository: `lessons.py summary --dry-run` -> 'would write 0 open lesson(s)' over a committed LESSONS-SUMMARY.md listing 441, because `sdlc-studio/.local/lessons.md` is absent on this machine (the 2026-10-05 close ran on another). The next close here would have replaced 441 lessons with this retro's few. `summary_status`'s remedy for a missing log offers the destructive step ('run `lessons summary` to clear the digest'). The class is LL0029: a record kept in a gitignored working directory is not a record.
- Operator ruling (D0350): fix the class now on the fast-track, by moving the log to a committed path, with the guard in AC3 because the move alone does not protect a machine whose log has not been migrated yet. The guard keys on lesson ids present in the log, open or closed, so closing a lesson stays a legitimate shrink.
- Re-sized 3 -> 5 for the migration, the guard and the documentation sweep. Affects paths corrected to repository paths.

## Review round 1 (REJECT, 2026-10-07)

- The guard compared the log's raw title with the summary's parsed one, so a title with a bold lead-in and a dash, which the parser splits at the inner `**`, refused the log that built it. It now compares both sides after the summary's own render-and-parse round trip, and a lesson counts as held when its id and either its title or its gist match. Pinned through the CLI and the close's summary step.
- `carry` and `violated` neither moved nor read the legacy log. The move now runs on every non-global `lessons` command, which makes "any `lessons` command" true; the refusal when both logs exist covers every verb that reads the log.
- `prune` then `summary` refused for ever. Prune now removes the pruned lessons' lines from the committed digest.
- reference-agentic-lessons.md called the committed path the gitignored legacy one, and help/lessons.md still said the file is never committed; both corrected. The doc check now reads sentences, not lines, and covers the scripts and best-practices too.
- `retro extract` refused a two-log project after writing the class store; the refusal now comes first, and a classed lesson pins it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Groomed for the fast-track (D0350): reproduced against 441 lessons in this repository; tool-derived criteria replaced with four executable ones; Affects corrected and widened to the doc sweep; 3 -> 5 points |
| 2026-10-07 | Claude Opus 5.5 (engineering seat) | Before review: AC2 said `migrate --apply` moved the log, which was not built; AC2 now names the paths that do (any project-log `lessons` command, and `retro extract`, both tested), and migrate.py leaves Affects |
| 2026-10-07 | Claude Opus 5.5 (engineering seat) | Repaired after the round-1 REJECT: round-trip guard, migration on every non-global verb, prune drops from the digest, two doc claims corrected, extract refuses before any write; AC2 and AC3 restated; four tests added |
