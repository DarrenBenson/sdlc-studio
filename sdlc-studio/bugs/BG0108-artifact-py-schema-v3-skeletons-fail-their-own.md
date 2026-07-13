# BG0108: artifact.py schema-v3 skeletons fail their own validator (no Raised-by line)

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-11
> **Created-by:** sdlc-studio file

## Summary

On a `schema_version`:3 workspace, artifact.py new/batch creates artefacts without the '> **Raised-by:** Name; type; version' line that validate.py (authorship rule, ~L117) requires on every v3 artefact. Today's sdlc-bench decomposition birthed 31 artefacts that opened with ~130 validator errors; three authoring agents each independently rediscovered and hand-stamped the line. The deterministic creator must emit artefacts the deterministic validator accepts.

## Steps to Reproduce

1. In a workspace with sdlc-studio/.config.yaml `schema_version`: 3, run artifact.py new --type story --title X --epic <id>. 2. Run validate.py check. 3. Authorship error on the fresh skeleton.

## Proposed Fix

artifact.py stamps Raised-by at creation from --author (resolving type/version the same way transition.py does; default to the invoking agent identity when --author is absent).

**Scope widened 2026-07-13.** The defect is not one missing line, it is a class: the
deterministic creators emit skeletons the deterministic validator rejects. A second instance,
reproduced today while filing two CRs into the schema-v3 `sdlc-bench` workspace:
`file_finding.py`'s CR skeleton carries no Impact section and no effort estimate, so every CR
it creates fails `validate.py`'s `evidence-present` rule (`validate.py:161`) on first check.
Both new CRs had to be hand-stamped.

The fix must therefore be **enforced structurally, not patched per field**: a test that
creates one artefact of every type, in both schema eras, through every creator
(`artifact.py new`, `artifact.py batch`, `file_finding.py file`) and asserts `validate.py`
returns zero errors. That test is the real deliverable - it fails today, and it prevents the
next field being added to the validator without the creators following.

## Acceptance Criteria

- [ ] Every creator (`artifact.py new`/`batch`, `file_finding.py file`) emits artefacts that pass `validate.py check` with zero errors, for every artefact type, under both schema v2 and v3
- [ ] A single parametrised test covers the create-then-validate round trip across that matrix, and fails on today's code
- [ ] `Raised-by` is stamped at creation from `--author`, defaulting to the invoking agent identity
- [ ] CR skeletons carry the Impact + effort block `validate.py` requires

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-11 | audit | Filed |
| 2026-07-13 | Darren | Scope widened during v4.1 grooming: found a second instance of the same class (file_finding.py's CR skeleton omits the Impact/effort block validate.py requires), reproduced live while re-homing CR0230/CR0231 into sdlc-bench. Reframed from "stamp one line" to "creators must emit what the validator accepts", enforced by a create-then-validate round-trip test across every creator, type and era. |
