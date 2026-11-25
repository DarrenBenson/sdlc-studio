# BG1758: BG1497 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py, tools/tests/test_lean_prd_refresh.py, changelog.d/BG1497.md
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T12:43:05Z

## Summary

BG1497 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] changelog.d/BG1497.md:13 now says the test "also fails on a read whose key it cannot resolve", which is false for an f-string key with a part built at run time: the scan reads it as the block its constant head names (test\_lean\_config\_keys\_read.py:266, "a map keyed at run time"), so `config.get(root, f"triage.{k.name}_cap", 1)` in a loop over `root.iterdir()`, added at triage\_noise.py:48, leaves the AC3 test green, while the same loop passing `k.name` bare fails it and a resolvable `f"triage.{k}_cap"` over a literal tuple fails it too\; the test's own docstring states the exception (lines 286-287, "A key built at run time inside a block ... reads as that block"), and round one's changelog stated it ("a key built at run time is not seen"), but this round's text drops it, so the release note promises a check the test does not make [LC-018]; RULINGS: CLOSED "AC3 is not met": the scan now follows `config.get`, `feature_enabled`, `load_config` and `project_override` through constants, loops, helper parameters and helper-returned blocks, and fails on an unresolved plain key. My three round-one mutants are killed: the `_cfg` helper key, the `load_config` block at route.py:100, and the helper block at route.py:308. `complexity.cognitive_high` and `version_check.*` are now in both files. CLOSED "the `report.enabled` row is filed in the Cost Baseline table": it has its own Sprint Report section (reference-config.md:341, its anchor unique, listed in the contents). MOVED "changelog.d/BG1497.md:7-8 says the test fails on any key": the block-through-a-helper clause is now true, but the same overclaim class survives in the new last clause, the ISSUES finding above. No regression from the newly declared defaults: each of the 32 new leaf keys is read either through `project_override`, which never reads config-defaults.yaml, or with a fallback equal to its declared value (`test_execution.*` matches EXECUTION\_DEFAULTS, `triage.enabled: null` keeps feature\_enabled on the schema), and `init` seeds from templates/config.yaml, not the defaults. The new rows I checked against code are TRUE: lessons, gate budget, flow bucket, version\_check, digests, provenance, wsjf. The test\_lean\_prd\_refresh.py change keeps the scripts-route check on a synthetic key. verify\_ac run --id BG1497 --dry-run: ac=3 pass=3. Config, docs and PRD modules: 143 passed. test\_check\_budgets.py and FrozenNotesTests: 19 passed. lint-style is clean. reference-config.md is 730 lines.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1497 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1497 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] changelog.d/BG1497.md:13 now says the test "also fails on a read whose key it cannot resolve", which is false for an f-string key with a part built at run time: the scan reads it as the block its constant head names (test\_lean\_config\_keys\_read.py:266, "a map keyed at run time"), so `config.get(root, f"triage.{k.name}_cap", 1)` in a loop over `root.iterdir()`, added at triage\_noise.py:48, leaves the AC3 test green, while the same loop passing `k.name` bare fails it and a resolvable `f"triage.{k}_cap"` over a literal tuple fails it too; the test's own docstring states the exception (lines 286-287, "A key built at run time inside a block ... reads as that block"), and round one's changelog stated it ("a key built at run time is not seen"), but this round's text drops it, so the release note promises a check the test does not make [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1497 AC1 still passes: Given the shipped reference-config.md, when it is searched for `sprint.fresh_session`, then the key is documented with its values and the default `sprint.py` uses (warn). Fails on: the key absent, or documented with a default the code does not use.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_fresh_session_is_documented_with_the_default_the_code_uses
- [ ] **AC3** BG1497 AC2 still passes: Given the shipped templates/config-defaults.yaml, when it is loaded, then `pricing.copilot_billing` is present with the value `lib/prices.py` falls back to when the key is unset. Fails on: the key absent from the defaults, or a shipped value that changes what an unconfigured project is billed as.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_copilot_billing_ships_with_the_default_the_code_uses
- [ ] **AC4** BG1497 AC3 still passes: Given a config key the scripts read that is missing from either reference-config.md or config-defaults.yaml, when the config-documentation test runs, then it fails naming the key and the file that lacks it; a key present in both passes. Fails on: the next undocumented key going unnoticed because the test checks only the two named here.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_a_key_the_code_reads_must_be_in_the_reference_and_the_defaults

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
