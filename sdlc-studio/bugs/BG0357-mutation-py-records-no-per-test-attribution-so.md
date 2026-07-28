# BG0357: mutation.py records no per-test attribution, so the prune-candidate consumer can never run

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, tools/test_census.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ closing review); agent; skill v5.0.0

## Summary

US0507 ships a consumer that nominates a test no mutation of its own module can kill. It requires each killed mutant to carry the test that killed it. mutation.py, this repository's only producer of mutation evidence, never emits that key, so the consumer takes its refusal branch against every real report. The refusal is loud rather than a false green, but the capability is unreachable until the producer records attribution.

## Steps to Reproduce

Run the census candidates subcommand against a real mutation report. It exits non-zero saying the killed mutants carry no per-test attribution and the run must be repeated with it. Search the repository for the attribution key: it appears only in the consumer and the consumer's own test.

## Proposed Fix

Have mutation.py record which test killed each mutant - run the suite per test, or parse the runner's per-test results - so the consumer has evidence to read. Until then US0507 is consumer-only and says so.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ closing review) | Filed |
