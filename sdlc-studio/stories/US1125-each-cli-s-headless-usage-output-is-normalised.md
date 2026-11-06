# US1125: Each CLI's headless usage output is normalised to one basis, pinned by real captured sessions

> **Status:** Ready
> **Delivers:** CR0667
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/harness_usage.py, .claude/skills/sdlc-studio/scripts/tests/test_harness_usage.py, .claude/skills/sdlc-studio/scripts/tests/fixtures/harness_usage/claude.json, .claude/skills/sdlc-studio/scripts/tests/fixtures/harness_usage/cursor.json, .claude/skills/sdlc-studio/scripts/tests/fixtures/harness_usage/codex.jsonl, .claude/skills/sdlc-studio/scripts/tests/fixtures/harness_usage/copilot.jsonl, .claude/skills/sdlc-studio/scripts/tests/fixtures/harness_usage/opencode.jsonl, changelog.d/US1125.md
> **Epic:** EP0299
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Each CLI's headless usage output is normalised to one basis, pinned by real captured sessions
**So that** every harness's lanes are counted on one basis, and none counts cached tokens twice

## Acceptance Criteria

- **AC1:** Given the headless output of Claude Code, Cursor CLI, Codex CLI, Copilot CLI and OpenCode captured from real sessions on 2026-11-06 and scrubbed of account identifiers, then `harness_usage.parse(harness, text)` returns input without cache, cache read, cache write, output, reasoning, model and session id for each. Fails on: a fixture written from documentation rather than captured
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_harness_usage.py::HarnessUsageTests::test_each_captured_session_normalises
- **AC2:** Given Codex's and Copilot's input, which includes cached tokens, then the cached part is split out, so input, cache read and cache write together equal the CLI's own prompt total exactly once. Fails on: cached tokens counted inside input and again as cache
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_harness_usage.py::HarnessUsageTests::test_cached_input_is_split_and_never_counted_twice
- **AC3:** Given a non-zero exit, output with no usage, or a line that does not parse, then the result is unmetered with a reason naming which. Fails on: any of them read as zero tokens
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_harness_usage.py::HarnessUsageTests::test_unmetered_with_a_reason
- **AC4:** Given output that carries the harness's own total (Claude Code's `total_cost_usd`, Copilot's session accounting), then the normalised figure is checked against it and a disagreement above 5% is named. Fails on: a disagreement passed silently
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_harness_usage.py::HarnessUsageTests::test_a_disagreement_with_the_harness_total_is_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed: criteria and Verify checks authored for run seven (RFC0062 Phase 1) |
