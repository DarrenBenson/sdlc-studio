# BG1181: gate_prereqs.py check reports every prerequisite present on a machine with no Python 3.10, which the release gate's US0908 lane needs

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/gate_prereqs.py, tools/tests/test_gate_prereqs.py, changelog.d/BG1181.md
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T21:06:53Z

## Summary

Found by the release triage (2026-11-02). Neither this workstation nor devserver1 had Python 3.10, so US0908's two criteria skipped and `gate.py --release` read them red. `python3 tools/gate_prereqs.py check` and `enable-hooks.sh` said every prerequisite was present. CI installs 3.10 itself (.github/workflows/lint.yml). It was fixed for this release by `uv python install 3.10` (D0396).

## Steps to Reproduce

1. On a machine with no python3.10 and `uv python find 3.10` empty, run `python3 tools/gate_prereqs.py check`: 'every one present'.

## Proposed Fix

Have `gate_prereqs` name Python 3.10 as a release-gate prerequisite, with the uv install route, as it names the others.

## Acceptance Criteria

- [ ] **AC1** `gate_prereqs.py check` names Python 3.10 as missing when neither python3.10 nor `uv python find 3.10` answers.
  - **Verify:** pytest tools/tests/test_gate_prereqs.py

## Impact

A release gate goes red on a machine the prerequisite check called ready.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
