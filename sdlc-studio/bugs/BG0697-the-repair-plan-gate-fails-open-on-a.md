# BG0697: The repair-plan gate fails open on a zero-finding plan, an unparseable config and an unreadable round file, and its refusals name no remedy or crash on malformed input

> **Status:** Superseded
> **Closes with:** US0913 (D0264: superseded only once it ships; backlog sweep D0265, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/repair_plan.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/BG0673-delivery-engineering.txt (engineering seat); verdicts/BG0673-delivery-qa.txt (qa seat); verdicts/BG0678-delivery-engineering.txt (engineering seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md. Also queued in findings/todo.txt (BG0678 plan_authors fails open). The Closed and Verified bypass is BG0679; project_upgrade's kindless read is BG0685.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Fail-open reads: `record_repair_plan` accepts a plan with zero findings and zero entries (`repair_plan.py`:180-187, unchanged since 3f73ab64), and through the new CLI such a plan, once independently approved, opens the gate (the probed bug reached Fixed). `gate_enabled` reads an unparseable .config.yaml as off (`repair_plan.py`:89-95), unlike `_plan_gate_active.` `plan_authors` silently skips a round it cannot read (`repair_plan.py`:101, 111): with round one's file corrupted, its author reviewed round two and passed the gate (probed), and a corrupt latest round is reported as 'no repair plan is recorded', which names the wrong cause. Refusals and faults: the gate's refusal names no remedy, neither `repair_plan.py` record nor review (transition.py:1139-1142, `repair_plan.py`:324), where sibling gates in the same ladder name their command. The gate catches only ValueError: with the gate on and plan-review-verdicts.md unreadable, set, --dry-run and --force all exit 1 with a bare 'error: Permission denied', and --force cannot waive it because `_force_bypassed` catches only ValueError too (transition.py:1337-1345); the sibling test-plan gate turns the same fault into a named block (transition.py:2806-2815). The record verb crashes with an AttributeError traceback on plan entries that are not JSON objects (`repair_plan.py`:374-376 catches only OSError and ValueError) and splits a findings string into single characters with list() and records them (`repair_plan.py`:375); review raises a PermissionError traceback on an unwritable reviews directory (`repair_plan.py`:391 catches FileNotFoundError and ValueError only). Three changelog claims are true when run but unpinned: the dry-run refusal, the --force waiver record, and the CLI refusing a plan file whose verdict is not REJECT. A mutant dropping 'not force' from the gate (transition.py:1135) and one hard-coding REJECT in `_cmd_record` (`repair_plan.py`:374) both survive `test_repair_plan.py` and `test_transition.py.`

## Steps to Reproduce

1. Set `review.repair_plan_gate`: true. Write plan.json as {"verdict": "REJECT", "findings": [], "entries": []}; python3 .claude/skills/sdlc-studio/scripts/`repair_plan.py` record --unit <bug> --author alice --plan-file plan.json; `repair_plan.py` review --unit <bug> --verdict APPROVE --reviewer bob; transition.py set <bug> Fixed - it lands. 2. Record round two by erin, corrupt round one's JSON, then `repair_plan.py` review --unit <bug> --verdict APPROVE --reviewer alice - accepted, and the gate passes. 3. chmod 000 sdlc-studio/reviews/plan-review-verdicts.md; transition.py set <bug> Fixed --force - exit 1, 'error: Permission denied'. 4. `repair_plan.py` record with "findings": "abc" - three findings a, b and c are recorded; with "entries": [1] - AttributeError traceback.

## Proposed Fix

Refuse a plan with no findings. Read an unparseable config as on, as `_plan_gate_active` does. Refuse loudly on an unreadable round file and name it. Name `repair_plan.py` record and review in the gate's refusal. Catch OSError in the gate and in `_force_bypassed` and turn it into a listed block --force can waive. Validate the types of plan entries and findings in record; catch OSError in review. Pin the dry-run refusal, the --force waiver and the non-REJECT plan-file refusal through the CLI.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Fail-open reads: `record_repair_plan` accepts a plan with zero findings and zero entries (`repair_plan.py`:180-187, unchanged since 3f73ab64), and through the...
- [ ] **AC2** The proposed fix lands, pinned by a test: Refuse a plan with no findings.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0913 ships - planning: SUPERSEDED - repair-plan gate fails open: repair ledger deleted in batch 2; superseded only once US0913 ships (D0264) |
