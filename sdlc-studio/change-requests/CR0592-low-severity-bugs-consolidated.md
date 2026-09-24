# CR-0592: Low-severity bugs (consolidated)

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-09-21
> **Consolidation:** low-severity-bugs
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A themed consolidation of Low-severity findings that individually do not warrant a standalone artefact (triage noise control, schema v3). Triage the batch, then action or reject as one.

## Impact

Each finding here is Low-severity on its own; the batch is triaged, then actioned or rejected as one. Left unconsolidated, the same findings would each mint an artefact and drown the real signal.

**Points:** 3

## Consolidated Findings

- **conformance hard-codes the Verified positive vocabulary that sdlc_md now owns, so the two will diverge the next time it changes**: BG0733 named the set of `Verified:` values that mean satisfied as `sdlc_md.VERIFIED_POSITIVE`, a frozenset of `yes` and `manual`. `conformance.py` carries the same pair as a literal tuple and compares against it independently. Two code paths now decide the same question from two definitions - LL0016 in the lessons registry is exactly this - and the next value added or removed will be added or removed in one of them.
- **the abandoned lens costs the triage sweep a quarter-second because every artefact is date-parsed, though only the children of In Progress requests are ever read**: BG0722's `abandoned` lens needs each artefact's last-touched date, so `_scan` now runs `_last_date` over all 2526 artefacts rather than the backlog subset. Measured by the reviewing seat, `triage()` went from 0.284s to 0.532s on this repository. Both `status` and `sprint plan` call it interactively. The `dates` map is only ever read for artefacts named as children by an In Progress cr/rfc - seven of them here - so almost all of that parse is discarded.
- **sprint plan --bugs Open --write --goal design crashes in capacity_report**: TypeError: '>' not supported between NoneType and int in capacity_report (sprint.py ~623), inside build_plan. Found by the US0870 review; pre-existing.
- **allocation_lock fails open after 10 seconds**: sdlc_md.allocation_lock yields without the lock after 10s of contention. With the lock held for 12s, 39 of 65 concurrent critic verdict rows were lost (US0873 review probe). The review ledger, id allocation and run state all rest on it. Raise, or create with O_EXCL, rather than proceed unlocked.
- **A re-run close files a new handover instead of refreshing its own**: RUN-01M36R3D's close ran three times, since US0876 allows a re-run, and filed HO0082, HO0083 and HO0084 for the same run. The report is keyed by run (US0877) but the handover is not.
- **Retro appenders leave a trailing blank line that markdownlint refuses**: `retro.py accuracy --write` and the close's handoff line each end the retro with a blank line (MD012), so the next commit is refused until the file is trimmed by hand. It happened three times on RUN-01M36R3D. The sprint report had the same defect and now ends with exactly one newline.
- **The close still refuses a goal-verdict note that states a round count**: The one-pass close (US0876) keeps an early refusal: a goal-verdict note may not state a number of rounds that the run-level review_rounds ledger contradicts (stated_round_count). The review marked this prose policing for deletion. It cost RUN-01M36R3D one refused close, over a note saying 'at most two rounds'.
- **A lesson class whose runs span two clones never retires**: `lessons.close_pass` retires a class only when this clone's run archive knows its recording run and every hit run. A class recorded in one clone and hit in another is known to neither, so it stays active for ever (the safe direction: it stays injected).
- **The report's Lessons appendix names the project store as its source when the bundled seed was read**: On a project with no `sdlc-studio/lessons.jsonl`, the lessons read comes from the skill's bundled seed, but `_lessons_section` still cites `sdlc-studio/lessons.jsonl`, a file that does not exist.
- **An unreviewed batch unit's review rounds move at the seal**: A batch unit with no review in the run has no `review_base`, so its round count reads 0 while the run is open and the ledger's rows once sealed; the report's figure moves at the seal.
- **Six stamped criteria still state push-boundary behaviour that US0881 moved to the release boundary**: US0881 moved module-alone, release-rehearsal and revert-check to the release boundary and retargeted their tests, keeping node names for the stamps. The criteria beside those stamps still say push: BG0649 AC2 and AC3, US0666 (release-rehearsal runs at both), US0674 AC1 (revert-check at push or release), BG0664 AC1 (the shim's module-alone push refusal) and BG0641 AC4 (the 'about ten minutes' floor). Two node names also claim push while testing release: test_gate.py test_the_rehearsal_lane_runs_at_the_push_and_release_boundaries and test_the_push_boundary_runs_every_module_alone_and_names_the_one_that_fails.
- **US0063 AC2's stamp selects nothing**: its Verify line is `pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_check.py`, which `verify_ac.py stamps` reports as selecting no test. Found by the US0905 review; pre-existing and unrelated to that diff.
- **A unit carried at the review cap still reads as an unanswered REJECT at the close**: `critic record` carries the unit and files a bug holding its findings, but writes no repair closure, so `sprint close` refuses on every carried unit until each finding is closed by hand with `critic repair ... filed: <bug>`. It cost RUN-01M39MC0 four hand repairs across four carried units.
- **`critic repair`'s refusal offers ordinals it then refuses**: the refusal lists findings from every verdict on the unit (#1 to #8), but an ordinal resolves only against the latest verdict (3 findings), so `#7` as offered is refused with 'the verdict raised 3'. A quoted prefix works, but must start at the finding's own opening words, including `non-blocking:`.
- **A graduated lesson's CR fails markdownlint, so the close's own output is refused at commit**: lessons._graduation_cr writes the 'Hits:' label directly above its bullet list with no blank line between, so every CR a close graduates fails MD032 and the commit of the close's outputs is refused until the file is fixed by hand. RUN-01M39MC0's close graduated CR0595, CR0596 and CR0597 and all three were refused.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Consolidation opened |
| 2026-09-21 | US0853 AC2 | The two BG0463 survivors this bucket had absorbed are minted as their own artefacts, BG0734 and BG0735, and removed from here. US0853's AC2 says nothing carries forward as a bullet inside another artefact, and delivery review was right that a bucket is exactly that. This page keeps whatever else it consolidates. |
| 2026-09-24 | Claude Opus 5.5 | US0063 AC2's stale stamp added, from the US0905 review (RUN-01M39MC0) |
| 2026-09-24 | Claude Opus 5.5 | Two `critic` carry and repair findings added from the RUN-01M39MC0 close |
