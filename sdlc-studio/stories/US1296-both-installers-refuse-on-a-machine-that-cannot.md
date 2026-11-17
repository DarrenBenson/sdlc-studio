# US1296: Both installers refuse on a machine that cannot import PyYAML, naming it and how to install it

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0731
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** install.sh, install.ps1, docs/INSTALL.md, tools/tests/test_install_requires_pyyaml.py
> **Epic:** EP0368
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Both installers refuse on a machine that cannot import PyYAML, naming it and how to install it
**So that** CR0731 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: install.sh refuses where PyYAML cannot be imported

- **Given** a machine whose `python3` cannot import `yaml` (a stub interpreter first on PATH), and again one with no `python3` at all, each with an empty install target
- **When** `install.sh` is run for a local install
- **Then** it exits non-zero before copying anything, stderr names PyYAML and a command that installs it, and the target holds no skill file. Fails on: an install that completes without PyYAML, or a refusal that leaves a partial copy behind
- **Verify:** pytest tools/tests/test_install_requires_pyyaml.py::InstallRequiresPyYamlTests::test_install_sh_refuses_when_pyyaml_cannot_be_imported

### AC2: install.sh still installs where PyYAML imports

- **Given** a machine whose `python3` imports `yaml`
- **When** the same install is run
- **Then** it exits 0 and the skill is installed as before. Fails on: a check that refuses every machine
- **Verify:** pytest tools/tests/test_install_requires_pyyaml.py::InstallRequiresPyYamlTests::test_install_sh_installs_when_pyyaml_imports

### AC3: install.ps1 makes the same refusal before its first copy

- **Given** `install.ps1`
- **When** it is run under `pwsh` with a Python that cannot import `yaml`, or, where `pwsh` is not installed, its source is read
- **Then** the import check comes before the first copy or download step, a failed check stops the script with a non-zero exit, and the message names PyYAML and the install command. Fails on: a PowerShell install that completes without PyYAML while the shell install refuses
- **Verify:** pytest tools/tests/test_install_requires_pyyaml.py::InstallRequiresPyYamlTests::test_install_ps1_checks_pyyaml_before_its_first_copy

### AC4: The install page names PyYAML as required

- **Given** `docs/INSTALL.md`
- **When** its requirements are read
- **Then** PyYAML is listed as required with its install command, and no sentence calls it optional, says the scripts degrade to built-in defaults without it, or calls the helpers pure standard library. Fails on: the page as it stands at grooming, which lists PyYAML as an optional dependency
- **Verify:** pytest tools/tests/test_install_requires_pyyaml.py::InstallRequiresPyYamlTests::test_the_install_page_names_pyyaml_as_required

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
