# BG0108: artifact.py schema-v3 skeletons fail their own validator (no Raised-by line)

> **Status:** Fixed
> **Verification depth:** functional
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

- [ ] Given the content its type needs, every creator (`artifact.py new`/`batch`, `file_finding.py file`, and the consolidation CR) emits an artefact that passes `validate.py check` with zero errors, for every artefact type, under both schema v2 and v3 - and that content appears in the artefact, never silently dropped
- [ ] No creator-owned rule (id, title, status, authorship, tranche) ever fires on a minted artefact, content or no content
- [ ] **Carve-out:** a content-less scaffold (no `--ac` on a story, no `--steps` on a bug, no `--impact`/`--effort` on a CR) still reports its unfilled `{{placeholder}}` slots. Making those green would mean writing non-AC text into the AC section, which satisfies `no-ac` in `validate.py` **and** promotes an unspecified story to `specified` in `conformance.py` - the silent corruption this bug exists to stop. The scaffold contract (create-then-fill) versus content-at-creation is a product call, raised as a separate RFC
- [ ] A single parametrised test covers the create-then-validate round trip across that matrix, and fails on today's code
- [ ] `Raised-by` is stamped at creation from `--author`, defaulting to the invoking agent identity
- [ ] CR skeletons carry the Impact + effort block `validate.py` requires

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-11 | audit | Filed |
| 2026-07-13 | Dani Okafor | AC1 amended in the implementing unit (the deviation is recorded with the work, not discovered at close). Two changes. (1) It now demands the supplied content REACHES the artefact, not only that the validator tolerates it: the first fix added content flags whose values `_graft` then dropped on the floor, so `--template full` (batch's default) returned exit 0 and a clean validator over an artefact the caller's words never reached. Caught by the independent critic. (2) A content-less scaffold is explicitly carved out: it still reports its unfilled placeholders, and making it green would require writing non-AC text into the AC section, which passes `no-ac` and silently promotes an unspecified story to `specified` in conformance. The scaffold-contract question goes to an RFC. |
| 2026-07-13 | Darren | Scope widened during v4.1 grooming: found a second instance of the same class (file_finding.py's CR skeleton omits the Impact/effort block validate.py requires), reproduced live while re-homing CR0230/CR0231 into sdlc-bench. Reframed from "stamp one line" to "creators must emit what the validator accepts", enforced by a create-then-validate round-trip test across every creator, type and era. |
