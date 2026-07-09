# BG0095: the Provenance: external stamp that gates shell verifiers has no writer anywhere on the ingest path

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4 (the executor gate, --no-shell and the prose warning still stand between an issue body and a shell). CWE-693 protection-mechanism gap: verify_ac.py:524-534 blocks shell/eval/http verbs when 'Provenance: external' is stamped - but nothing ever writes that stamp. Verified by broad grep (RV0007): reference-verify.md:165-171 claims 'the ingest path stamps this field' - false; github_sync.py cmd_pull (:511-568) writes no files and only prints a TODO pointing at 'create --from-issue'; reference-cr.md's from-issue workflow (:324-330) and reference-github-sync.md (:129-138) contain no stamp instruction; reference-story.md has NO from-issue branch at all despite reference-github-sync.md:235 linking to one; templates carry no Provenance field; artifact.py new accepts no provenance argument. A GitHub issue body ingested by the documented workflow arrives unstamped, so its shell/eval/http Verify lines execute by default at first verify - the entry point the control exists for.

## Steps to Reproduce

Follow reference-cr.md's from-issue ingest on an issue containing a '- **Verify:** shell ...' line; grep the created artefact for 'Provenance' -> absent; verify_ac run executes the line (subject to remaining gates).

## Proposed Fix

Make the stamp mechanical: from-issue branches in reference-cr.md and a new one in reference-story.md add '> **Provenance:** external'; add a deterministic path (artifact.py new --provenance external or a github_sync ingest helper); correct the reference-verify.md claim until then.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
