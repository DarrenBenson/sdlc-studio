# US0759: `config.py show --sources` marks each key in force as a skill default or project-set

> **Status:** Ready
> **Delivers:** CR0534
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_show_sources.py, changelog.d/US0759.md
> **Epic:** EP0233
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** `config.py show --sources` to mark every key in force as a skill default or set by my project
**So that** I can see which settings my project chose without reading `config-defaults.yaml` beside my own `.config.yaml`

## Summary

Reshaped by D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from a 5-point story that also carried a meaning column, decision ids per key and retro proposals; those are dropped. `config.py show` already prints the merged configuration (`cmd_show`), and `load_config` already merges the skill defaults with the project file (`_deep_merge`), so the source of each leaf is known at the merge and only needs printing. No new key, file, gate or report section.

## Premise at HEAD

Executed at `85042135`:

```text
$ python3 .claude/skills/sdlc-studio/scripts/config.py show --sources
usage: config.py [-h] [--root ROOT] {show} ...
config.py: error: unrecognized arguments: --sources
exit=2
```

## Acceptance Criteria

- [ ] **AC1** Given a fixture project whose `sdlc-studio/.config.yaml` sets `coverage.unit: 75`, when `config.py show --sources --root <fixture>` runs, then it exits 0 and prints one line per leaf key naming the dotted key, its value and `project` for `coverage.unit` and `default` for a key the file does not set (e.g. `review.policy`). Fails on: HEAD exits 2 `unrecognized arguments: --sources`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_show_sources.py::ConfigShowSourcesTests::test_a_project_key_and_a_default_key_are_marked
- [ ] **AC2** Given that fixture, which sets one leaf of the `coverage` section, when `config.py show --sources` runs, then only `coverage.unit` reads `project` and its sibling `coverage.integration` reads `default`. Fails on: marking a whole section `project` when any one of its leaves is set
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_show_sources.py::ConfigShowSourcesTests::test_a_sibling_of_an_overridden_leaf_stays_default
- [ ] **AC3** Given the same fixture, when `config.py show` runs without `--sources`, then its output is the JSON it prints today, byte for byte. Fails on: changing the plain `show` output to carry sources
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_show_sources.py::ConfigShowSourcesTests::test_plain_show_is_unchanged

## Technical Notes

Derive the source per leaf by walking the parsed project file against the merged config, not by a second merge. `reference-config.md` gains one sentence naming the flag. Out of scope (D0291): a meaning column, decision ids per key, and any retro proposal.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | sdlc-studio | Retitled: was 'A command prints every configuration key in force with its value, its source and its meaning' |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
