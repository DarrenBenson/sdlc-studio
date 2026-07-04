# TS0002: Mutation-check gate test spec

> **Status:** Ready
> **Epic:** EP0011
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new

## Overview

The epic-scope test specification for EP0011 (executable mutation-check gate). Every story AC
maps to a planned test case here; the stories' `Verify:` lines point at these exact pytest
titles so implementation binds tests to this matrix by construction. Doc ACs are verified by
shell greps (the link/style guards cover mechanics).

## Scope

### Stories Covered

| Story | Title | Priority |
| --- | --- | --- |
| [US0051](../stories/US0051-textual-mutation-engine-declared-fault-classes-language-profiles.md) | Textual mutation engine | High |
| [US0052](../stories/US0052-runner-bridge-and-mutation-report-killed-vs-survived.md) | Runner bridge + mutation report | High |
| [US0053](../stories/US0053-mutation-cli-lanes-story-files-since-selection-static.md) | CLI lanes, pre-filter, cost ceiling | Medium |
| [US0054](../stories/US0054-gate-wiring-and-docs-advisory-mutation-lane-discipline.md) | Gate wiring + docs | Medium |

### AC Coverage Matrix

| Story | AC | Description | Test Cases | Status |
| --- | --- | --- | --- | --- |
| US0051 | AC1 | enumeration is deterministic (same list twice, line-ordered) | test_mutation.py::EngineTests::test_enumeration_is_deterministic | Planned |
| US0051 | AC2 | each fault class mutates its Python form, one at a time | test_mutation.py::EngineTests::test_each_class_mutates_python | Planned |
| US0051 | AC3 | apply/restore round-trip byte-identical, incl. on runner exception | test_mutation.py::EngineTests::test_restore_is_byte_identical | Planned |
| US0051 | AC4 | uncovered language reports un-checked, never passed | test_mutation.py::EngineTests::test_uncovered_language_unchecked | Planned |
| US0052 | AC1 | vacuous test survives, load-bearing test kills | test_mutation.py::BridgeTests::test_vacuous_survives_loadbearing_kills | Planned |
| US0052 | AC2 | report shape + summary counts equal records | test_mutation.py::BridgeTests::test_report_shape_and_counts | Planned |
| US0052 | AC3 | survivors exit non-zero, named | test_mutation.py::BridgeTests::test_survivor_exits_nonzero | Planned |
| US0052 | AC4 | runner error reported, never a kill | test_mutation.py::BridgeTests::test_runner_error_not_a_kill | Planned |
| US0053 | AC1 | --files and --since select the declared surface | test_mutation.py::LaneTests::test_files_and_since_select_surface | Planned |
| US0053 | AC2 | ceiling truncates loudly (truncated count in report) | test_mutation.py::LaneTests::test_ceiling_truncates_loudly | Planned |
| US0053 | AC3 | prefilter flags assertion-free tests only | test_mutation.py::LaneTests::test_prefilter_flags_assertion_free | Planned |
| US0054 | AC1 | gate warns on survivors, stays advisory | test_gate.py::MutationLaneTests::test_survivors_warn_advisory | Planned |
| US0054 | AC2 | absent report reads not-run, never PASS | test_gate.py::MutationLaneTests::test_absent_report_is_not_run | Planned |
| US0054 | AC3 | discipline prose links to the executable gate | shell grep (see story Verify) | Planned |

## Fixtures

Temp-dir repos with a small Python module + paired pytest-style tests (one load-bearing, one
vacuous); a `.js` file for profile coverage; a git repo fixture for `--since`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | sdlc | Created via `new` (deterministic) |
| 2026-07-04 | claude | Matrix authored at design (shift-left bridge); stories' Verify lines point at these titles |
