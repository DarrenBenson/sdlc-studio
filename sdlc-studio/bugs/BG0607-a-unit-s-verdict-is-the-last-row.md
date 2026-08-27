# BG0607: A unit's verdict is the LAST row written, so one seat's APPROVE recorded after another seat's REJECT makes a rejected unit read approved

> **Status:** Fixed
> **Supersedes:** BG0620
> **Severity:** High
> **Verification depth:** functional (seven criteria, each with its own mutant executed and killed: four over the roll-up and the repair state it feeds, one paired control on the per-rejection closure match, and two over the DECISION LOG, because the residue is resolved by a recorded waiver rather than by code. The backfill this unit first attempted was REJECTED at review and REMOVED: 24 of its 53 closures cited, as their evidence, a cross-seat approval whose brief fingerprint differs from the rejection's - the exact row this unit's own code refuses to treat as answering. The record was made prettier, not truer, and reverting it is the finding)
>
> **Points:** 8
> **Depends on:** BG0621, BG0618
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, sdlc-studio/decisions.md, docs/known-issues.md, docs/release-notes-v5.0.1.md
> **Evidence:** RUN-01M0JD1W close, 2026-08-24. Eighteen delivery verdicts recorded across three seats; three units with a recorded REJECT print APPROVE from `critic.py show`. The blocking findings behind those REJECTs were real and were repaired, which is how the masking was noticed at all.
> **Created:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`critic.py show` and the gates that read it take a unit's standing verdict to be the most recently recorded row. A panel is three seats, recorded one after another, so a unit REJECTed by the engineering seat and APPROVEd by the product seat reads APPROVE whenever the product row happens to be written second. The verdict then depends on the order the recorder was invoked in, not on what the panel found. Both rows are in the log and honest; the roll-up is what is wrong.

## Steps to Reproduce

1. Record a REJECT for a unit from one reviewer. 2. Record an APPROVE for the same unit from a DIFFERENT reviewer. 3. Run `critic.py show --unit <id>`: it prints APPROVE, and the REJECT is invisible to every caller reading the head row. Observed on RUN-01M0JD1W, 2026-08-24: US0671, US0675 and US0676 each carry a seat REJECT from delivery round 2 and each reads APPROVE because the product seat was recorded last. US0674 reads REJECT only because the product seat happened to be the rejecting one.

## Proposed Fix

Key the retraction on the BRIEF FINGERPRINT, and backfill the residue. Two halves:

1. A REJECT is retired by a later APPROVE carrying the SAME `Brief` fingerprint. The fingerprint hashes the brief the seat was handed, which embeds the seat charter, so it identifies the seat AND the round without conflating two seats - unlike the reviewer string, which this repository writes differently per round. Measured on this corpus: 81 units carry an unanswered REJECT under the reviewer string and 49 under the fingerprint, a strict superset recovering 32 and losing none.

2. The 49 that remain are largely the case AC1 exists for - one seat rejecting, a different seat approving, and no recorded repair answering the rejection. Those are real masked rejections, not rule failures, and closing them means recording the repair that answered each. Land the roll-up WITHOUT the backfill and the conformance lane goes red on every unit the backfill has not reached, which is what happened when this shipped and was withdrawn.

Report the panel as its members - `US0675 REJECT (qa, engineering) / APPROVE (product)` - so a split panel is visible as a split rather than resolved silently by write order. Keep the per-row log exactly as it is; only the roll-up changes.

## Acceptance Criteria

- [x] **AC1** Given a unit with a REJECT from one seat and an APPROVE from another, when the standing verdict is read, then it is the REJECT - a panel is several seats recorded one after another, and taking the last row written made the verdict a fact about the order the recorder was called in
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_one_seats_approve_does_not_retire_anothers_reject
  - **Verified:** yes (2026-08-26)
- [x] **AC2** Given a seat that REJECTED and later APPROVED the same unit, when the standing verdict is read, then it is the APPROVE - the paired control and the boundary: a seat may change its mind, and refusing that would make every REJECT permanent. The key is the BRIEF FINGERPRINT and not the reviewer string, because this repository names seats per round
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_a_seat_may_retire_its_own_reject
  - **Verified:** yes (2026-08-26)
- [x] **AC3** Given a unit carrying TWO unanswered rejections, when the standing verdict is read, then the LATEST is reported - the earliest reading leaves 18 units non-conformant against the latest's 19, and the unit it drops is US0671, the first one this bug's own Steps to Reproduce name as masked
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_the_latest_unanswered_reject_is_the_one_reported
  - **Verified:** yes (2026-08-26)
- [x] **AC4** Given a unit carrying SEVERAL unanswered rejections, when its repair state is computed, then every one of them contributes its findings to `outstanding` - this roll-up creates multi-reject units for the first time, and deriving outstanding from the standing row alone left 118 findings invisible to this function, to the conformance lane that calls it and to every checker built on either
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_every_unanswered_rejection_contributes_its_findings
  - **Verified:** yes (2026-08-26)
- [x] **AC5** Given a repair recorded against an EARLIER rejection, when a later rejection is raised, then the earlier repair does not answer it - the paired control, and sharper than it looks: a closure may name its finding by ORDINAL, and an ordinal is positional, so pooling closures across rejections makes an ordinal silently answer another round's first finding
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClosureResolutionTests::test_a_repair_does_not_answer_a_LATER_rejection
  - **Verified:** yes (2026-08-26)
- [x] **AC6** Given the nineteen units this roll-up leaves carrying a rejection no seat ever answered, when the shipped whole-workspace conformance lane runs, then it is GREEN at 608/690 with none non-conformant - reached by a recorded WAIVER naming each unit, because those rejections cannot be closed retroactively without fabricating evidence, and a backfill attempting exactly that was rejected at review for citing the cross-seat approval this rule exists to refuse
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/conformance.py check
  - **Verified:** yes (2026-08-26)
- [x] **AC7** Given each of those nineteen units, when the decision log is read, then a waiver names that unit by id and states what is set aside - the historical gap and not the rule. A waiver nobody can read back to a unit is an exemption rather than a decision
  - **Verify:** shell python3 -c "import pathlib,sys; t=pathlib.Path('sdlc-studio/decisions.md').read_text(); sys.exit(0 if all('critiqued:'+u.lower() in t for u in 'US0577 US0578 US0580 US0583 US0585 US0591 US0597 US0629 US0630 US0631 US0632 US0645 US0662 US0663 US0664 US0665 US0666 US0671 US0676'.split()) else 1)"
  - **Verified:** yes (2026-08-26)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `critic.py`, return `latest` from `verdict_for`, ignoring `_unanswered_rejects` | Given a unit with a REJECT from one seat and an APPROVE from another, when the standing verdict is read, then it is the REJECT - a panel is several seats recorded one after another, and taking the last row written made the verdict a fact about the order the recorder was called in |
| AC2 | in `critic.py`, replace the `brief` comparison in `_unanswered_rejects` with a `reviewer` comparison | Given a seat that REJECTED and later APPROVED the same unit, when the standing verdict is read, then it is the APPROVE - the paired control and the boundary: a seat may change its mind, and refusing that would make every REJECT permanent. The key is the BRIEF FINGERPRINT and not the reviewer string, because this repository names seats per round |
| AC3 | in `critic.py`, replace `unanswered[-1]` with `unanswered[0]` in `verdict_for` | Given a unit carrying TWO unanswered rejections, when the standing verdict is read, then the LATEST is reported - the earliest reading leaves 18 units non-conformant against the latest's 19, and the unit it drops is US0671, the first one this bug's own Steps to Reproduce name as masked |
| AC4 | in `critic.py`, replace `repair_state`'s rejection list with the standing verdict alone | Given a unit carrying SEVERAL unanswered rejections, when its repair state is computed, then every one of them contributes its findings to `outstanding` - this roll-up creates multi-reject units for the first time, and deriving outstanding from the standing row alone left 118 findings invisible to this function, to the conformance lane that calls it and to every checker built on either |
| AC5 | in `critic.py`, merge the closures across every rejection in `repair_state` instead of matching them per rejection | Given a repair recorded against an EARLIER rejection, when a later rejection is raised, then the earlier repair does not answer it - the paired control, and sharper than it looks: a closure may name its finding by ORDINAL, and an ordinal is positional, so pooling closures across rejections makes an ordinal silently answer another round's first finding |
| AC6 | in `sdlc-studio/decisions.md`, delete a waiver row so one of the nineteen units is no longer set aside | Given the nineteen units this roll-up leaves carrying a rejection no seat ever answered, when the shipped whole-workspace conformance lane runs, then it is GREEN at 608/690 with none non-conformant - reached by a recorded WAIVER naming each unit, because those rejections cannot be closed retroactively without fabricating evidence, and a backfill attempting exactly that was rejected at review for citing the cross-seat approval this rule exists to refuse |
| AC7 | in `sdlc-studio/decisions.md`, replace a waiver subject with a bare `rule:conformance:critiqued` carrying no unit id | Given each of those nineteen units, when the decision log is read, then a waiver names that unit by id and states what is set aside - the historical gap and not the rule. A waiver nobody can read back to a unit is an exemption rather than a decision |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
