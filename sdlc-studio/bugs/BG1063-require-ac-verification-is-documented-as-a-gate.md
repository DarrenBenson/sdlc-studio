# BG1063: `require_ac_verification` is documented as a gate that aborts the completion cascade on a failed verification, but no code reads it

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-verify.md, .claude/skills/sdlc-studio/reference-outputs.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/scripts/constitution.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py, sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py, changelog.d/BG1063.md, docs/existing-users.md, changelog.d/BG1525.md
> **Evidence:** RV0028 finding PRD-2; config-defaults.yaml:98; reference-outputs.md:768; transition.py:1042-1049 reads `quality.done_requires_verified`.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:49:39Z

## Summary

The PRD (prd.md:368, :707, :727), reference-verify.md (lines 34, 46, 235, 301, 385), reference-outputs.md:770, reference-config.md:298, help/verify.md:311 and templates/config-defaults.yaml:117 describe `require_ac_verification` as the switch that makes `artifact.py close` run `verify_ac` and abort the cascade on failure. At HEAD no shipped script reads it: it appears only in a docstring (constitution.py:13) and as an example key in test_config.py. The live Done gate is `quality.done_requires_verified`, read by transition.py. A key a user can set that changes nothing is the false-assurance class LL0008 names.

## Steps to Reproduce

1. In a throwaway project, write a story In Progress whose one criterion is `- **Verify:** shell false`.
2. Set `require_ac_verification: true` and `quality: done_requires_verified: false` in
   `sdlc-studio/.config.yaml`, then `transition.py set US0001 Done`.
3. Repeat with `require_ac_verification: false` and no `quality` block.

Measured at HEAD 3791e5193: step 2 sets Done with only the `quality.done_requires_verified=false`
advisory, though the documented key asks for the gate; step 3 is refused by the Done gate,
though the documented key turns it off. The key changes nothing either way.

## Proposed Fix

Retire the key, since `quality.done_requires_verified` is the gate the documents describe:
register it in `sdlc_md.RETIRED_CONFIG_KEYS` with `quality.done_requires_verified` as what
replaced it, so `migrate --apply` strips it; remove it from config-defaults.yaml and every
reference and help page, pointing at `quality.done_requires_verified`; fix constitution.py's
docstring; file `changelog.d/BG1063.md` under `Breaking`, which the breaking inventory requires
of a registered retirement; and update the PRD's Verify AC criterion, its block and row, and the
PRD test that uses BG1063 as its held-criterion example.

## Acceptance Criteria

- [ ] **AC1** Given a project `.config.yaml` holding `require_ac_verification: true` beside `quality: done_requires_verified: false`, when `migrate.py --apply` runs, then the key is removed and the removal reported, and `quality.done_requires_verified` is kept. Fails on: HEAD, whose `sdlc_md.RETIRED_CONFIG_KEYS` lacks the key, so migrate keeps a line that changes nothing (measured: with it set true, a story with `shell false` reached Done).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_require_ac_verification_is_retired_by_migrate
- [ ] **AC2** Given the shipped skill, when every reference-*.md, help page and template is read, then none names `require_ac_verification`, config-defaults.yaml declares no such key, and reference-verify.md's gated-completion section names `quality.done_requires_verified`. Fails on: HEAD's config-defaults.yaml:117, reference-verify.md, reference-outputs.md:770, reference-config.md:298 and help/verify.md:311.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_require_ac_verification_is_not_documented
- [ ] **AC3** Given the key registered as retired, when the breaking inventory reads the pending fragments, then a `Breaking` line names `require_ac_verification`. Fails on: a fix that registers the key and files its fragment under `Fixed`.
  - **Verify:** pytest tools/tests/test_lean_breaking_inventory.py::BreakingInventoryTests::test_every_registered_retirement_is_disclosed
- [ ] **AC4** Given BG1063 at Fixed, when the PRD rules are read, then the Verify AC criterion names `quality.done_requires_verified`, is ticked and held by no bug, its block and Feature row read Complete, and the held-criterion test no longer depends on a BG1063 hold. Fails on: a fix that reaches Fixed with the PRD untouched (`criterion 3 is held by BG1063, which is Fixed`).
  - **Verify:** shell python3 -m pytest -q -p no:cacheprovider tools/tests/test_lean_prd_refresh.py::PrdRulesTests::test_the_engagement_floor_tracks_bg0959 tools/tests/test_lean_prd_refresh.py::PrdRulesTests::test_a_held_criterion_names_the_bug_its_words_describe

## Impact

An operator who sets the documented key believes they changed a gate; nothing changes.

## Notes

- From US1104 (2026-11-01): tools/tests/test_lean_prd_refresh.py::PrdRulesTests reads this bug's status. When BG1063 reaches Fixed, the PRD's held criterion must be ticked and its row and block must read Complete in the same commit, or the test goes red. Add sdlc-studio/prd.md to this unit's Affects when it is planned (done in the run twenty-four groom).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-23 | Sam Eriksson (qa) | Groomed for run twenty-four: reproduced at HEAD through `transition.py set` both ways; the fix chooses retirement through `RETIRED_CONFIG_KEYS`; the one `-k` criterion replaced by four executable ones (migrate, docs, Breaking disclosure, PRD); Affects adds sdlc_md.py and reference-config.md and drops test_retired_config_keys.py (never existed) and test_constitution.py (reads no such text); 2 to 3 points |
| 2026-11-24 | Claude Opus 5.5 (run twenty-four orchestrator) | Affects + docs/existing-users.md: retiring the key makes the upgrade page's every-retired-surface test require its row |
| 2026-11-24 | Claude Opus 5.5 (run twenty-four orchestrator) | Affects + changelog.d/BG1525.md: the round-one review found the unreleased BG1525 fragment still lists the retired key among the live gate keys |
