# BG0131: The subagent token metric does not track work - it cannot be used for calibration as-is

> **Status:** Open
> **Severity:** High
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The token-supplier PoC (CR0258) flows numbers from a subagent's reported usage into telemetry. The mechanism works, but the METRIC is invalid as a per-unit actual. Measured across three real units delivered by subagents: BG0126 (Python fix + lock + test, 14 tool uses, 272s) = 46,792 tokens; CR0250 (two doc edits, 11 tool uses, 80s) = 46,359 tokens; BG0130 (classifier reorder + 7 tests, 15 tool uses, 189s) = 42,687 tokens. Tokens span 42.7k-46.8k - a +/-9% spread - while wall-clock spans 240% (80s to 272s) and the work differs completely in kind. BG0130 used the MOST tool calls and reported the FEWEST tokens. So the reported figure correlates with neither wall-clock, tool-uses, nor the nature of the work: it is dominated by something near-fixed (most likely output-tokens-only, or context/prompt overhead), not total spend. Calibrating estimates against it would fit noise.

## Steps to Reproduce

Run three units of very different size/kind as subagents; record each completion's reported token usage into telemetry. Compare against `wall_time_s` and `tool_uses.` Tokens stay ~42-47k regardless; wall-clock varies 3.4x.

## Proposed Fix

Define the measured quantity before using it. Establish what the harness's reported token figure counts (output only? total? context?). If it is not total spend, either (a) source the actual from a metric that does track work - wall-clock is the obvious candidate and it demonstrably differentiated all three units - or (b) obtain true input+output usage from the API layer. Until then, do NOT recalibrate the S/M/L token bands (CR0257) or the capacity budget (CR0259) against this figure. Blocks the token half of CR0258; the wall-clock half is unaffected.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
