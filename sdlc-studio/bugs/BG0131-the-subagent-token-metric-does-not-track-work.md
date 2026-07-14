# BG0131 (CORRECTED - the original claim was WRONG): The subagent token metric does not track work - it cannot be used for calibration as-is

> **Status:** Open
> **Severity:** Low
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## CORRECTION - the metric DOES track work

Filed at N=3 claiming the token figure "does not track work". **That was wrong, and the error was
mine: the sample was too narrow to show the signal.** The first three units all sat in an 11-15
tool-use band, which made tokens look flat (42.7k-46.8k). Two larger units then broke it open:

| unit   | tools | actual tokens | estimate | over by |
| ---    | ---   | ---           | ---      | ---     |
| CR0250 | 11    | 46,359        | 50,000   | 1.1x    |
| BG0126 | 14    | 46,792        | 245,000  | 5.2x    |
| BG0130 | 15    | 42,687        | 125,000  | 2.9x    |
| CR0249 | 28    | 98,513        | 245,000  | 2.5x    |
| CR0248 | 39    | 84,302        | 310,000  | 3.7x    |

Tokens roughly DOUBLE from the small band (42-47k) to the large one (84-98k). The metric scales
with work volume; it simply carries a large fixed floor (~35-40k of context/setup per subagent)
that dominates a small unit. Wall-clock is the WORSE proxy here (BG0130 ran 189s for fewer tokens
than CR0250's 80s).

**What the data actually says (N=5, still small):** the estimator over-estimates by 2.5x-5.2x on
every unit that touches a complex file, and is near-exact (1.1x) on the one unit with complexity 0.
The `complexity x 5,000` term is the error source; the 50k base is about right for the fixed cost.
The cognitive complexity of the FILE is a poor proxy for the WORK done in it. That is a real
calibration signal - but N=5 is a signal, not a calibration. Keep collecting.

**Severity downgraded High -> Low.** The metric is usable. What remains is the narrower, true point
below: define what the figure counts before trusting absolute values.

## Original summary (retained - it was over-stated)

The token-supplier PoC (CR0258) flows numbers from a subagent's reported usage into telemetry. The mechanism works, but the METRIC is invalid as a per-unit actual. Measured across three real units delivered by subagents: BG0126 (Python fix + lock + test, 14 tool uses, 272s) = 46,792 tokens; CR0250 (two doc edits, 11 tool uses, 80s) = 46,359 tokens; BG0130 (classifier reorder + 7 tests, 15 tool uses, 189s) = 42,687 tokens. Tokens span 42.7k-46.8k - a +/-9% spread - while wall-clock spans 240% (80s to 272s) and the work differs completely in kind. BG0130 used the MOST tool calls and reported the FEWEST tokens. So the reported figure correlates with neither wall-clock, tool-uses, nor the nature of the work: it is dominated by something near-fixed (most likely output-tokens-only, or context/prompt overhead), not total spend. Calibrating estimates against it would fit noise.

## Steps to Reproduce

Run three units of very different size/kind as subagents; record each completion's reported token usage into telemetry. Compare against `wall_time_s` and `tool_uses.` Tokens stay ~42-47k regardless; wall-clock varies 3.4x.

## Proposed Fix

Define the measured quantity before using it. Establish what the harness's reported token figure counts (output only? total? context?). If it is not total spend, either (a) source the actual from a metric that does track work - wall-clock is the obvious candidate and it demonstrably differentiated all three units - or (b) obtain true input+output usage from the API layer. Until then, do NOT recalibrate the S/M/L token bands (CR0257) or the capacity budget (CR0259) against this figure. Blocks the token half of CR0258; the wall-clock half is unaffected.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
