# US1214: A verify stamp records the Affects digest, and a transition accepts a current stamp without a re-run

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0679
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0331
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A verify stamp records the Affects digest, and a transition accepts a current stamp without a re-run
**So that** CR0679 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A verify run records the digest of the unit's Affects

- **Given** a unit with Affects and green criteria
- **When** `verify_ac.py run --id <id>` is run, one Affects file is then edited, and the command is run again; and separately it is run with `--dry-run`
- **Then** each written report entry carries a digest of the content of the unit's Affects files, the two digests differ, and the dry run records none. Fails on: an entry with no digest, or a digest that does not change when an Affects file's bytes change
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::AffectsDigestStampTests::test_a_run_records_the_affects_digest_with_its_stamp

### AC2: A transition accepts a green stamp at the current digest without a re-run

- **Given** a unit whose verify stamp is green at the current Affects digest, and whose verifier would leave a marker file if it ran
- **When** `transition.py` moves the unit to Done
- **Then** the unit reaches Done and no marker file is written. Fails on: the criteria run a second time over files that have not changed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::AffectsDigestStampTests::test_a_current_stamp_is_accepted_without_a_rerun

### AC3: A stamp at another digest re-runs, and a red re-run refuses

- **Given** a unit stamped green, one of whose Affects files is then edited so a criterion fails; a second unit edited so its criteria still pass; and a third whose report entry carries no digest
- **When** `transition.py` moves each to Done
- **Then** each unit's criteria are run again; the first is refused naming the red criterion; the second and third reach Done with the stamp renewed at the current digest. Fails on: the earlier green accepted for changed files, or an entry with no digest read as current
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::AffectsDigestStampTests::test_a_mismatched_or_absent_digest_reruns_and_a_red_refuses

### AC4: A light-tier brief prints a current stamp's result without a re-run

- **Given** a light-tier unit whose verify stamp is green at the current Affects digest and whose verifier would leave a marker file if it ran, and the same unit after one Affects file is edited
- **When** `critic.py brief --unit <id> --seat qa` is run in each state
- **Then** the first brief's RESULTS section gives the stamped result with the commit of the stamp and no marker file is written; the second runs the verifiers again. Fails on: a light-tier brief re-running a current stamp, or printing a stamp taken at another digest
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefStampTests::test_a_light_brief_prints_a_current_stamp_without_a_rerun

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
