<!-- close-status:begin -->
> **RUN-01M4R168 closed goal-reached.** 18 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

# RV0028 - Unified Review - 6.1.0 plus 6.2 on main, before the second 6.2 run

> **Reviewer:** Claude Opus 5.5, one read-only reviewer per leg | **Date:** 2026-10-19
> **Project version:** 6.1.0 | **Triggered by:** D0372 | **Predecessor unified:** RV0010 (2026-07-16)
> **Record:** [RV0028](RV0028-unified-review-before-the-second-6-2-run.md) holds every finding
> with its evidence and where it was filed.

## Headline

The product is ahead of its documents by about three months. The PRD, TRD and TSD each describe
the gate as one pre-commit hook. They miss the commit-msg and pre-push split, the boundary gates and
the move of run records and evidence into committed storage. The TRD and PRD both say only stories
execute Verify lines, when bugs do too. RUN-01M4R168 closed and was signed on 2026-10-16 (RPT0020).
Main is green.

| Leg | Verdict | Filed to |
| --- | --- | --- |
| PRD (25) | Requirements satisfied: **no**. Gaps: BG1063 (a documented gate no code reads), BG0959, BG1023, and `reconcile --scope` | CR0647, BG1063 |
| TRD (25) | Current: **no**. 1 Critical (TRD-1); the hook tier is undocumented; 3 ADRs stale, 1 unbuilt | CR0644, CR0645, BG1064 |
| TSD (24) | Current: **no**. A commit "runs the whole gate"; coverage 89% in CI, not 82% | CR0644, CR0646, BG1065 |
| Persona (11) | Current: **no**. None stale; Maya's card trails the work; no maintainer card | CR0648, BG1066, D0373 |
| Cross-doc | Concerns. Verifier scope, network paths and the gate tier disagree with the code | as above |

CRs: 15 Proposed (none past 14 days), 25 In Progress (all on Draft 6.2 epics), 520 Complete.
RFCs: none stalled. Agent instructions: clean. No auto-fixes; they land with CR0647. CR0649
extends the freshness census to the PRD and TSD so the next drift is caught when it happens.

## Rulings (operator, 2026-10-18 and 2026-10-19)

- **D0369, superseded by D0376: run two** is EP0288 (CR0635's remote gate, US1075-US1078),
  BG1061, and CR0644, the TRD and TSD gate refresh. Refine CR0644 before planning.
- **D0370:** devserver1's push gate with `--no-verify` stays in force until US1075 ships.
- **D0371:** once BG1061 lands, the agent copies studypc's `.local/lessons.md` over ssh. That
  needs studypc switched on.
- **D0373:** add a skill-maintainer persona card.
- **D0374:** run a stakeholder consult for persona-changing epics (EP0287 first).
- **D0375:** the pre-tag `--release`, record-green and tag-check steps stay manual.

## What is open

- **The lessons digest** predates RETRO0134's lessons until the log migrates (D0371, after BG1061);
  RPT0020 carries it as a known issue.
- **6.2 release blockers:** BG0962 and BG1000, the open High bugs. CI's corpus-verify job is red
  (BG1054).
- **Carried from RETRO0134, all not-stop-ship:** the Mediums are BG1050, BG1051, BG1052, BG1054,
  BG1058, BG1059 and BG1060. Filed since: BG1062 and BG1067 (filing frictions).

## Learned the hard way

- A test that enumerates a tool's spellings never converges; hold the input to exact allowed
  forms instead (BG1056).
- `git stash create` snapshots the working tree, not the index; build a judged commit with
  `git commit-tree "$(git write-tree)" -p HEAD`.
- A retro scaffolded before a `batch add` omits the late units; read its Batch line against the
  run state before closing (BG1059).
- Documents drift wherever no census reads them: the TRD's counted bands held, while the PRD's
  and TSD's pinned counts went stale (CR0649).

## History

- RV0028 (2026-10-19): this review.
- RUN-01M4R168 (RPT0020, signed 2026-10-16 by the operator, the command entered by the agent at
  the operator's instruction): ledger rulings, sealed runs, and gates that state their needs.
- RUN-01M45FV6 (RPT0019, signed 2026-10-05): sign seals only a page that still checks (BG0940).
