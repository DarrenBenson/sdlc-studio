# BG0323: provenance check silently reports an unreadable artifact as clean - defeating the census's explicit keep-it-visible cont

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/provenance.py, .claude/skills/sdlc-studio/scripts/tests/test_provenance.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

check() re-reads each artifact and skips any it cannot read, so an unreadable artifact is absent from findings and ok stays true - an enforced provenance gate exits 0 on a file it could not judge, discarding the visibility `sdlc_md.iter_artifact_files` deliberately provides by yielding unreadable files as (path, None).

## Steps to Reproduce

Evidence (check(), lines 93-102 (except OSError: continue at 99-100)): Reproduced with a fixture workspace: a chmod-000 story vanished from output, ok: true, exit 0; lib/`sdlc_md.py`:1229-1231 comment: 'keep it visible so a checker NAMES it'; provenance.py cites LL0008 at line 81 while violating it twelve lines later.

## Proposed Fix

Consume the (path, text) pairs from `sdlc_md.iter_artifact_files` instead of re-reading, and emit a blocking 'unreadable' finding for any text=None file.

## Acceptance Criteria

### AC1: an unreadable artefact is not reported clean

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** `pytest .claude/skills/sdlc-studio/scripts/tests/test_provenance.py::UnreadableArtifactTests`, written red before the fix and green after
- **Verified:** yes (2026-07-27, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
