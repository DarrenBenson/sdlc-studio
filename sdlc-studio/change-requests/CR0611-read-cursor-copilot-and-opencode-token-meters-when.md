# CR-0611: Read Cursor, Copilot, and OpenCode token meters when those harnesses are in use

> **Status:** In Progress
> **Decomposed-into:** EP0274
> **Priority:** High
> **Type:** Feature
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** sdlc-studio-lens RUN-01M48BNK, closed 2026-10-06. open_run stamped session_token_baseline null. session_tokens reported no harness transcript directory at ~/.claude/projects/-workspace. The sprint report left tokens NOT MEASURED. The session was a Cursor cloud agent, not Claude Code.
> **Date:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Cursor Agent; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T17:59:56Z

## Summary

`run_state.session_tokens` reads one meter: the newest Claude Code transcript under ~/.claude/projects/<project-slug>/*.jsonl (override `SDLC_STUDIO_TRANSCRIPTS`). It sums `input_tokens`, `output_tokens`, and `cache_creation_input_tokens`, and it drops cache reads. `open_run` stamps that reading as the baseline. The close subtracts it from a later reading of the same file. No transcript, no usage records, a malformed record, or a different session file all mean the sprint's token cost is not attributable. The close must not substitute the raw session total or a zero.

That rule is right, and it is also why a Cursor, GitHub Copilot CLI, or OpenCode run publishes a blank token actual. Those harnesses do not write the Claude transcript. On RUN-01M48BNK the directory was absent, the baseline stayed null, and RPT0001 recorded no token figure. The same blank will recur for every sprint driven by one of those three harnesses.

The fix is a harness reader selected for the process that is actually running. Claude stays the reader it is today. Cursor, Copilot, and OpenCode each get a reader of the store that harness persists. A missing store, an unreadable record, or two plausible stores and no choice stays not attributable. Stores are never summed together.

## Impact

Every sprint report, velocity row, and tokens-per-point rate for a project whose agent is Cursor, Copilot CLI, or OpenCode. Today those runs look unmeasured. A wrong reader would be worse: booking a Claude leftover, a context-window occupancy figure, or a zero onto the velocity history is how this project previously published 341,450 and then 472,691 tokens per point.

## Acceptance Criteria

- [ ] When the running harness is Claude Code, the token baseline and the close delta stay the current Claude transcript reading, cache reads excluded, and a missing or malformed transcript stays not attributable.
- [ ] When the running harness is Cursor, the close records that run's token total from the cloud usage API or from the CLI's persisted usage, counting input, output and cache write with cache reads recorded separately (D0346), and a missing key, an unreachable API, or an exited print run with no stored result stays not attributable rather than zero.
- [ ] When the running harness is GitHub Copilot CLI, the close records the session.shutdown modelMetrics usage from the Copilot session events, honouring `COPILOT_HOME`, without adding reasoning tokens on top of output and without treating context-window occupancy as spend.
- [ ] When the running harness is OpenCode, the close records message token fields from the read-only OpenCode database, or the legacy JSON store when the database is absent, for this repo's sessions including child sessions, and does not invoke the opencode binary to obtain the figure.
- [ ] If more than one harness store is present and `SDLC_STUDIO_HARNESS` does not choose, the close names the candidates and records no token total. It never sums two harnesses.

## Recommendation

Detect the harness, then read only that harness's meter.

Selection. `SDLC_STUDIO_HARNESS` set to claude, cursor, copilot, or opencode wins. Otherwise use the process environment: `CURSOR_AGENT` or a Cursor cloud run id selects Cursor; `COPILOT_HOME` or a live Copilot CLI session selects Copilot; OPENCODE or `OPENCODE_DB` selects OpenCode; a readable Claude transcript selects Claude. If more than one store exists and nothing selects, name the candidates and return not attributable. Do not add them. An old Claude directory must not be booked onto a Cursor run.

Claude. Keep `session_tokens` as it is, including the exclusion of cache reads, the main-thread-only basis, and the refusal of a malformed usage record. `SDLC_STUDIO_TRANSCRIPTS` still overrides the directory.

Cursor. Two persisted surfaces, and they must not be mixed. The cloud usage API is GET /v1/agents/{id}/usage. It returns totalUsage and one usage object per run: inputTokens, outputTokens, cacheWriteTokens, cacheReadTokens, totalTokens. Call it only when a Cursor API key is available and the run id is known. No key, an HTTP failure, or a run that has not recorded usage yet is not attributable, never a zero. The CLI print path (agent -p --output-format json) can include a usage object with the same four fields on the result. The interactive CLI and ACP mode do not emit it, and there is no Claude-style transcript to subtract after the fact. Pin whatever session store the current CLI actually writes by reading it at implementation time, with a fixture. Do not scrape the TUI, and do not hard-code a guessed path. If the only record was stdout from a process that has already exited, say so and leave the figure blank.

Copilot CLI. Read ~/.copilot/session-state/<session-id>/events.jsonl, with `COPILOT_HOME` overriding ~/.copilot. The session total is the session.shutdown event's data.modelMetrics.<model>.usage: inputTokens, outputTokens, cacheReadTokens, cacheWriteTokens, and reasoningTokens when present. reasoningTokens are a subset of output and must not be added twice. More than one model in that map is the existing mixed-model marker, not a silent pick of one model. Ignore `session.usage_info` currentTokens: that is context-window occupancy, not spend. assistant.usage events are per call; prefer the shutdown aggregate so a resumed session is not double-counted.

OpenCode. Read the SQLite database read-only (mode=ro, `query_only`). The usual path is ~/.local/share/opencode/opencode.db. Honour `XDG_DATA_HOME` and `OPENCODE_DB`. Fold message JSON fields tokens.input, tokens.output, tokens.reasoning, tokens.cache.read, and tokens.cache.write for sessions whose directory is this repo. Do not trust the session aggregate columns: migrated rows leave them zero. Include child sessions (`parent_id` set) and say in the basis that subagent spend is included. If the database is absent, read the legacy JSON tree under storage/message. Do not shell out to opencode stats. A missing binary must not become a zero.

Counting. Each reader returns the categories that harness bills, and the basis string names the harness and the categories. Ruled in D0346: every reader counts input, output and cache write in the headline and records cache reads separately, outside it, as the Claude reader already does, so tokens-per-point stays comparable across harnesses. The raised text counted the billed total, cache reads included, for Cursor, Copilot and OpenCode. The open baseline and the close reading must be the same source. A different session, a meter at or below the baseline, or a batch that does not cover the retro's units stays not attributable, as `run_attributed_tokens` already requires. Where the store includes subagent spend, do not also add `delegated_tokens` for the same work. Where it does not (Claude, and a Cursor result that is main-thread only), keep the supplied `delegated_tokens` path.

Tests. Fixture a Claude transcript, a Copilot events.jsonl shutdown record, an OpenCode sqlite message, and a Cursor usage payload. Each asserts the summed total, the basis, and the model or mixed marker. A missing directory, an empty store, a malformed record, and two unselected stores each return tokens null with a named reason and never zero. A Cursor run with a leftover Claude directory does not read the Claude file.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | Cursor Agent | Raised |
| 2026-10-06 | Claude Opus 5.5 | Filed with `file_finding.py`; Recommendation carried over. Amended per D0346: one counting basis for every reader (AC2, Counting) |
