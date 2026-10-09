# US1003: enable-hooks.sh names every missing gate prerequisite with a route that works on this interpreter

> **Status:** Draft
> **Delivers:** CR0613
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/gate_prereqs.py, requirements-dev.txt, tools/enable-hooks.sh, AGENTS.md, tools/tests/test_gate_prereqs.py, changelog.d/US1003.md
> **Epic:** EP0278
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer setting up a fresh clone of the skill source on a new machine
**I want** `bash tools/enable-hooks.sh` to check the interpreter and tools the gates run on, and name each missing or too-old prerequisite with what breaks without it and a way to install it that works on this interpreter
**So that** I learn at setup what the gate needs and how to get it here, instead of from a push that goes red after the full suite, or from an install command my system Python refuses

## Acceptance Criteria

- **AC1:** Given a fixture clone whose requirements-dev.txt declares a distribution that is not installed (`zzq-absent-dist>=1`) and a floor no installed version meets (`coverage>=999`), when `bash tools/enable-hooks.sh` runs, then it names the first as missing and the second as too old with the version found and the floor, still sets core.hooksPath and prints the keepalive line, and exits 0.
  - **Verify:** pytest tools/tests/test_gate_prereqs.py::EnableHooksPrerequisiteTests::test_a_missing_or_too_old_prerequisite_is_named_and_setup_completes
- **AC2:** Given a python3 that cannot import coverage (hidden by a sitecustomize shim on PYTHONPATH), when enable-hooks.sh runs, then coverage is named with its consequence class: the push suite goes red without it.
  - **Verify:** pytest tools/tests/test_gate_prereqs.py::EnableHooksPrerequisiteTests::test_a_suite_prerequisite_is_named_with_the_consequence_of_its_absence
- **AC3:** Given two interpreters with the same gap, one carrying an `EXTERNALLY-MANAGED` marker in its stdlib directory with no importable pip and one unmanaged with pip importable, when enable-hooks.sh runs with each first on PATH, then only the second offers `python3 -m pip install -r requirements-dev.txt`, and the first names its own path as externally managed and offers the OS package and a virtual environment placed first on PATH.
  - **Verify:** pytest tools/tests/test_gate_prereqs.py::EnableHooksPrerequisiteTests::test_the_install_route_is_read_from_the_interpreter
- **AC4:** Given a PATH with no markdownlint, no node_modules/.bin/markdownlint, no rg and no gh, when enable-hooks.sh runs, then each of the four is named on its own line with its consequence (the commit's markdown lanes skip and CI enforces them, the rg-only tests skip, the red-CI read before a push reads UNREAD) and either `npm ci`, a fixed project URL or the package name.
  - **Verify:** pytest tools/tests/test_gate_prereqs.py::EnableHooksPrerequisiteTests::test_missing_tools_outside_python_are_named_with_their_consequence
- **AC5:** Given a clone and interpreter with every prerequisite present, when enable-hooks.sh runs, then it reports every gate prerequisite present, names none missing, and exits 0.
  - **Verify:** pytest tools/tests/test_gate_prereqs.py::EnableHooksPrerequisiteTests::test_a_complete_environment_reports_nothing_missing

## Notes

- Release: 6.2 (D0355 breakdown G4, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the checker's non-zero exit aborting enable-hooks.sh under `set -euo pipefail` (enable-hooks.sh:22) before the keepalive block; or a presence-only check that ignores the floor; or the checker holding its own Python list instead of reading requirements-dev.txt (today: nothing is checked at all)
- AC2 must fail on: every gap given one generic consequence, so the refusing class (pytest, coverage, PyYAML) cannot be told from the slowing or skipping classes
- AC3 must fail on: a fixed `pip install` line printed whatever the interpreter (it fails on this machine: /usr/bin/python3 3.14 is EXTERNALLY-MANAGED and has no pip module)
- AC4 must fail on: the check covering the Python packages only, so the node and executable prerequisites are never named
- AC5 must fail on: a package looked up by its import name (`yaml`, `xdist`) as if it were the distribution name, so a present package reads missing (`importlib.metadata.version('yaml')` and `('xdist')` raise PackageNotFoundError; the distribution names resolve)
- The prerequisite set is wider than the CR's five. Probed at HEAD by hiding a package from python3 with a sitecustomize shim:
- Without coverage, 15 tests in six modules go red (test_transition CoverageGateTests, test_verify_ac LineCoverageTests, test_lean_coverage_opt_in, tools/tests/test_lean_push). Without PyYAML, test_lean_config_show_sources goes red. lint.yml installs both (:65-76), and ripgrep (:63).
- Declared set. Python, from requirements-dev.txt: PyYAML, pytest, pytest-xdist, coverage>=7.10. Node, from package.json: markdownlint, via `npm ci`. Executables declared in the checker: rg, gh, plus a Python 3.10 floor (what CI tests and what `repo map build` needs).
- Consequence classes, keyed by name:
- Refuses the push: pytest, coverage>=7.10, PyYAML. A declared distribution with no listed class defaults to this one.
- Slows the push: pytest-xdist (the suite runs serially). Skips locally, CI enforces: markdownlint, rg. Degrades the red-CI read: gh.
- Install route, read from the interpreter: whether pip imports, whether `sysconfig.get_path('stdlib')/EXTERNALLY-MANAGED` exists, and whether `sys.prefix != sys.base_prefix` (a venv).
- The pip -r line is printed only for a venv, or an unmanaged interpreter with pip. Otherwise: name the interpreter path, say it is externally managed or has no pip, and give the OS package and a venv first on PATH. The hooks run `python3` from PATH.
- Check the `python3` the hooks run. enable-hooks.sh runs `python3 tools/gate_prereqs.py check` and ignores its exit code, then continues to the keepalive block (AC1). Presence and version are read by distribution name through importlib.metadata.
- Honour `SDLC_COVERAGE_PYTHON`: when it is set, check coverage on that interpreter (verify_ac.py:2371-2373).
- enable-hooks.sh tolerates an absent tools/gate_prereqs.py with a named note (the panel's answer). The existing fixtures in tools/tests/test_pre_push_hook.py (EnableHooksNamesEveryHookTests, KeepaliveTests) copy only enable-hooks.sh, and they keep passing unchanged.
- AGENTS.md: point at `python3 tools/gate_prereqs.py check` from the hooks paragraph ('Enable the hooks once per clone'). It does not go in the Soft dependencies table, which lists the shipped skill's runtime features. G8's commit-hooks story owns the Testing section edit.
- Fixtures. AC1 declares a distribution that cannot exist and an unmeetable floor, which is simpler and steadier than hiding metadata. AC2 keeps one sitecustomize shim, keyed on coverage by name.
- AC3 has two shims: one points sysconfig's stdlib at a directory holding the marker and hides pip, and the other puts a stub `pip` package on PYTHONPATH.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G4 after the refine panel's review |
