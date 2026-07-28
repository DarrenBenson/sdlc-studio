# BG0335: _manual_acs_missing_evidence fails open on any exception, silently disarming the manual-evidence Done gate

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

The helper wraps its `verify_ac` import and `parse_story` call in 'except Exception: return []', so any import or parse failure is indistinguishable from 'every manual AC carries a passing human verdict'; for an all-manual story the gate then returns None and waves it to Done with nothing looked at, while the comment claims the opposite intent.

## Steps to Reproduce

Evidence (`_manual_acs_missing_evidence` lines 122-126, consumed by `_done_verify_gate` lines 152-159): Confirmed at transition.py 122-126: bare 'except Exception: return []' annotated 'a parse hiccup must not mask the gate'; `_done_verify_gate` treats [] as gate-satisfied and returns None when no executable ACs exist.

## Proposed Fix

Make the exception path fail loud: return a sentinel (or raise) that `_done_verify_gate` turns into a block reason such as 'manual-evidence check could not run (parse/import failure) - fix the story or tooling before Done', symmetric with the executable leg's honest degrade.

## Acceptance Criteria

### AC1: a parse failure blocks Done instead of waving it through

- **Given** an all-manual story with no recorded human verdict, and a `verify_ac.parse_story` that raises
- **When** `transition --status Done` runs
- **Then** the transition is refused and the refusal names the underlying failure, rather than the story reaching Done with nothing looked at
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ManualEvidenceGateFailsLoudTests::test_parse_failure_blocks_done_instead_of_waving_it_through

### AC2: a broken `verify_ac` import blocks Done for the same reason

- **Given** the same story and a `verify_ac` module that cannot be imported
- **When** the Done transition runs
- **Then** it is refused, because broken tooling is not a passed gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ManualEvidenceGateFailsLoudTests::test_import_failure_blocks_done

### AC3: the helper distinguishes "nothing owed" from "nothing looked at"

- **Given** `_acs_missing_evidence` called once over a story it cannot parse and once over a fully-evidenced one
- **When** the caller inspects the returned value
- **Then** the failure case reports an error and the healthy case does not, so two empty lists can no longer stand for a clean bill of health
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ManualEvidenceGateFailsLoudTests::test_helper_reports_the_failure_rather_than_an_empty_all_clear

### AC4: failing loud does not become unbypassable

- **Given** the same unparseable story
- **When** the transition is run with `--force`
- **Then** it succeeds, so the deliberate recorded override still works
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ManualEvidenceGateFailsLoudTests::test_force_still_overrides_the_loud_failure

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
| 2026-07-28 | delivery lane (RUN-01KYJZGZ) | Acceptance criteria authored; fix + regression tests landed |
