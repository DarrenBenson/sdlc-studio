# BG0160: config.get() crashes with an uncaught ParserError on a malformed .config.yaml despite BG0093's warn-and-default contract - yaml.YAMLError is missing from the catch tuple

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

config.py get() catches (RuntimeError, OSError, ValueError), but `yaml.safe_load` raises ParserError/ScannerError, subclasses of yaml.YAMLError -> Exception, not ValueError. Reproduced live: a single typo in .config.yaml uncaught-tracebacks every config consumer - status, gate, transition gates, `telemetry.model_price`, `sprint_report.rendering_enabled.` The docstring claims 'an unreadable/malformed override' degrades to the default with a warning (BG0093), and CR0180's AC demanded testing both the no-PyYAML AND malformed conditions, yet GracefulDegradeTests mocks only the RuntimeError path - the defence was never validated against the bug it defends against (LL0010). Verified 3x including live reproduction by two panel voters.

## Steps to Reproduce

Write .config.yaml containing `pricing:\n  opus: [unclosed`; call config.get(root, 'pricing.opus', 'DEFAULT') - uncaught yaml.parser.ParserError propagates through every consumer (status, gate, transition, telemetry).

## Proposed Fix

Add the YAML error to the catch (guard the import: catch a tuple built to include _yaml.YAMLError when PyYAML is present), warn-and-default per the BG0093 contract, and add a malformed-YAML test to GracefulDegradeTests.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
