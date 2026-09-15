# BG0681: config.py show --key crashes on a key whose value holds an unquoted YAML date, the path BG0670 left

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py
> **Evidence:** Reproduced at 6fd766cc, 2026-09-15 (rc=1).
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0670 gave `show` (the whole config) a json default for date and datetime values; `show --key` still calls json.dumps without it, so `config.py show --key gate_budget` on this repository's own config exits 1 with a TypeError, because `gate_budget` holds `baseline_date.`

## Steps to Reproduce

1. `python3 .claude/skills/sdlc-studio/scripts/config.py show --key gate_budget` on this repository.
2. It exits 1 with TypeError: Object of type date is not JSON serializable.

## Proposed Fix

Pass the same json default on the --key path; pin both a nested date under a dotted key and a scalar date key.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0670 gave `show` (the whole config) a json default for date and datetime values; `show --key` still calls json.dumps without it, so `config.py show --key...
- [ ] **AC2** The proposed fix lands, pinned by a test: Pass the same json default on the --key path; pin both a nested date under a dotted key and a scalar date key.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
