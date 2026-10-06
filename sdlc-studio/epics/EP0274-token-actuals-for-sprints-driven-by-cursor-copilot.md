# EP0274: Token actuals for sprints driven by Cursor, Copilot CLI or OpenCode

> **Status:** Draft
> **Derived Point Total:** 26
> **Parent:** CR0611
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0611. Delivers the work CR0611 requested.

## Story Breakdown

- [ ] [US0986: The token meter reads the running harness's store, chosen by SDLC_STUDIO_HARNESS or the environment, and never sums two](../stories/US0986-the-token-meter-reads-the-running-harness-s.md)
- [ ] [US0987: A Copilot CLI run records its token actual from the session events](../stories/US0987-a-copilot-cli-run-records-its-token-actual.md)
- [ ] [US0988: An OpenCode run records its token actual from the read-only OpenCode database, child sessions included](../stories/US0988-an-opencode-run-records-its-token-actual-from.md)
- [ ] [US0989: A Cursor cloud run records its token actual from the usage API when a key is present](../stories/US0989-a-cursor-cloud-run-records-its-token-actual.md)
- [ ] [US0990: A Cursor CLI run records its token actual from the store the CLI persists, or says why it cannot](../stories/US0990-a-cursor-cli-run-records-its-token-actual.md)
- [ ] [US0991: The close and the report state each reading's own basis, and add delegated tokens only when the reading excludes subagent spend](../stories/US0991-the-close-and-the-report-state-each-reading.md)

## Acceptance Criteria (Epic Level)

- [ ] When the running harness is Claude Code, the token baseline and the close delta stay the current Claude transcript reading, cache reads excluded, and a missing or malformed transcript stays not attributable.
- [ ] When the running harness is Cursor, the close records that run's token total from the cloud usage API or from the CLI's persisted usage, counting input, output and cache write with cache reads recorded separately (D0346), and a missing key, an unreachable API, or an exited print run with no stored result stays not attributable rather than zero.
- [ ] When the running harness is GitHub Copilot CLI, the close records the session.shutdown modelMetrics usage from the Copilot session events, honouring `COPILOT_HOME`, without adding reasoning tokens on top of output and without treating context-window occupancy as spend.
- [ ] When the running harness is OpenCode, the close records message token fields from the read-only OpenCode database, or the legacy JSON store when the database is absent, for this repo's sessions including child sessions, and does not invoke the opencode binary to obtain the figure.
- [ ] If more than one harness store is present and `SDLC_STUDIO_HARNESS` does not choose, the close names the candidates and records no token total. It never sums two harnesses.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Created via `new` (deterministic) |
