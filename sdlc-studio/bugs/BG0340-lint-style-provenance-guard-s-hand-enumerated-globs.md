# BG0340: lint-style provenance guard's hand-enumerated globs miss scripts/hooks/ (and narrow templates YAML to config*.yaml)

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/lint-style.sh
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

The provenance-tag guard enumerates scripts/*.py and scripts/lib/*.py only, so the tracked shipped script scripts/hooks/`close_guard.py` (and any future scripts subdirectory) is exempt; the same line covers only templates/config*.yaml, exempting version.yaml and product-manifest.yaml. A provenance tag added to `close_guard.py` would pass the pre-commit style lane and CI.

## Steps to Reproduce

Evidence (rule 3, grep file list at line 64): Confirmed at lint-style.sh 64: grep targets reference-*.md, help/*.md, scripts/*.py, scripts/lib/*.py, templates/config*.yaml plus find-gathered templates markdown; the templates find exists precisely because that tree nests, yet the equally nested scripts tree kept single-level enumeration.

## Proposed Fix

Gather the scripts-tree Python with find, as templates markdown already is: run find over the skill's scripts directory for *.py excluding pycache and capture the result into pyfiles via command substitution, and widen the YAML term to every templates/*.yaml (or a find), so new subdirectories are covered without list maintenance.

## Acceptance Criteria

### AC1: the provenance guard gathers the scripts tree by discovery, so a new subdirectory is covered

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** pytest tools/tests/test_lint_style.py::ProvenanceGuardTests, written red before the fix and green after
- **Verified:** yes (2026-07-28, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
| 2026-07-28 | Claude Fable 5 | Delivered in RUN-01KYJZGZ; acceptance criteria authored at review against the tests that landed |
