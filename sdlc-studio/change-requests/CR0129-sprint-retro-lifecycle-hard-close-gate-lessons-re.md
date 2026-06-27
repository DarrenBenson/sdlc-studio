# CR-0129: sprint retro lifecycle: hard close gate, lessons re-validation, rolling summary of learnings

> **Status:** Proposed
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Depends on:** CR0125

## Summary

`reference-sprint.md` step 7 calls the closing retro "unconditional", but it is doctrine, not a
mechanical gate, so it is silently skipped: a consuming repo (466 CRs, 533 stories) and a second consuming repo have
**no `retros/` directory at all**, and a third consuming repo has been run (state files present) yet recorded
**zero lessons**. The valuable lessons that did accrue sit in gitignored, per-worktree
`.local/lessons.md` files that never travel and have never been promoted to the skill tier
(`lessons add --global` has never been used). The learning loop the operator wants is half-built.

This CR makes the retro a real lifecycle with five script-backed steps, so a sprint cannot report
success without learning being captured, re-validated, and distilled to something cheap to read next
time:

1. **Retro is a hard close gate.** `autosprint` / `sprint` / `review` close refuses to report
   success until `retros/RETRO{next}.md` exists for the batch, mirroring the existing reconcile-drift-0
   gate. This is the [[LL0008]] discipline (a tool must not report success it did not achieve) applied
   to the closing gate itself.
2. **Review lessons after every sprint and write them to files.** At retro, the accrued
   `.local/lessons.md` entries are reviewed and the durable ones written into the committed retro.
3. **Re-validate open lessons; close the obsolete.** Read all accumulated lessons and re-check each
   still-open issue against current reality; close (mark superseded/resolved) the ones no longer
   valid, so the log does not grow into stale noise. This is `lessons prune` generalised from
   "by epic age" to "by continued validity".
4. **Produce a rolling Summary of Learnings.** Distil the still-valid lessons into a short summary
   artefact (e.g. `sdlc-studio/retros/LESSONS-SUMMARY.md`) - the cheap, high-signal digest. This is
   progressive disclosure applied to lessons: the full log is the archive, the summary is what is
   loaded routinely (the same token-vs-context trade-off as the index-archive work in [[CR0125]]).
5. **Read the summary at the start of any new sprint** (plus `lessons recall`), replacing the
   load-everything approach. Generalisable lessons are surfaced here for `lessons add --global`
   promotion, closing the harvest gap so cross-project wisdom stops being stranded.

The whole point is determinism: each step is backed by `scripts/lessons.py` / a retro helper, not
left to an agent honouring prose. The close gate, the re-validation pass, and the summary
generation are mechanical; the judgement (which lesson is still valid, which generalises) stays the
agent's, but the steps cannot be skipped without a loud failure.

## Acceptance Criteria

- [ ] the sprint/autosprint/review **close gate fails loud** (non-zero, no success report) if the
      batch's `retros/RETRO{next}.md` is absent, mirroring the reconcile-drift-0 gate ([[LL0008]])
- [ ] `scripts/lessons.py` gains a **re-validation** verb that lists open lessons for the agent to
      confirm/close and records the close (status transition), generalising `prune --older` to
      validity-based closure; deterministic and idempotent
- [ ] a **summary generator** (script-backed) refreshes `retros/LESSONS-SUMMARY.md` from the
      still-valid lessons at retro close; the summary is committed (unlike `.local/lessons.md`)
- [ ] the sprint **start** step reads `LESSONS-SUMMARY.md` + `lessons recall` instead of loading the
      full log; `reference-sprint.md` step 7 updated to describe the full lifecycle
- [ ] the retro step prompts for `lessons add --global` promotion of any generalisable lesson, with
      `--origin` set, so the harvest gap closes
- [ ] **deterministic where possible** ([[LL0008]]): the gate, re-validation, and summary refresh are
      backed by scripts with unit tests; only the validity/generalisability judgements remain
      agent-made, and those are explicitly named
- [ ] unit tests: close-gate fails without a retro then passes with one; re-validation idempotency;
      summary regenerates deterministically from a fixture lesson set
- [ ] docs: `reference-sprint.md`, `help/sprint.md`, `help/lessons.md`, `reference-agentic-lessons.md`
      updated; CHANGELOG `[Unreleased]` entry ([[LL0004]])

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-27 | field | Created via `new` (deterministic) |
