# BG1517: The TRD threat model omits Verify-line shell execution and wrongly says Verify tools are host-bounded

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md §5 Network paths (lines 337-338); §9 Threat Model, 'Network exfiltration' row (line 768); no row for Verify-line execution anywhere in §9
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:21:34Z

## Summary

The TRD says twice that a project's Verify-line tools are bounded to the hosts `SDLC_VERIFY_HTTP_HOSTS` names, and uses that as the mitigation in the Network exfiltration row. In `verify_ac.py` the allow-list is empty by default, which means unrestricted, and it is consulted only for the `http` verb, so `shell`, `eval`, `pytest` and the other verbs are untouched by it. The Threat Model also has no row for the highest-impact threat in the design: `verify_ac.py` runs text taken from a markdown artefact through a shell. The real control, the `Provenance: external` stamp with `--no-shell` and `--allow-external`, is never mentioned in the TRD. A rebuild from this document would ship shell execution of artefact text with no trust boundary and would believe a network bound that does not exist by default.

## Steps to Reproduce

1. Read sdlc-studio/trd.md lines 337 to 338 and the Network exfiltration row at about line 768: both say Verify-line tools are bounded by `SDLC_VERIFY_HTTP_HOSTS`.
2. Read `_restricted_http_hosts` in .claude/skills/sdlc-studio/scripts/`verify_ac.py` (about line 2096): the docstring says the list is empty by default, unrestricted, and its only caller is `_check_http_target`, the http verb.
3. Read `shell_allowed_for` in the same file (about line 2677): shell execution is gated on the Provenance stamp, and an absent stamp permits it.
4. Search sdlc-studio/trd.md for provenance, no-shell, allow-external and untrusted: no hit concerns the verifier, and section 9 has no row for Verify-line execution.

## Proposed Fix

Correct both TRD sentences to say the host allow-list is unset by default, applies to the `http` verb only, and bounds nothing until a project sets it. Add a Threat Model row for execution of artefact text by the verifier, naming the Provenance stamp, `--no-shell` and `--allow-external` as the control and stating its limit: the stamp is self-declared and an absent stamp permits shell. Pin the corrected wording and the new row in the TRD refresh test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The TRD says twice that a project's Verify-line tools are bounded to the hosts `SDLC_VERIFY_HTTP_HOSTS` names, and uses that as the mitigation in the Network...
- [ ] **AC2** The proposed fix lands, pinned by a test: Correct both TRD sentences to say the host allow-list is unset by default, applies to the `http` verb only, and bounds nothing until a project sets it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
