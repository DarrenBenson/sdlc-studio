# BG0120: the index writer emits MD060 table errors on a freshly created index

> **Status:** Open
> **Severity:** Low
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Dani Okafor; persona; v1

## Summary

Found while delivering BG0112 (2026-07-13), flagged as out of scope there. BG0112 fixed the full templates so a created artefact lints clean, but a freshly created _index.md summary and row table still emit MD060, because the index writer emits padded-but-unspaced delimiter rows. Tracked indexes look clean only because reconcile rewrites them to compact style; a brand new index (a consuming project's first artefact of a type) lands failing markdownlint. Same class as BG0112 (a deterministic writer producing output the workspace lint rejects), but the emitter is the index code in the shared library, not a template, so it needs its own unit. BG0112's round-trip markdownlint leg lints only the artefact file, not the index, so this is not caught by that guard.

## Steps to Reproduce

1. artifact.py new --type rfc (in a workspace with no rfcs yet, so the index is freshly written). 2. Run markdownlint under the root config on the created _index.md. 3. MD060 fires on the freshly written delimiter rows.

## Proposed Fix

Emit compact single-dash delimiter rows from the index writer, matching what reconcile rewrites them to, so a fresh index is lint-clean from creation. Extend BG0112's round-trip markdownlint leg to also lint the _index.md the creator touched.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Dani Okafor | Filed |
