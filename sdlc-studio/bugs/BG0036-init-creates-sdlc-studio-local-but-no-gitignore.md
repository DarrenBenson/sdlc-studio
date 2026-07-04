# BG0036: init creates sdlc-studio/.local but no .gitignore, so consuming projects commit runtime caches/reports

> **Status:** Closed
> **Severity:** medium
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

scripts/init.py creates the sdlc-studio/.local runtime-state dir (caches, verify-report.json, lessons) but never writes a .gitignore excluding it. This repo only avoids tracking .local because it has a hand-written root .gitignore entry (sdlc-studio/.local/); a greenfield project bootstrapped by init gets no such entry, so derived state is committed. A field agent upgrading shoppinglist found .local tracked and committed verify-report.json with the upgrade.

## Steps to Reproduce

1. Run init in a fresh project. 2. Run any command that writes .local (gate, verify_ac, status cache). 3. git status shows sdlc-studio/.local/*.json as untracked-and-committable; nothing ignores them. Repro: shoppinglist v3 upgrade committed .local derived files.

## Proposed Fix

In init, write a self-contained sdlc-studio/.gitignore containing '.local/' (idempotent via the existing _write skip-if-exists). Self-contained in the sdlc-studio dir so it never touches the project's own root .gitignore. Unit test: init creates sdlc-studio/.gitignore ignoring .local/; idempotent on re-run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Filed |
