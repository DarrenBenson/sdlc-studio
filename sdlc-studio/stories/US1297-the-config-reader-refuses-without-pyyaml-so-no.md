# US1297: The config reader refuses without PyYAML, so no command reads a present config as the shipped defaults

> **Status:** Done
> **Risk-class:** elevated
> **Delivers:** CR0731
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py, changelog.d/US1297.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py, .claude/skills/sdlc-studio/scripts/migrate.py
> **Epic:** EP0368
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The config reader refuses without PyYAML, so no command reads a present config as the shipped defaults
**So that** CR0731 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The library reader refuses a present config when PyYAML is absent

- **Given** a project whose `sdlc-studio/.config.yaml` sets a key away from its shipped default, in a process where `yaml` cannot be imported
- **When** the `lib/sdlc_md.py` reader every script reads project config through is asked for that key
- **Then** it raises its named refusal, whose message names PyYAML and the command that installs it, and never returns the default. Fails on: one warning on stderr and the shipped default handed back
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::RequiredPyYamlTests::test_a_present_config_is_refused_not_defaulted_without_pyyaml
- **Verified:** yes (2026-11-19)

### AC2: config.py prints no defaults for a config it cannot read

- **Given** the same project and the same missing import
- **When** `config.py show` is run, and `config.get` is called for the overridden key
- **Then** the command exits non-zero naming PyYAML and prints no configuration, and `get` raises the refusal in place of returning the caller's default. Fails on: the warn-and-default that `GracefulDegradeTests` pins today for an absent PyYAML
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::RequiredPyYamlTests::test_config_refuses_without_pyyaml_and_prints_no_defaults
- **Verified:** yes (2026-11-19)

### AC3: A shipped command exits non-zero with one refusal line

- **Given** the same project, and an interpreter that cannot import `yaml`
- **When** a shipped command that reads the project config is run as a subprocess
- **Then** it exits non-zero, stderr holds one line naming PyYAML and how to install it, and there is no traceback. Fails on: a traceback, or an exit of 0 with the opted-in setting read as its default
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::RequiredPyYamlTests::test_a_shipped_command_exits_non_zero_with_one_refusal_line
- **Verified:** yes (2026-11-19)

### AC4: A config is still honoured where PyYAML imports

- **Given** a project with a readable `.config.yaml`, and one with a malformed one, where `yaml` imports
- **When** the reader is asked for an overridden key in each
- **Then** the readable config's value is returned, and the malformed config is handled as it is today (`config_unparseable` reads true and the unhonoured-config warning is printed). Fails on: a refusal on a machine that has PyYAML, or a changed answer for a malformed config
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::RequiredPyYamlTests::test_a_readable_config_is_still_honoured_with_pyyaml
- **Verified:** yes (2026-11-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
